# Dashboard user guide

**English** | [Nederlands](dashboard.nl.md)

The dashboard is a small Flask app that exposes the runtime state of
the `8852au` driver and a handful of operational controls — scan,
connect, change interface parameters, run the test suite, edit driver
module parameters. It runs locally on the host, binds to loopback by
default, and is protected by HTTP Basic Auth.

This guide walks through every tab and every control, plus a few
common scenarios.

---

## Table of contents

- [First-time setup](#first-time-setup)
- [Logging in](#logging-in)
- [Tabs](#tabs)
  - [Overview](#overview)
  - [Networks](#networks)
  - [Monitor](#monitor)
  - [Settings](#settings)
  - [Tests](#tests)
  - [Advanced](#advanced)
- [Language switcher](#language-switcher)
- [Common scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)

---

## First-time setup

1. Install dependencies (one-off, hash-locked) into a virtual
   environment. Debian/Kali's system Python is externally-managed
   (PEP 668) and refuses a bare `pip install`:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install --require-hashes -r dashboard/requirements.txt
   ```
2. Start the dashboard with that same interpreter. It needs root to
   call `iw`, `wpa_supplicant`, `modprobe`, and `dhclient`:
   ```bash
   sudo ./.venv/bin/python3 dashboard/app.py
   ```
3. The first run generates an auth token in
   `~/.config/rtl8852au/dashboard.token` (mode `0600`). The token
   survives restarts so your browser keeps remembering the login.
4. Open the printed URL — by default `http://127.0.0.1:8080/`.

## Logging in

Every page and every `/api/*` endpoint is protected by HTTP Basic Auth:

- **Username:** anything (it is ignored)
- **Password:** the token printed at startup and stored in
  `~/.config/rtl8852au/dashboard.token`

The browser caches the credentials per session, so you only see the
prompt the first time you open the dashboard after a restart.

Exposing the dashboard to the LAN (`--host 0.0.0.0`) is supported but
opt-in: the auth token is then the only thing standing between the
network and root-level operations on the host, so treat it like a
password.

---

## Tabs

### Overview

The default landing page. Four cards summarising the live state of
the adapter:

| Card               | What it shows                                                                                  |
|--------------------|------------------------------------------------------------------------------------------------|
| **Adapter Info**   | Interface name, MAC address, IP address, UP/DOWN state, MTU, USB speed and the USB VID:PID    |
| **Connection**     | When associated: SSID, signal strength (dBm + colour bar), frequency, current TX bitrate      |
| **Statistics**     | TX/RX bytes, TX/RX packets, errors and dropped — eight tiles updated every ~2 s via SSE       |
| **Driver Info**    | Module name, driver name, kernel version, `srcversion` hash, vendor version                   |
| **Trends**         | Four sparklines covering the last 60 minutes: signal (dBm), TX bitrate (Mbps), RX throughput (B/s), error rate (Δ per sample). Live value of each metric is shown to the right of the line |

A status badge at the top right shows **Connected** (green) or **Not
connected** (red) at a glance, plus the loaded-driver state.

The dashboard pushes status updates over a long-lived
`/api/stream` Server-Sent Events connection. There is no polling
interval to tune — new data arrives within ~2 s of any change.

### Networks

Three cards. The first visualises the spectrum around you, the
second is the classic AP table, the third is manual-connect.

**Channel usage** (top card)

Two canvases — one for 2.4 GHz (channels 1–14), one for 5 GHz
(channels 36–165). Each channel is a bar:

| Visual cue       | Meaning                                                                |
|------------------|------------------------------------------------------------------------|
| Bar **height**   | Strongest RSSI seen on that channel (-90 to -20 dBm)                   |
| Bar **colour**   | Green for 1 AP, amber for 2, red for 3 or more (likely congestion)     |
| Number above bar | Count of APs on that channel                                           |
| Y-axis labels    | -30 / -50 / -70 / -90 dBm grid lines                                   |

The card auto-refreshes every 30 s while the Networks tab is active,
and the scan is cached for 30 s on the server so switching tabs back
and forth doesn't re-trigger an `iw scan` cycle. A one-line summary
under the title reads `N APs across M channels`.

**Available networks**

| Control / column | Meaning                                                       |
|------------------|---------------------------------------------------------------|
| **Scan**         | Triggers `iw dev <iface> scan`; the table fills with results |
| **SSID**         | Network name; "(Hidden)" if the AP doesn't broadcast it       |
| **BSSID**        | The AP's MAC address                                          |
| **Signal**       | RSSI in dBm with a green/yellow/orange/red bar               |
| **Freq**         | Centre frequency in MHz                                       |
| **Security**     | Detected encryption (WPA2, WPA3, …, or `--` for open)        |
| **Connect**      | One-click prefill of the SSID into the connect form          |

**Connect manually**

- **SSID** — 1–32 bytes, UTF-8 allowed.
- **Password** — leave blank for an open network. Otherwise 8–63
  characters per WPA spec.
- **Connect** — writes a temporary `wpa_supplicant.conf`, kills any
  existing supplicant for this interface, starts a new one, and runs
  `dhclient`. The SSID and passphrase are escaped before being written
  to the conf file, so a `"` in either won't break the parser.
- **Disconnect** — stops `wpa_supplicant`, releases the DHCP lease,
  brings the interface down.

### Monitor

The driver's marquee feature in one tab. Three cards:

**Mode + interface state**

The top card shows the current interface, mode (`managed` /
`monitor` / `unspec`) and channel, plus two buttons:

- **Enable monitor** — runs `ip link down` → `iw dev … set type
  monitor` → `ip link up`. If a channel is selected in the picker
  below, it is set in the same step.
- **Back to managed** — symmetric reverse. Any running frame
  capture is stopped first.

A yellow warning above the buttons reminds you that NetworkManager
and `wpa_supplicant` must let go of the interface before the toggle
can succeed. The dashboard cannot do that for you; run

```bash
sudo nmcli device set wlan1 managed no
sudo systemctl stop wpa_supplicant
```

once, then toggle.

**Channel selection**

A `<select>` grouped 2.4 GHz (channels 1–14) and 5 GHz (36–165). The
current channel is pre-selected. **Apply** runs `iw dev … set
channel N`. If your regulatory domain or the driver rejects the
channel, a toast surfaces the error — the picker doesn't filter
proactively.

**Frame capture**

Spawns two `tcpdump` processes in parallel: one writes a `pcap` to
`/tmp/rtw_monitor.pcap` for the **Download .pcap** button (open it
in Wireshark), the other emits text lines that feed the live frame
table.

| Control               | What it does                                                  |
|-----------------------|---------------------------------------------------------------|
| **Start capture**     | Spawns both tcpdumps. Disabled when not in monitor mode.      |
| **Stop capture**      | Terminates both. The pcap file stays so you can still export. |
| **Download .pcap**    | Saves the file with `Content-Type: application/vnd.tcpdump.pcap` so Wireshark opens it directly. |
| **Filter** (input)    | Case-insensitive substring match against type / SSID / src / dst / raw. |
| Frame table           | Newest first, capped at 200 rows. Time, type, source MAC, destination MAC, SSID (for management frames), RSSI. |

The table refreshes every 2 seconds while the Monitor tab is the
active one and capture is running. Switching tabs pauses the
refresh; the capture itself keeps running until you click Stop.

### Settings

Live interface tweaks that take effect immediately (no module reload).

| Control          | What it does                                                                 | Range          |
|------------------|------------------------------------------------------------------------------|----------------|
| **MTU**          | Maximum transmission unit — `ip link set <iface> mtu N`                       | 576 – 9000     |
| **TX Power (dBm)** | Transmit power — `iw dev <iface> set txpower fixed N*100`                  | 0 – 30         |
| **Power Save**   | Toggle `iw dev <iface> set power_save on|off`                                | on / off       |
| **Apply**        | Sends the form values to `/api/ifconfig`. Values outside the range are silently skipped |

### Tests

Runs the Python `unittest` suite at `tests/test_driver.py` and
displays the output inline.

- **Run tests** — calls `/api/tests/run`. The button shows a spinner
  while the suite is running.
- **Output panel** — full stdout, with `... ok`, `FAIL` and `ERROR`
  colour-coded.
- **Summary line** — passed / total, plus failed / errors / skipped
  counts pulled from `tests/test_report.json`.

Only the safe (non-destructive) classes run from the dashboard. To
exercise `TestModuleReload` and `TestStability` you must run
`./tests/run_tests.sh --all` from a terminal — the runner needs
NetworkManager / wpa_supplicant stopped first.

### Advanced

A Windows-Device-Manager-style editor for driver **module
parameters**. These are options the driver registers with the kernel
at load time; changing them requires reloading the module to take
effect.

Layout:

- **Left column** — categories (Wireless Mode, Channel & Bandwidth,
  Power Management, Performance, Antenna & Beamforming, Roaming &
  Connection, Debug & Advanced).
- **Middle column** — properties in the selected category. A yellow
  dot next to a property name means you have an unsaved change.
- **Right column** — editor for the selected property:
  - **Property name** + a `Module parameter — restart needed` badge.
  - A `<select>` for enumerated options (Off / On / Auto / …) or a
    plain `<input type="text">` for numeric/bitmask values.
  - **Current value (active)** — what the driver is actually using
    right now.
  - **Saved (waiting for restart)** — value written to
    `/etc/modprobe.d/8852au.conf` but not yet loaded by the kernel.
  - **Description** — a sentence or two explaining what the parameter
    does, what the safe defaults are, and what the trade-off is.

Actions at the bottom:

- **Save & Apply** — writes pending changes to
  `/etc/modprobe.d/8852au.conf`. Will not load them yet.
- **Reset to default** — discards local pending changes (only the
  in-memory ones; doesn't touch already-saved values).
- **Reload module** — `rmmod 8852au` + `modprobe 8852au` so the saved
  options come into effect. **The WiFi link drops briefly** while the
  module restarts.

The yellow banner at the bottom of the tab shows up whenever you have
unsaved changes or saved-but-not-yet-applied changes, with a one-line
instruction what to click next.

---

## Language switcher

The two buttons at the top right (**EN** / **NL**) flip the entire
UI between English and Dutch. The choice is stored in
`localStorage`, so a refresh keeps your preference. On a fresh
browser the dashboard auto-detects the user's locale: a Dutch
browser opens in Dutch, anything else opens in English.

## Theme

Two more buttons in the header — **●** (dark) and **○** (light) —
flip the entire UI between a dark slate theme and a light slate
theme. Like the language choice, it's persisted in `localStorage`.
The sparklines and spectrum canvases pick up the theme's accent
colour automatically.

## Keyboard shortcuts

| Key         | Action                                          |
|-------------|-------------------------------------------------|
| `1`–`5`     | Jump to the corresponding tab                   |
| `/`         | Open Networks and trigger a scan                |
| `r`         | Refresh status / driver info / trends           |
| `t`         | Toggle theme (dark ↔ light)                     |
| `l`         | Toggle language (EN ↔ NL)                       |
| `?`         | Open the shortcuts help overlay                 |
| `Esc`       | Close the overlay                               |

Shortcuts are suppressed while an input, select or textarea has
focus, so they never collide with typing an SSID or passphrase.

---

## Common scenarios

### Connect to an AP I haven't seen before

1. **Networks** → **Scan**. Wait a few seconds.
2. Click **Connect** next to the SSID in the table — this prefills
   the manual connect form.
3. Type the passphrase, click **Connect** in the form.
4. The status badge in the header turns green and the **Overview**
   tab shows the live signal and bitrate.

### Test if my adapter throughput is normal

1. **Overview** — note the current **TX bitrate** under
   *Connection*. WiFi 6 on 80 MHz can reach ~1200 Mbps on a strong
   signal; anything above 500 Mbps is healthy for a desktop scenario.
2. Check **USB speed** under *Adapter Info*. `5000 Mbps` is USB 3
   (good). `480 Mbps` means the adapter has fallen back to USB 2,
   which caps throughput at ~300 Mbps. Try a different USB port,
   ideally one directly on the motherboard.
3. **Statistics** — watch *TX/RX errors* and *dropped*. Both should
   stay near zero. A growing error counter usually points at a weak
   signal or a noisy environment.

### Make the adapter quieter on a laptop

1. **Settings** tab.
2. Set **Power Save** to **On** and **TX Power** to something modest
   (e.g. 15 dBm). Click **Apply**.
3. For a deeper change open **Advanced** → *Power Management* and
   raise `rtw_power_mgnt` to **Maximum**. Click **Save & Apply**,
   then **Reload module**.

### Try a new driver setting and roll back if it breaks

1. **Advanced** — change the property; the yellow dot appears.
2. **Save & Apply** writes it to `/etc/modprobe.d/8852au.conf`.
3. **Reload module** — if the adapter behaves better, you're done.
4. If something breaks, open **Advanced** again, change the property
   back, **Save & Apply** + **Reload module**. Worst case: delete
   `/etc/modprobe.d/8852au.conf` and `sudo modprobe -r 8852au &&
   sudo modprobe 8852au`.

---

## Troubleshooting

**The dashboard won't start: `Address already in use`**

Another copy is still running. Stop it first:

```bash
sudo fuser -k 8080/tcp
```

Or run the new instance on a different port:

```bash
sudo ./.venv/bin/python3 dashboard/app.py --port 9090
```

**The browser keeps asking for login on every refresh**

The browser is not caching Basic Auth credentials (some privacy
extensions strip them). Either install your own cookie/credentials
extension that whitelists `127.0.0.1`, or open the URL with the
token embedded:

```
http://anything:TOKEN@127.0.0.1:8080/
```

(Firefox and Chromium both accept that format, but only on
loopback — they refuse `user:pass@…` for non-loopback URLs.)

**The Overview tab shows "No interface found"**

The dashboard didn't find a `wlan*` device bound to `rtl8852au`.
Verify the module is loaded and the device is recognised:

```bash
lsmod | grep 8852au
ip link | grep wlan
dmesg | tail -20
```

If the device is plugged in but no `wlan*` exists, run `sudo
modprobe -r 8852au && sudo modprobe 8852au`, or check that the USB
ID is in [`os_dep/linux/usb_intf.c`](../os_dep/linux/usb_intf.c).

**A property in the Advanced tab is marked "Not available"**

That module parameter is not compiled into the current `8852au.ko`.
This is usually because the upstream Realtek build flags omitted
it. Either ignore it or rebuild the driver with the corresponding
`CONFIG_*` symbol enabled.

**The Reload module button times out**

`rmmod` is blocking. Most likely cause: NetworkManager or
`wpa_supplicant` is still holding the interface. Stop them, then
retry:

```bash
sudo systemctl stop NetworkManager wpa_supplicant
```

Patch 0007 in this fork makes `rmmod` resilient against this — the
unload path returns in under 200 ms even with the interface up —
but external services that try to *re-grab* the device can still
delay a fresh reload.
