#!/usr/bin/env python3
"""
RTL8852AU WiFi Adapter Dashboard
Flask-based web interface for monitoring and configuring the WiFi adapter.

Usage: sudo python3 dashboard/app.py [--port 8080] [--host 127.0.0.1]

The dashboard binds to loopback by default. All endpoints (including the
HTML root) are protected by HTTP Basic Auth — username is ignored, the
password is the per-user token stored in ~/.config/rtl8852au/dashboard.token
(generated on first run). Pass `--host 0.0.0.0` to expose to the LAN; in
that case the token is the only thing standing between the network and
root-level operations on this host.
"""

import argparse
import glob
import hmac
import json
import os
import re
import secrets
import socket
import subprocess
import threading
import time
from collections import deque
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

# Templates and static assets live next to this file. Flask defaults to
# `templates/` and `static/` relative to the app's import path, which
# matches the layout we ship.
_DASHBOARD_ROOT = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(_DASHBOARD_ROOT / "templates"),
    static_folder=str(_DASHBOARD_ROOT / "static"),
)

DRIVER_NAME = "rtl8852au"
MODULE_NAME = "8852au"

# ── Auth + Host-header hardening ─────────────────────────────────────
# Goal: the dashboard runs as root and exposes endpoints that can change
# WiFi state, reload the kernel module, and run the test suite. Without
# auth, any process on this machine (or — when --host 0.0.0.0 — anyone on
# the LAN, plus drive-by JS via DNS-rebinding) could trigger those.
#
# We use HTTP Basic Auth so the browser handles credential caching for us
# (no JS changes in the embedded UI), and a Host-header whitelist so a
# DNS-rebind attack cannot reach the loopback endpoint from a remote tab.

# Resolve XDG_CONFIG_HOME (sudo keeps the original HOME; if not, fall back
# to /root/.config). The token file is mode 0600 and survives restarts.
def _config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return Path(base) / "rtl8852au"


TOKEN_PATH = _config_dir() / "dashboard.token"
ALLOWED_HOSTS = set()  # populated in __main__ before app.run


def _load_or_create_token():
    """Return the dashboard auth token, generating one on first run."""
    try:
        if TOKEN_PATH.is_file():
            existing = TOKEN_PATH.read_text().strip()
            if existing:
                return existing
    except (IOError, OSError):
        pass
    token = secrets.token_urlsafe(32)
    try:
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(token + "\n")
        TOKEN_PATH.chmod(0o600)
    except (IOError, OSError) as exc:
        print(f"WARNING: could not persist token to {TOKEN_PATH}: {exc}")
        print("         A fresh token will be generated on every restart.")
    return token


AUTH_TOKEN = _load_or_create_token()


@app.before_request
def _enforce_auth_and_host():
    """Reject requests with an unexpected Host header (DNS-rebinding
    defence) or without valid HTTP Basic credentials.

    Exception: the Server-Sent Events stream cannot send a custom
    Authorization header, so /api/stream also accepts the token as a
    ?token=<...> query parameter. The token is the same per-host
    secret as the Basic Auth password, just delivered differently.
    """
    host = (request.host or "").split(":")[0].lower()
    if host not in ALLOWED_HOSTS:
        return Response("forbidden host\n", status=403, mimetype="text/plain")

    if request.method not in ("GET", "HEAD", "OPTIONS"):
        # Basic Auth is ambient: once the browser holds the credentials it
        # attaches them to every request for this origin, including a form
        # that some other site submits here (CSRF). Browsers say where a
        # request came from, so refuse a state-changing one that came from
        # elsewhere. Clients that send neither header (curl) still need the
        # token, so nothing is weakened for them.
        site = request.headers.get("Sec-Fetch-Site")
        origin = request.headers.get("Origin")
        if (site is not None and site not in ("same-origin", "none")) or \
                (origin is not None and origin != request.host_url.rstrip("/")):
            return Response("cross-site request refused\n", status=403,
                            mimetype="text/plain")

    if request.path == "/api/stream":
        qtoken = request.args.get("token") or ""
        if hmac.compare_digest(qtoken, AUTH_TOKEN):
            return None

    auth = request.authorization
    supplied = (auth.password or "") if auth is not None else ""
    if not hmac.compare_digest(supplied, AUTH_TOKEN):
        return Response(
            "authentication required\n",
            status=401,
            mimetype="text/plain",
            headers={"WWW-Authenticate": 'Basic realm="RTL8852AU Dashboard"'},
        )
    return None


@app.after_request
def _security_headers(resp):
    """No framing (clickjacking), no MIME sniffing, no Referer, and no
    <base>, <object> or foreign form targets even if markup slips through.
    script-src is left alone: the UI still uses inline event handlers."""
    h = resp.headers
    h.setdefault("X-Content-Type-Options", "nosniff")
    h.setdefault("X-Frame-Options", "DENY")
    h.setdefault("Referrer-Policy", "no-referrer")
    h.setdefault("Content-Security-Policy",
                 "frame-ancestors 'none'; base-uri 'none'; "
                 "object-src 'none'; form-action 'self'")
    return resp


def _escape_wpa_string(value):
    """Escape a string for use inside a double-quoted wpa_supplicant value.

    Strips newlines (would split into a fresh directive and let an
    attacker inject network blocks or override ctrl_interface). Escapes
    the two characters the wpa_supplicant parser treats specially inside
    a quoted string: backslash and double-quote.
    """
    value = value.replace("\r", "").replace("\n", "")
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return value


def run(cmd, timeout=15):
    """Run a command and return (rc, stdout, stderr).

    Accepts either a list (preferred, executed directly without a shell)
    or a string (legacy path via `shell=True`, kept for the few commands
    that genuinely need pipes / redirects — none in this codebase anymore
    but the path is retained so external callers don't break).

    Using a list eliminates the shell-injection oppervlak completely:
    even if a user-controlled string ends up in argv, the kernel sees it
    as a single argument, not a shell command. Capture_output also lets
    us drop the `2>/dev/null` redirects that used to be sprinkled around.
    """
    use_shell = isinstance(cmd, str)
    try:
        r = subprocess.run(
            cmd,
            shell=use_shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError as exc:
        return -1, "", f"{exc.filename}: not found"


def get_wlan_interface():
    for iface_dir in glob.glob("/sys/class/net/wlan*"):
        iface = os.path.basename(iface_dir)
        driver_link = os.path.join(iface_dir, "device", "driver")
        if os.path.islink(driver_link):
            if DRIVER_NAME in os.readlink(driver_link):
                return iface
    return None


def read_sysfs(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="replace").strip()
        if "\ufffd" in text:
            return None
        return text
    except (IOError, OSError):
        return None


# \u2500\u2500 Metric history \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# Rolling ringbuffer of samples for the trend sparklines on the Overview
# tab. We append one sample per /api/status call; with the default
# 5-second client poll that gives 60 minutes of history (720 samples).
# Capped on memory regardless of polling rate. Read by /api/history.
METRIC_HISTORY = deque(maxlen=720)
_HISTORY_LOCK = threading.Lock()


def _parse_bitrate_mbps(s):
    """Pull the leading float out of an `iw dev <iface> link` bitrate
    string (e.g. '780.0 MBit/s'). Returns None when no match."""
    if not s:
        return None
    m = re.match(r'\s*([0-9.]+)\s*MBit/s', s)
    return float(m.group(1)) if m else None


def _record_sample(payload):
    """Append a single trend sample derived from the /api/status payload."""
    conn = payload.get("connection") or {}
    stats = payload.get("statistics") or {}
    sample = {
        "t": time.time(),
        "signal": conn.get("signal_dbm"),
        "bitrate": _parse_bitrate_mbps(conn.get("tx_bitrate")),
        "tx_bytes": stats.get("tx_bytes", 0),
        "rx_bytes": stats.get("rx_bytes", 0),
        "errors": (stats.get("tx_errors", 0) or 0) + (stats.get("rx_errors", 0) or 0),
    }
    with _HISTORY_LOCK:
        METRIC_HISTORY.append(sample)


# ── API Endpoints ─────────────────────────────────────────────────────

def _collect_status(iface):
    """Build the status dict for a known interface — shared by
    /api/status and the SSE stream so both views see the same shape."""
    dev_path = os.path.realpath(f"/sys/class/net/{iface}/device")
    usb_parent = os.path.dirname(dev_path)

    # Basic info
    mac = read_sysfs(f"/sys/class/net/{iface}/address") or "unknown"
    operstate = read_sysfs(f"/sys/class/net/{iface}/operstate") or "unknown"
    mtu = read_sysfs(f"/sys/class/net/{iface}/mtu") or "unknown"
    tx_bytes = read_sysfs(f"/sys/class/net/{iface}/statistics/tx_bytes") or "0"
    rx_bytes = read_sysfs(f"/sys/class/net/{iface}/statistics/rx_bytes") or "0"
    tx_packets = read_sysfs(f"/sys/class/net/{iface}/statistics/tx_packets") or "0"
    rx_packets = read_sysfs(f"/sys/class/net/{iface}/statistics/rx_packets") or "0"
    tx_errors = read_sysfs(f"/sys/class/net/{iface}/statistics/tx_errors") or "0"
    rx_errors = read_sysfs(f"/sys/class/net/{iface}/statistics/rx_errors") or "0"
    tx_dropped = read_sysfs(f"/sys/class/net/{iface}/statistics/tx_dropped") or "0"
    rx_dropped = read_sysfs(f"/sys/class/net/{iface}/statistics/rx_dropped") or "0"
    speed = read_sysfs(os.path.join(usb_parent, "speed")) or "unknown"

    # USB info
    vendor = read_sysfs(os.path.join(usb_parent, "idVendor")) or "unknown"
    product = read_sysfs(os.path.join(usb_parent, "idProduct")) or "unknown"
    manufacturer = read_sysfs(os.path.join(usb_parent, "manufacturer")) or "unknown"
    product_name = read_sysfs(os.path.join(usb_parent, "product")) or "unknown"

    # Module info
    srcversion = read_sysfs(f"/sys/module/{MODULE_NAME}/srcversion") or "unknown"

    # Connection info from iw
    rc, iw_out, _ = run(["iw", "dev", iface, "link"])
    connected_ssid = None
    signal_dbm = None
    freq = None
    bitrate = None
    if rc == 0 and "Connected" in iw_out:
        m = re.search(r'SSID: (.+)', iw_out)
        if m:
            connected_ssid = m.group(1)
        m = re.search(r'signal: (-?\d+) dBm', iw_out)
        if m:
            signal_dbm = int(m.group(1))
        m = re.search(r'freq: (\d+)', iw_out)
        if m:
            freq = int(m.group(1))
        m = re.search(r'tx bitrate: (.+)', iw_out)
        if m:
            bitrate = m.group(1)

    # IP address
    rc, ip_out, _ = run(["ip", "-4", "addr", "show", iface])
    ip_addr = None
    if rc == 0:
        m = re.search(r'inet (\S+)', ip_out)
        if m:
            ip_addr = m.group(1)

    payload = {
        "driver_loaded": True,
        "interface": iface,
        "mac_address": mac,
        "operstate": operstate,
        "mtu": mtu,
        "ip_address": ip_addr,
        "usb_speed_mbps": speed,
        "usb_vendor": vendor,
        "usb_product": product,
        "usb_manufacturer": manufacturer,
        "usb_product_name": product_name,
        "module_srcversion": srcversion,
        "connection": {
            "ssid": connected_ssid,
            "signal_dbm": signal_dbm,
            "frequency_mhz": freq,
            "tx_bitrate": bitrate,
        },
        "statistics": {
            "tx_bytes": int(tx_bytes),
            "rx_bytes": int(rx_bytes),
            "tx_packets": int(tx_packets),
            "rx_packets": int(rx_packets),
            "tx_errors": int(tx_errors),
            "rx_errors": int(rx_errors),
            "tx_dropped": int(tx_dropped),
            "rx_dropped": int(rx_dropped),
        }
    }
    return payload


@app.route("/api/status")
def api_status():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found", "driver_loaded": False})
    payload = _collect_status(iface)
    _record_sample(payload)
    return jsonify(payload)


@app.route("/api/stream")
def api_stream():
    """Server-Sent Events stream — pushes a fresh status payload every
    ~2 seconds. Replaces the client's setInterval(refreshStatus, 5000)
    polling loop. EventSource cannot send a custom Authorization
    header, so this endpoint accepts the token via ?token=<...>
    (see _enforce_auth_and_host)."""
    def event_stream():
        last_payload = None
        while True:
            iface = get_wlan_interface()
            if iface:
                payload = _collect_status(iface)
                _record_sample(payload)
            else:
                payload = {"error": "No interface found", "driver_loaded": False}
            serialised = json.dumps(payload)
            if serialised != last_payload:
                yield f"event: status\ndata: {serialised}\n\n"
                last_payload = serialised
            else:
                # Keep-alive comment so proxies / browsers don't drop the connection.
                yield ": keepalive\n\n"
            time.sleep(2)

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return Response(event_stream(), mimetype="text/event-stream", headers=headers)


@app.route("/api/history")
def api_history():
    """Return the rolling buffer of trend samples (newest last)."""
    with _HISTORY_LOCK:
        return jsonify({"samples": list(METRIC_HISTORY)})


# Cached scan result reused by /api/spectrum so users don't have to wait
# four extra seconds for an iw-scan-trigger when they switch sub-views.
_LAST_SCAN = {"t": 0.0, "networks": []}

# Monitor-mode state.
#   _MONITOR_CAPTURE  — Popen handle for the running tcpdump, or None.
#   _MONITOR_FRAMES   — rolling buffer of (timestamp, raw line) tuples.
#   _MONITOR_PCAP     — path to the rotating pcap file used by the
#                        export endpoint. Written to /tmp so it's
#                        tmpfs and disappears on reboot.
_MONITOR_LOCK = threading.Lock()
_MONITOR_CAPTURE = None
_MONITOR_FRAMES = deque(maxlen=200)
_MONITOR_PCAP = "/tmp/rtw_monitor.pcap"


def _freq_to_channel(freq):
    if freq is None:
        return None
    if 2412 <= freq <= 2484:
        return 14 if freq == 2484 else (freq - 2407) // 5
    if 5170 <= freq <= 5825:
        return (freq - 5000) // 5
    if 5955 <= freq <= 7115:    # 6 GHz, not supported by RTL8852AU but harmless
        return (freq - 5950) // 5
    return None


def _aggregate_spectrum(networks):
    """Group scan results by channel and return per-band summaries."""
    bands = {"2.4": [], "5": []}
    by_channel = {}
    for n in networks:
        freq = n.get("frequency")
        if freq is None:
            continue
        ch = n.get("channel") or _freq_to_channel(freq)
        if ch is None:
            continue
        band = "2.4" if freq < 3000 else "5"
        slot = by_channel.setdefault((band, ch), {
            "band": band, "channel": ch, "freq": freq,
            "ap_count": 0, "max_signal": None, "ssids": [],
        })
        slot["ap_count"] += 1
        sig = n.get("signal")
        if sig is not None and (slot["max_signal"] is None or sig > slot["max_signal"]):
            slot["max_signal"] = sig
        ssid = n.get("ssid") or ""
        if ssid and ssid not in slot["ssids"]:
            slot["ssids"].append(ssid)
    for slot in by_channel.values():
        bands[slot["band"]].append(slot)
    for v in bands.values():
        v.sort(key=lambda s: s["channel"])
    return bands


@app.route("/api/spectrum")
def api_spectrum():
    """Return the latest scan grouped by channel + band. Re-runs a fresh
    scan only when the cached result is older than 30 s."""
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404

    age = time.time() - _LAST_SCAN["t"]
    networks = _LAST_SCAN["networks"]
    if age > 30 or not networks:
        run(["ip", "link", "set", iface, "up"])
        run(["iw", "dev", iface, "scan", "trigger"])
        time.sleep(3)
        rc, out, _ = run(["iw", "dev", iface, "scan", "dump"], timeout=20)
        if rc == 0:
            networks = _parse_scan(out)
            _LAST_SCAN["networks"] = networks
            _LAST_SCAN["t"] = time.time()

    return jsonify({
        "bands": _aggregate_spectrum(networks),
        "total_aps": len(networks),
        "scanned_at": _LAST_SCAN["t"],
    })


# ── Monitor mode ───────────────────────────────────────────────────────

# 2.4 GHz channels (1-13 worldwide, 14 only legal in JP) and the common
# 5 GHz channels supported by the RTL8852AU. The driver / regulatory
# domain may refuse some of these; the front-end only offers them as a
# starting list and the user can type a free-form value.
MONITOR_CHANNELS_24 = list(range(1, 15))
MONITOR_CHANNELS_5 = [36, 40, 44, 48, 52, 56, 60, 64,
                      100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144,
                      149, 153, 157, 161, 165]


def _monitor_iface_info(iface):
    """Return (type, channel) for the interface; both may be None."""
    rc, info, _ = run(["iw", "dev", iface, "info"])
    if rc != 0:
        return None, None
    iface_type = None
    channel = None
    m = re.search(r'type (\S+)', info)
    if m:
        iface_type = m.group(1)
    m = re.search(r'channel (\d+)', info)
    if m:
        channel = int(m.group(1))
    return iface_type, channel


@app.route("/api/monitor/status")
def api_monitor_status():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404
    iface_type, channel = _monitor_iface_info(iface)
    with _MONITOR_LOCK:
        capturing = _MONITOR_CAPTURE is not None and _MONITOR_CAPTURE.poll() is None
        frame_count = len(_MONITOR_FRAMES)
    return jsonify({
        "interface": iface,
        "type": iface_type,
        "channel": channel,
        "capturing": capturing,
        "frame_count": frame_count,
        "channels_24": MONITOR_CHANNELS_24,
        "channels_5": MONITOR_CHANNELS_5,
        "pcap_available": os.path.isfile(_MONITOR_PCAP),
    })


@app.route("/api/monitor/enable", methods=["POST"])
def api_monitor_enable():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404
    data = request.get_json(silent=True) or {}
    channel = data.get("channel")

    run(["ip", "link", "set", iface, "down"])
    rc, _, err = run(["iw", "dev", iface, "set", "type", "monitor"])
    run(["ip", "link", "set", iface, "up"])
    if rc != 0:
        return jsonify({"error": "Failed to enter monitor mode",
                        "hint": "Stop NetworkManager / wpa_supplicant for this "
                                "interface first.", "details": err}), 500

    if channel is not None:
        try:
            run(["iw", "dev", iface, "set", "channel", str(int(channel))])
        except (ValueError, TypeError):
            pass

    iface_type, ch = _monitor_iface_info(iface)
    return jsonify({"success": True, "type": iface_type, "channel": ch})


@app.route("/api/monitor/disable", methods=["POST"])
def api_monitor_disable():
    global _MONITOR_CAPTURE
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404

    with _MONITOR_LOCK:
        if _MONITOR_CAPTURE is not None:
            try:
                _MONITOR_CAPTURE.terminate()
                _MONITOR_CAPTURE.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    _MONITOR_CAPTURE.kill()
                except OSError:
                    pass
            _MONITOR_CAPTURE = None

    run(["ip", "link", "set", iface, "down"])
    rc, _, err = run(["iw", "dev", iface, "set", "type", "managed"])
    run(["ip", "link", "set", iface, "up"])
    if rc != 0:
        return jsonify({"error": "Failed to leave monitor mode",
                        "details": err}), 500
    return jsonify({"success": True})


@app.route("/api/monitor/channel", methods=["POST"])
def api_monitor_channel():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404
    data = request.get_json(silent=True) or {}
    try:
        ch_int = int(data.get("channel"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid channel"}), 400
    if not (1 <= ch_int <= 200):
        return jsonify({"error": "Channel out of range"}), 400
    rc, _, err = run(["iw", "dev", iface, "set", "channel", str(ch_int)])
    if rc != 0:
        return jsonify({"error": err or "Channel change rejected"}), 500
    return jsonify({"success": True, "channel": ch_int})


def _parse_frame_line(line):
    """Pull a handful of useful fields out of a tcpdump line for the
    monitor-mode table. tcpdump's text output is loose, so we just look
    for the patterns we care about and fall back to the raw line."""
    info = {"raw": line.strip(), "t": time.time()}
    m = re.search(r'\b(?:Beacon|Probe Request|Probe Response|Authentication|'
                  r'Association Request|Association Response|Deauthentication|'
                  r'Disassociation|ACK|RTS|CTS|Data|QoS Data)\b', line)
    if m:
        info["type"] = m.group(0)
    m = re.search(r'SA:([0-9a-f:]{17})', line)
    if m:
        info["src"] = m.group(1)
    m = re.search(r'DA:([0-9a-f:]{17})', line)
    if m:
        info["dst"] = m.group(1)
    m = re.search(r'\(([^)]+)\)', line)
    if m and "type" in info and info["type"] in ("Beacon", "Probe Request", "Probe Response"):
        info["ssid"] = m.group(1)
    m = re.search(r'(-?\d+)dBm', line)
    if m:
        info["rssi"] = int(m.group(1))
    return info


def _capture_reader(proc):
    """Background thread: pump tcpdump lines into the rolling buffer."""
    try:
        for line in proc.stdout:
            if not line:
                continue
            with _MONITOR_LOCK:
                _MONITOR_FRAMES.append(_parse_frame_line(line))
    except Exception:
        pass


@app.route("/api/monitor/capture/start", methods=["POST"])
def api_monitor_capture_start():
    global _MONITOR_CAPTURE
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404
    iface_type, _ = _monitor_iface_info(iface)
    if iface_type != "monitor":
        return jsonify({"error": "Interface is not in monitor mode"}), 400

    with _MONITOR_LOCK:
        if _MONITOR_CAPTURE is not None and _MONITOR_CAPTURE.poll() is None:
            return jsonify({"error": "Capture already running"}), 400
        _MONITOR_FRAMES.clear()

    # Two parallel tcpdumps:
    #   - one writes a pcap to disk for the user to export later
    #   - one prints text lines we parse for the live frame table
    # Spawning a single tcpdump with both `-w` and stdout-text isn't
    # supported, so we just run the disk-writer separately. The text
    # capture is what backs the buffer.
    try:
        subprocess.Popen(
            ["tcpdump", "-i", iface, "-n", "-U", "-w", _MONITOR_PCAP, "-G", "0"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return jsonify({"error": "tcpdump not installed"}), 500

    try:
        proc = subprocess.Popen(
            ["tcpdump", "-i", iface, "-n", "-e", "-l", "-Q", "in"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1,
        )
    except FileNotFoundError:
        return jsonify({"error": "tcpdump not installed"}), 500

    threading.Thread(target=_capture_reader, args=(proc,), daemon=True).start()
    with _MONITOR_LOCK:
        _MONITOR_CAPTURE = proc
    return jsonify({"success": True})


@app.route("/api/monitor/capture/stop", methods=["POST"])
def api_monitor_capture_stop():
    global _MONITOR_CAPTURE
    # Also stop the disk-writer tcpdump.
    run(["pkill", "-f", f"tcpdump.*-w {_MONITOR_PCAP}"])
    with _MONITOR_LOCK:
        if _MONITOR_CAPTURE is not None:
            try:
                _MONITOR_CAPTURE.terminate()
                _MONITOR_CAPTURE.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    _MONITOR_CAPTURE.kill()
                except OSError:
                    pass
        _MONITOR_CAPTURE = None
    return jsonify({"success": True})


@app.route("/api/monitor/frames")
def api_monitor_frames():
    with _MONITOR_LOCK:
        return jsonify({"frames": list(_MONITOR_FRAMES),
                        "count": len(_MONITOR_FRAMES)})


@app.route("/api/monitor/pcap")
def api_monitor_pcap():
    """Stream the saved pcap so the user can open it in Wireshark."""
    from flask import send_file
    if not os.path.isfile(_MONITOR_PCAP):
        return jsonify({"error": "No capture file available"}), 404
    return send_file(_MONITOR_PCAP, as_attachment=True,
                     download_name="rtw_monitor.pcap",
                     mimetype="application/vnd.tcpdump.pcap")


def _parse_scan(out):
    """Parse `iw scan dump` output into the same shape the /api/scan
    endpoint emits. Extracted so /api/spectrum can reuse the parser."""
    networks = []
    current = None
    for line in out.split('\n'):
        line = line.strip()
        m = re.match(r'BSS ([0-9a-f:]+)', line)
        if m:
            if current:
                networks.append(current)
            current = {"bssid": m.group(1), "ssid": "", "signal": None,
                       "frequency": None, "channel": None, "security": "Open"}
        if current is None:
            continue
        if line.startswith("SSID:"):
            current["ssid"] = line[6:].strip()
        elif line.startswith("signal:"):
            m2 = re.search(r'(-?\d+\.?\d*)', line)
            if m2:
                current["signal"] = float(m2.group(1))
        elif line.startswith("freq:"):
            m2 = re.search(r'(\d+)', line)
            if m2:
                current["frequency"] = int(m2.group(1))
        elif "WPA" in line or "RSN" in line:
            current["security"] = "WPA2/WPA3" if "RSN" in line else "WPA"
        elif line.startswith("DS Parameter set: channel"):
            m2 = re.search(r'channel (\d+)', line)
            if m2:
                current["channel"] = int(m2.group(1))
    if current:
        networks.append(current)
    return networks


@app.route("/api/scan")
def api_scan():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404

    run(["ip", "link", "set", iface, "up"])
    run(["iw", "dev", iface, "scan", "trigger"])
    time.sleep(4)
    rc, out, err = run(["iw", "dev", iface, "scan", "dump"], timeout=20)
    if rc != 0:
        return jsonify({"error": f"Scan failed: {err}"}), 500

    networks = []
    current = None
    for line in out.split('\n'):
        line = line.strip()
        m = re.match(r'BSS ([0-9a-f:]+)', line)
        if m:
            if current:
                networks.append(current)
            current = {"bssid": m.group(1), "ssid": "", "signal": None,
                       "frequency": None, "channel": None, "security": "Open"}
        if current is None:
            continue
        if line.startswith("SSID:"):
            current["ssid"] = line[6:].strip()
        elif line.startswith("signal:"):
            m2 = re.search(r'(-?\d+\.?\d*)', line)
            if m2:
                current["signal"] = float(m2.group(1))
        elif line.startswith("freq:"):
            m2 = re.search(r'(\d+)', line)
            if m2:
                current["frequency"] = int(m2.group(1))
        elif "WPA" in line or "RSN" in line:
            current["security"] = "WPA2/WPA3" if "RSN" in line else "WPA"
        elif line.startswith("DS Parameter set: channel"):
            m2 = re.search(r'channel (\d+)', line)
            if m2:
                current["channel"] = int(m2.group(1))
    if current:
        networks.append(current)

    # Sort by signal strength
    networks.sort(key=lambda n: n["signal"] if n["signal"] is not None else -999, reverse=True)
    return jsonify({"networks": networks, "count": len(networks)})


@app.route("/api/connect", methods=["POST"])
def api_connect():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404

    data = request.get_json(silent=True) or {}
    ssid = data.get("ssid", "") or ""
    password = data.get("password", "") or ""

    # SSID: IEEE 802.11 limits to 32 bytes. Reject newlines/embedded NUL.
    if not ssid or len(ssid.encode("utf-8")) > 32:
        return jsonify({"error": "SSID must be 1-32 bytes UTF-8"}), 400
    # WPA passphrase spec: 8-63 ASCII chars (or 64 hex). Empty = open network.
    if password and not (8 <= len(password) <= 63):
        return jsonify({"error": "WPA passphrase must be 8-63 characters"}), 400

    # Escape both for the quoted wpa_supplicant string literal. Without
    # this, an SSID like  evil"\nnetwork={ssid="x  would inject extra
    # network blocks (rogue-AP redirect, ctrl_interface override).
    ssid_esc = _escape_wpa_string(ssid)
    password_esc = _escape_wpa_string(password)

    conf = f'network={{\n    ssid="{ssid_esc}"\n'
    if password_esc:
        conf += f'    psk="{password_esc}"\n'
    else:
        conf += '    key_mgmt=NONE\n'
    conf += '}\n'

    conf_path = f"/run/wpa_{iface}.conf"
    fd = os.open(conf_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(f'ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1\n\n{conf}')

    run(["killall", "-9", "wpa_supplicant"])
    time.sleep(1)
    run(["ip", "link", "set", iface, "up"])

    # Discard stderr from wpa_supplicant — it can echo the passphrase on
    # failure paths (e.g. "Line N: invalid PSK 'mypass123'").
    rc, _, _ = run(["wpa_supplicant", "-B", "-i", iface, "-c", conf_path], timeout=10)
    if rc != 0:
        return jsonify({"error": "wpa_supplicant failed to start"}), 500

    run(["dhclient", "-r", iface])
    rc, _, _ = run(["dhclient", iface], timeout=30)
    if rc != 0:
        return jsonify({"warning": "Connected but DHCP failed", "ssid": ssid})

    time.sleep(2)
    return jsonify({"success": True, "ssid": ssid})


@app.route("/api/disconnect", methods=["POST"])
def api_disconnect():
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404

    run(["iw", "dev", iface, "disconnect"])
    run(["killall", "wpa_supplicant"])
    run(["dhclient", "-r", iface])
    return jsonify({"success": True})


@app.route("/api/driver")
def api_driver():
    rc, modinfo, _ = run(["modinfo", MODULE_NAME])
    info = {}
    if rc == 0:
        for line in modinfo.split('\n'):
            m = re.match(r'(\w+):\s+(.+)', line)
            if m:
                key = m.group(1)
                if key not in info:
                    info[key] = m.group(2)
                elif key == "alias":
                    if isinstance(info[key], list):
                        info[key].append(m.group(2))
                    else:
                        info[key] = [info[key], m.group(2)]

    srcversion = read_sysfs(f"/sys/module/{MODULE_NAME}/srcversion") or "unknown"
    _, kver, _ = run("uname -r")

    return jsonify({
        "module_name": MODULE_NAME,
        "driver_name": DRIVER_NAME,
        "kernel_version": kver,
        "srcversion": srcversion,
        "modinfo": info
    })


@app.route("/api/ifconfig", methods=["POST"])
def api_ifconfig():
    """Change interface settings (MTU, power save, etc.)."""
    iface = get_wlan_interface()
    if not iface:
        return jsonify({"error": "No interface found"}), 404

    data = request.get_json()
    results = []

    if "mtu" in data:
        mtu = int(data["mtu"])
        if 576 <= mtu <= 9000:
            rc, _, err = run(["ip", "link", "set", iface, "mtu", str(mtu)])
            results.append({"mtu": "ok" if rc == 0 else err})

    if "txpower" in data:
        txp = int(data["txpower"])
        if 0 <= txp <= 30:
            rc, _, err = run(["iw", "dev", iface, "set", "txpower", "fixed", str(txp * 100)])
            results.append({"txpower": "ok" if rc == 0 else err})

    if "power_save" in data:
        ps = "on" if data["power_save"] else "off"
        rc, _, err = run(["iw", "dev", iface, "set", "power_save", ps])
        results.append({"power_save": "ok" if rc == 0 else err})

    return jsonify({"results": results})


@app.route("/api/tests/run", methods=["POST"])
def api_run_tests():
    """Run the driver test suite and return results."""
    test_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "tests", "test_driver.py")
    if not os.path.exists(test_script):
        return jsonify({"error": "Test script not found"}), 404

    rc, out, err = run(["python3", test_script], timeout=120)
    report_path = os.path.join(os.path.dirname(test_script), "test_report.json")
    report = None
    if os.path.exists(report_path):
        with open(report_path) as f:
            report = json.load(f)

    return jsonify({
        "exit_code": rc,
        "output": out,
        "stderr": err,
        "report": report
    })


# ── Advanced Configuration ───────────────────────────────────────────

MODPROBE_CONF = "/etc/modprobe.d/8852au.conf"

# What a module-parameter value written to MODPROBE_CONF may consist of.
# modprobe parses that file as root, line by line: whitespace would end the
# value and a newline would start a new directive -- `install 8852au <cmd>`
# runs <cmd> as root on the next load.
_MODPROBE_VALUE_RE = re.compile(r"[A-Za-z0-9_.+-]+")

# Whitelist of module parameters exposed in the Advanced tab.
# Each entry: param_name -> {type, options (for select), min/max (for number)}
ADVANCED_PARAMS = {
    # Draadloze Modus
    "rtw_ht_enable":      {"vtype": "select", "opts": {"0": "Uit", "1": "Aan"}},
    "rtw_vht_enable":     {"vtype": "select", "opts": {"0": "Uit", "1": "Aan", "2": "Auto"}},
    "rtw_he_enable":      {"vtype": "select", "opts": {"0": "Uit", "1": "Aan", "2": "Auto"}},
    "rtw_wireless_mode":  {"vtype": "number", "min": 0, "max": 255},
    "rtw_band_type":      {"vtype": "select", "opts": {"1": "Alleen 2.4 GHz", "2": "Alleen 5 GHz", "3": "Dual-band (2.4 + 5 GHz)"}},
    # Kanaal & Bandbreedte
    "rtw_channel":        {"vtype": "number", "min": 0, "max": 165},
    "rtw_bw_mode":        {"vtype": "number", "min": 0, "max": 255},
    "rtw_channel_plan":   {"vtype": "number", "min": 0, "max": 255},
    "rtw_country_code":   {"vtype": "text", "pattern": r"[A-Za-z0-9]{2}"},
    # Energiebeheer
    "rtw_power_mgnt":     {"vtype": "select", "opts": {"0": "Uit", "1": "Minimaal", "2": "Maximaal"}},
    "rtw_ips_mode":       {"vtype": "select", "opts": {"0": "Geen", "1": "Normaal", "2": "Level 2"}},
    "rtw_lps_level":      {"vtype": "select", "opts": {"0": "Normaal", "1": "Clock Gating", "2": "Power Gating"}},
    # Prestaties
    "rtw_ampdu_enable":   {"vtype": "select", "opts": {"0": "Uit", "1": "Aan"}},
    "rtw_en_napi":        {"vtype": "select", "opts": {"0": "Uit", "1": "Aan"}},
    "rtw_en_gro":         {"vtype": "select", "opts": {"0": "Uit", "1": "Aan"}},
    "rtw_switch_usb_mode":{"vtype": "select", "opts": {"0": "Geen wijziging", "1": "USB 3.0", "2": "USB 2.0"}},
    "rtw_wmm_enable":     {"vtype": "select", "opts": {"0": "Uit", "1": "Aan"}},
    # Antenne & Beamforming
    "rtw_beamform_cap":   {"vtype": "number", "min": 0, "max": 255},
    "rtw_dyn_txbf":       {"vtype": "select", "opts": {"0": "Uit", "1": "Aan"}},
    "rtw_tx_nss":         {"vtype": "select", "opts": {"0": "Auto", "1": "1 Stream", "2": "2 Streams"}},
    "rtw_rx_nss":         {"vtype": "select", "opts": {"0": "Auto", "1": "1 Stream", "2": "2 Streams"}},
    "rtw_antdiv_cfg":     {"vtype": "select", "opts": {"0": "Uit", "1": "Aan", "2": "Auto (Efuse)"}},
    "rtw_rx_stbc":        {"vtype": "select", "opts": {"0": "Uit", "1": "Alleen 2.4 GHz", "2": "Alleen 5 GHz", "3": "Beide banden"}},
    # Roaming & Verbinding
    "rtw_max_roaming_times": {"vtype": "number", "min": 0, "max": 8},
    "rtw_btcoex_enable":  {"vtype": "select", "opts": {"0": "Uit", "1": "Aan", "2": "Auto (Efuse)"}},
    # Debug
    "rtw_drv_log_level":  {"vtype": "select", "opts": {"0": "Geen", "1": "Error", "2": "Warning", "3": "Notice", "4": "Info", "5": "Debug"}},
    "rtw_tx_pwr_by_rate": {"vtype": "select", "opts": {"0": "Uit", "1": "Aan", "2": "Auto (Efuse)"}},
    "rtw_tx_pwr_lmt_enable": {"vtype": "select", "opts": {"0": "Uit", "1": "Aan", "2": "Auto (Efuse)"}},
}


def read_module_param(name):
    """Read a single module parameter from sysfs."""
    val = read_sysfs(f"/sys/module/{MODULE_NAME}/parameters/{name}")
    if val is None:
        return None
    try:
        return int(val)
    except ValueError:
        return val


def read_modprobe_conf():
    """Parse saved settings from /etc/modprobe.d/8852au.conf."""
    pending = {}
    if os.path.exists(MODPROBE_CONF):
        try:
            with open(MODPROBE_CONF) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"options {MODULE_NAME}"):
                        parts = line.split()[2:]
                        for part in parts:
                            if "=" in part:
                                k, v = part.split("=", 1)
                                if k in ADVANCED_PARAMS:
                                    pending[k] = v
        except (IOError, OSError):
            pass
    return pending


def write_modprobe_conf(params):
    """Write module parameters to /etc/modprobe.d/8852au.conf (merge)."""
    other_lines = []
    existing = {}
    if os.path.exists(MODPROBE_CONF):
        try:
            with open(MODPROBE_CONF) as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith(f"options {MODULE_NAME}"):
                        for part in stripped.split()[2:]:
                            if "=" in part:
                                k, v = part.split("=", 1)
                                existing[k] = v
                    elif not stripped.startswith("# RTL8852AU") and not stripped.startswith("# Automatisch"):
                        other_lines.append(line)
        except (IOError, OSError):
            pass

    existing.update(params)
    # Second line of defence behind api_advanced_save's validation: never
    # write a value modprobe could read as more than a single token.
    valid = {k: v for k, v in existing.items()
             if k in ADVANCED_PARAMS and _MODPROBE_VALUE_RE.fullmatch(str(v))}

    with open(MODPROBE_CONF, "w") as f:
        f.write("# RTL8852AU advanced settings - managed by dashboard\n")
        f.write("# Automatisch gegenereerd - niet handmatig bewerken\n")
        if valid:
            opts = " ".join(f"{k}={v}" for k, v in sorted(valid.items()))
            f.write(f"options {MODULE_NAME} {opts}\n")
        for line in other_lines:
            f.write(line)


@app.route("/api/advanced")
def api_advanced():
    """Read all advanced parameters: current from sysfs, pending from modprobe.d."""
    params = {}
    for name in ADVANCED_PARAMS:
        current = read_module_param(name)
        params[name] = {"current": current}

    pending = read_modprobe_conf()
    has_pending = False
    for name, val in pending.items():
        if name in params:
            try:
                pval = int(val)
            except ValueError:
                pval = val
            params[name]["pending"] = pval
            if params[name]["current"] is not None and str(params[name]["current"]) != str(pval):
                has_pending = True

    return jsonify({
        "parameters": params,
        "has_pending_changes": has_pending,
        "modprobe_conf_exists": os.path.exists(MODPROBE_CONF),
    })


@app.route("/api/advanced", methods=["POST"])
def api_advanced_save():
    """Save advanced settings. Live settings applied immediately, module settings persisted."""
    data = request.get_json()
    results = []
    iface = get_wlan_interface()

    # Apply live settings via iw
    live = data.get("live", {})
    if iface and "txpower" in live:
        txp = int(live["txpower"])
        if 0 <= txp <= 30:
            rc, _, err = run(["iw", "dev", iface, "set", "txpower", "fixed", str(txp * 100)])
            results.append({"txpower": "ok" if rc == 0 else err})
    if iface and "power_save" in live:
        ps = "on" if live["power_save"] else "off"
        rc, _, err = run(["iw", "dev", iface, "set", "power_save", ps])
        results.append({"power_save": "ok" if rc == 0 else err})

    # Persist module settings
    module = data.get("module", {})
    reload_needed = False
    if module:
        safe = {}
        for k, v in module.items():
            if k not in ADVANCED_PARAMS:
                continue
            spec = ADVANCED_PARAMS[k]
            sv = str(v)
            if spec["vtype"] == "number":
                try:
                    iv = int(sv)
                except ValueError:
                    continue
                if "min" in spec and iv < spec["min"]:
                    continue
                if "max" in spec and iv > spec["max"]:
                    continue
                # int() tolerates surrounding whitespace, newlines included,
                # so store the canonical form rather than what was sent.
                sv = str(iv)
            elif spec["vtype"] == "select":
                if sv not in spec["opts"]:
                    continue
            elif spec["vtype"] == "text":
                # Free text lands verbatim in /etc/modprobe.d, which modprobe
                # reads as root: a newline would start an `install` directive
                # that runs a command on the next module load. Each text
                # parameter declares the exact shape it accepts; one that
                # declares none accepts nothing.
                pattern = spec.get("pattern")
                if not pattern or not re.fullmatch(pattern, sv):
                    continue
            else:
                continue
            safe[k] = sv
        if safe:
            try:
                write_modprobe_conf(safe)
                reload_needed = True
                results.append({"module": "ok", "saved": list(safe.keys())})
            except (IOError, OSError) as e:
                results.append({"module": f"error: {e}"})

    return jsonify({"results": results, "reload_needed": reload_needed})


@app.route("/api/advanced/reload", methods=["POST"])
def api_advanced_reload():
    """Safely reload the kernel module to apply new parameters."""
    iface = get_wlan_interface()
    warnings = []

    if iface:
        rc, link_out, _ = run(["iw", "dev", iface, "link"])
        if rc == 0 and "Connected" in link_out:
            warnings.append("Adapter was verbonden met een netwerk. Verbinding is verbroken.")
        run(["ip", "link", "set", iface, "down"])
        run(["killall", "wpa_supplicant"])
        run(["dhclient", "-r", iface])
        time.sleep(1)

    rc, _, err = run(["modprobe", "-r", MODULE_NAME], timeout=10)
    if rc != 0:
        rc, _, err = run(["rmmod", MODULE_NAME], timeout=10)
        if rc != 0:
            return jsonify({
                "success": False,
                "error": f"Kan module niet verwijderen: {err}",
                "hint": "Sluit alle programma's die de adapter gebruiken en probeer opnieuw.",
            }), 500

    time.sleep(2)

    rc, _, err = run(["modprobe", MODULE_NAME], timeout=15)
    if rc != 0:
        return jsonify({"success": False, "error": f"Kan module niet laden: {err}"}), 500

    new_iface = None
    for _ in range(10):
        time.sleep(1)
        new_iface = get_wlan_interface()
        if new_iface:
            break

    if not new_iface:
        return jsonify({
            "success": True,
            "warning": "Module geladen maar interface nog niet beschikbaar.",
            "warnings": warnings,
        })

    run(["ip", "link", "set", new_iface, "up"])
    return jsonify({
        "success": True,
        "interface": new_iface,
        "warnings": warnings,
        "message": "Module succesvol herladen met nieuwe instellingen.",
    })


# ── HTML Dashboard ────────────────────────────────────────────────────



def _static_version():
    """Cheap cache-bust: append the highest mtime of style.css / app.js
    as a query parameter on the <link> and <script> tags. Browsers see
    a new URL whenever either asset is updated and skip the cached
    copy."""
    paths = [_DASHBOARD_ROOT / "static" / "style.css",
             _DASHBOARD_ROOT / "static" / "app.js"]
    try:
        return int(max(p.stat().st_mtime for p in paths if p.exists()))
    except (OSError, ValueError):
        return 0


@app.route("/")
def index():
    # The dashboard markup lives in templates/index.html and pulls its
    # CSS / JS from static/. The auth-token meta tag plus an mtime-based
    # cache-bust are the only Jinja2 substitutions; the JS file has
    # plenty of `${…}` template literals that we deliberately keep out
    # of the template engine's scope.
    return render_template(
        "index.html",
        auth_token=AUTH_TOKEN,
        static_version=_static_version(),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTL8852AU WiFi Dashboard")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Bind address (default: 127.0.0.1, loopback only). "
             "Pass 0.0.0.0 to expose to the LAN — the auth token is then "
             "the only thing preventing remote root operations.",
    )
    parser.add_argument(
        "--prod", action="store_true",
        help="Serve via waitress instead of Werkzeug's threaded server. "
             "Production-grade and removes the 'dev server' banner, but "
             "Server-Sent Events (the live status stream) do not work "
             "under waitress — the Overview tab won't auto-update. Use "
             "with a reverse proxy + a gevent/asgi worker if you need "
             "real production behaviour.",
    )
    parser.add_argument(
        "--threads", type=int, default=8,
        help="Worker thread count for waitress (only used with --prod). "
             "Default: 8.",
    )
    args = parser.parse_args()

    if os.geteuid() != 0:
        print("WARNING: Dashboard should run as root for full functionality")

    # Populate the Host-header whitelist used by before_request. Loopback
    # names are always allowed; if the user bound to a non-loopback
    # address we also accept that literal address and the machine's
    # hostname (best-effort).
    ALLOWED_HOSTS.update({"127.0.0.1", "localhost", "::1"})
    if args.host not in ("127.0.0.1", "localhost"):
        ALLOWED_HOSTS.add(args.host.lower())
        try:
            ALLOWED_HOSTS.add(socket.gethostname().lower())
        except OSError:
            pass
        print()
        print("=" * 64)
        print(" WARNING: dashboard is bound to a non-loopback address.")
        print(" Anyone reaching this host on the network needs the token")
        print(" below to interact with /api/* endpoints. Keep it private.")
        print("=" * 64)

    print()
    print(f" RTL8852AU Dashboard:  http://{args.host}:{args.port}/")
    print(f" Auth token         :  {AUTH_TOKEN}")
    print(f" Token file         :  {TOKEN_PATH}")
    print( " Login              :  any username, password = the token above")
    print()

    if args.prod:
        try:
            from waitress import serve
        except ImportError:
            print("ERROR: waitress is not installed. Run "
                  "`pip install --require-hashes -r dashboard/requirements.txt`,",
                  "or omit --prod to use Werkzeug.")
            raise SystemExit(1)
        print(" NOTE: --prod uses waitress; /api/stream (SSE) does not work "
              "under it — the\n       dashboard's live updates will fall back "
              "to manual refresh only.\n")
        serve(app, host=args.host, port=args.port, threads=args.threads,
              ident="rtl8852au-dashboard")
    else:
        # Werkzeug, threaded so the long-lived /api/stream SSE connection
        # doesn't block other endpoints. The "development server" banner
        # is acceptable for a host-local dashboard — see --prod for the
        # waitress path if the banner matters.
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
