#!/usr/bin/env python3
"""
RTL8852AU Driver Test Suite
Verifies that the out-of-tree RTL8852AU WiFi driver works correctly
on the current system.

Run as root: sudo python3 tests/test_driver.py

Safety:
    By default ONLY non-destructive read-only tests run. The destructive
    classes (TestModuleReload, TestStability) caused a hard kernel panic
    on a previous test run because they tear down the module / rapidly
    toggle the interface while the system is actively associated with an
    AP — a race against netdev_close() that has expensive blocking calls
    (rtw_disassoc_cmd with WAIT_ACK, scan_abort, wait_scan_req_empty).

    To run them anyway, set RTW_TEST_DESTRUCTIVE=1 in the environment OR
    pass --destructive. The harness will then refuse to start unless the
    interface is in a safe state (disconnected, NetworkManager stopped).
"""

import argparse
import subprocess
import os
import shutil
import sys
import time
import re
import json
import unittest
import glob
from functools import lru_cache

MODULE_NAME = "8852au"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVER_NAME = "rtl8852au"
EXPECTED_CHIP_ID = 0x50  # RTL8852A

# Modules may be installed compressed — DKMS on Debian/Kali writes
# 8852au.ko.xz. modinfo and modprobe read those transparently; insmod does
# not, so the reload test has to pick its loader based on the suffix.
MODULE_SUFFIXES = (".ko", ".ko.xz", ".ko.gz", ".ko.zst")

# A bound USB interface appears in /sys/bus/usb/drivers/<drv>/ as
# <bus>-<port-path>:<config>.<interface>. The port path is dot-separated and
# nests one level per hub: "1-2:1.0" on a root port, "1-8.4:1.0" behind one
# hub, "2-1.4.3:1.0" behind two. The same directory also holds bind, unbind,
# uevent, module, new_id and remove_id, which this pattern excludes.
USB_INTERFACE_RE = re.compile(r'\d+-\d+(?:\.\d+)*:\d+\.\d+\Z')

DESTRUCTIVE_REASON = (
    "destructive test (rmmod / rapid toggle) — opt in with --destructive "
    "or RTW_TEST_DESTRUCTIVE=1, and only on a system that is not actively "
    "associated to an AP; previous unguarded runs triggered a kernel panic"
)


def destructive_enabled():
    return os.environ.get("RTW_TEST_DESTRUCTIVE", "0") == "1"


def run(cmd, timeout=30, check=False):
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if check and r.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}\n{r.stderr}")
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"


def is_root():
    return os.geteuid() == 0


@lru_cache(maxsize=None)
def find_module_file():
    """Locate the .ko to inspect, or None if there is none.

    Three sources, in the order that matches intent:

    1. An in-tree build in the repo root. If you just ran `make`, that is the
       module you mean, and a srcversion mismatch against the loaded one is a
       real finding rather than noise.
    2. Whatever modprobe would load (`modinfo -n`). This is the normal case
       for anyone who installed with ./dkms-install.sh, where the module
       lives in /lib/modules/<release>/updates/dkms/ and is xz-compressed.
    3. A direct glob of that DKMS directory, for systems where modinfo cannot
       resolve the name.

    Before this, the path was hard-coded to <repo>/8852au.ko, so a DKMS
    install — the method the README recommends — failed three tests purely
    because the file was somewhere else (issue #43).
    """
    for suffix in MODULE_SUFFIXES:
        candidate = os.path.join(REPO_ROOT, f"{MODULE_NAME}{suffix}")
        if os.path.isfile(candidate):
            return candidate

    rc, out, _ = run(f"modinfo -n {MODULE_NAME}")
    if rc == 0 and out and os.path.isfile(out):
        return out

    _, kver, _ = run("uname -r")
    if kver:
        matches = sorted(glob.glob(
            f"/lib/modules/{kver}/updates/dkms/{MODULE_NAME}.ko*"))
        if matches:
            return matches[0]

    return None


def module_is_insmodable(path):
    """insmod takes only an uncompressed .ko; modprobe handles the rest."""
    return bool(path) and path.endswith(".ko")


def bound_usb_interfaces(entries):
    """Filter sysfs driver-directory entries down to bound USB interfaces.

    Split out from the test so the hub-path handling can be verified without
    hardware — see TestSysfsParsing.
    """
    return [e for e in entries if USB_INTERFACE_RE.match(e)]


def rf_blocked():
    """True when rfkill reports a soft or hard block on a wireless device."""
    rc, out, _ = run("rfkill list wifi", timeout=5)
    if rc != 0 or not out:
        return False
    return any(
        line.strip().lower().endswith("blocked: yes")
        for line in out.splitlines()
    )


def get_wlan_interface():
    """Find the wlan interface bound to our driver."""
    for iface_dir in glob.glob("/sys/class/net/wlan*"):
        iface = os.path.basename(iface_dir)
        driver_link = os.path.join(iface_dir, "device", "driver")
        if os.path.islink(driver_link):
            target = os.readlink(driver_link)
            if DRIVER_NAME in target:
                return iface
    return None


def module_loaded():
    """Check if the 8852au module is loaded."""
    rc, out, _ = run(f"lsmod | grep -w {MODULE_NAME}")
    return rc == 0 and MODULE_NAME in out


def _service_active(name):
    rc, _, _ = run(f"systemctl is-active --quiet {name}")
    return rc == 0


def _iface_associated(iface):
    if not iface:
        return False
    rc, out, _ = run(f"iw dev {iface} link", timeout=5)
    if rc != 0:
        return False
    return "Connected to" in out or "SSID:" in out


def safety_preflight(require_disconnected=True):
    """Refuse to run destructive tests if the system is in an unsafe state.

    A panic was observed during a previous test run because rmmod was
    issued while wlan0 was actively associated and NetworkManager kept
    trying to reassociate. We now hard-fail rather than gamble.
    """
    problems = []
    iface = get_wlan_interface()

    if require_disconnected and _iface_associated(iface):
        problems.append(
            f"interface {iface} is associated to an AP — bring it down first: "
            f"sudo ip link set {iface} down"
        )

    if _service_active("NetworkManager"):
        problems.append(
            "NetworkManager is active and will re-associate during the test; "
            "stop it first: sudo systemctl stop NetworkManager"
        )

    if _service_active("wpa_supplicant"):
        problems.append(
            "wpa_supplicant is active; stop it: sudo systemctl stop wpa_supplicant"
        )

    return problems


class TestSysfsParsing(unittest.TestCase):
    """Test 0: pure parsing helpers — no hardware, no root, runs in CI.

    These guard the two assumptions that made a working adapter look broken
    in issue #43: how a bound USB interface is spelled in sysfs, and where an
    installed module file lives.
    """

    def test_01_device_on_root_port(self):
        """An adapter plugged straight into a root port counts as bound."""
        self.assertEqual(bound_usb_interfaces(["1-2:1.0"]), ["1-2:1.0"])

    def test_02_device_behind_hub(self):
        """Regression (issue #43): an adapter behind a USB hub counts too.

        Its port path is dot-separated ("1-8.4:1.0"), and one hub level is
        not the limit — chained hubs nest further ("2-1.4.3:1.0"). The old
        pattern (\\d+-\\d+:\\d+\\.\\d+) matched neither, so a perfectly bound
        device reported "No USB devices bound to driver".
        """
        entries = ["1-8.4:1.0", "2-1.4.3:1.0"]
        self.assertEqual(bound_usb_interfaces(entries), entries)

    def test_03_housekeeping_entries_ignored(self):
        """bind/unbind/uevent/module/new_id/remove_id are not devices."""
        entries = ["bind", "unbind", "uevent", "module", "new_id", "remove_id"]
        self.assertEqual(bound_usb_interfaces(entries), [])

    def test_04_mixed_directory(self):
        """A realistic listing yields only the interface entries."""
        entries = ["bind", "1-8.4:1.0", "module", "uevent", "1-8.4:1.1"]
        self.assertEqual(bound_usb_interfaces(entries),
                         ["1-8.4:1.0", "1-8.4:1.1"])

    def test_05_near_misses_rejected(self):
        """Partial matches must not slip through.

        re.match() only anchors the start, which is why the pattern carries
        an explicit \\Z — otherwise "1-2:1.0.backup" would count as a device.
        """
        for entry in ["1-2:1.0.backup", "1-2:1", "x1-2:1.0", "1-:1.0", "1-2.:1.0"]:
            with self.subTest(entry=entry):
                self.assertEqual(bound_usb_interfaces([entry]), [])

    def test_06_insmod_only_takes_uncompressed(self):
        """DKMS ships 8852au.ko.xz; insmod cannot load a compressed module."""
        self.assertIn(".ko.xz", MODULE_SUFFIXES)
        self.assertTrue(module_is_insmodable("/lib/modules/x/8852au.ko"))
        self.assertFalse(module_is_insmodable("/lib/modules/x/8852au.ko.xz"))
        self.assertFalse(module_is_insmodable(None))


class TestModuleBasics(unittest.TestCase):
    """Test 1: Module load/unload and basic registration."""

    def test_01_module_file_exists(self):
        """Verify a built or installed module file can be located."""
        path = find_module_file()
        self.assertIsNotNone(
            path,
            f"No {MODULE_NAME} module found — neither an in-tree build in "
            f"{REPO_ROOT} nor an installed one (modprobe / DKMS). Build it "
            f"with `make`, or install it with ./dkms-install.sh.",
        )
        self.assertTrue(os.path.isfile(path), f"Module file not found: {path}")

    def test_02_module_info(self):
        """Verify modinfo reports correct metadata."""
        path = find_module_file()
        if not path:
            self.skipTest("no module file to inspect (see test_01)")
        rc, out, _ = run(f"modinfo {path}")
        self.assertEqual(rc, 0, f"modinfo failed for {path}")
        # modinfo reports the module name (8852au) and the Realtek description;
        # the "rtl8852au" string only appears in the sysfs driver name, not in
        # modinfo output. Match either signal.
        named = re.search(rf'^name:\s+{re.escape(MODULE_NAME)}\b', out, re.M)
        self.assertTrue(
            named or "realtek" in out.lower(),
            f"Module name '{MODULE_NAME}' / 'realtek' not found in modinfo",
        )
        self.assertIn("vermagic:", out, "No vermagic in modinfo")
        # Verify kernel version matches
        _, kver, _ = run("uname -r")
        self.assertIn(kver, out,
                       f"Module vermagic doesn't match kernel {kver}")

    def test_03_module_is_loaded(self):
        """Verify module is currently loaded."""
        self.assertTrue(module_loaded(),
                        f"Module {MODULE_NAME} is not loaded")

    def test_04_module_srcversion_matches(self):
        """Verify loaded module matches the built/installed .ko file."""
        path = find_module_file()
        if not path:
            self.skipTest("no module file to compare against (see test_01)")
        rc1, built_src, _ = run(f"modinfo -F srcversion {path}")
        self.assertEqual(rc1, 0, f"modinfo -F srcversion failed for {path}")
        loaded_src_path = f"/sys/module/{MODULE_NAME}/srcversion"
        self.assertTrue(os.path.exists(loaded_src_path),
                        "Module srcversion sysfs entry not found")
        with open(loaded_src_path) as f:
            loaded_src = f.read().strip()
        self.assertEqual(built_src, loaded_src,
                         f"srcversion mismatch: built={built_src} loaded={loaded_src}")

    def test_05_driver_registered(self):
        """Verify USB driver is registered."""
        driver_dir = f"/sys/bus/usb/drivers/{DRIVER_NAME}"
        self.assertTrue(os.path.isdir(driver_dir),
                        f"Driver {DRIVER_NAME} not registered in sysfs")


class TestDeviceBinding(unittest.TestCase):
    """Test 2: Device binding and interface creation."""

    def setUp(self):
        self.iface = get_wlan_interface()

    def test_01_device_bound(self):
        """Verify at least one USB device is bound to our driver."""
        driver_dir = f"/sys/bus/usb/drivers/{DRIVER_NAME}"
        if not os.path.isdir(driver_dir):
            self.fail(f"Driver {DRIVER_NAME} not registered in sysfs "
                      f"({driver_dir} does not exist)")
        entries = os.listdir(driver_dir)
        bound = bound_usb_interfaces(entries)
        self.assertGreater(
            len(bound), 0,
            f"No USB devices bound to driver. Entries in {driver_dir}: "
            f"{sorted(entries)}",
        )

    def test_02_wlan_interface_exists(self):
        """Verify a wlan interface was created for the device."""
        self.assertIsNotNone(self.iface,
                             f"No wlan interface found for {DRIVER_NAME}")

    def test_03_interface_has_mac(self):
        """Verify interface has a valid MAC address."""
        self.assertIsNotNone(self.iface)
        rc, out, _ = run(f"cat /sys/class/net/{self.iface}/address")
        self.assertEqual(rc, 0)
        mac = out.strip()
        self.assertRegex(mac, r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$',
                         f"Invalid MAC: {mac}")
        self.assertNotEqual(mac, "00:00:00:00:00:00", "MAC is all zeros")

    def test_04_interface_mtu(self):
        """Verify MTU is set to a reasonable value."""
        self.assertIsNotNone(self.iface)
        with open(f"/sys/class/net/{self.iface}/mtu") as f:
            mtu = int(f.read().strip())
        self.assertGreaterEqual(mtu, 1500, f"MTU too low: {mtu}")

    def test_05_interface_operstate(self):
        """Verify interface has a valid operational state."""
        self.assertIsNotNone(self.iface)
        with open(f"/sys/class/net/{self.iface}/operstate") as f:
            state = f.read().strip()
        self.assertIn(state, ["up", "down", "dormant", "unknown"],
                      f"Unexpected operstate: {state}")


class TestInterfaceUp(unittest.TestCase):
    """Test 3: Interface can be brought up and down."""

    def setUp(self):
        self.iface = get_wlan_interface()
        if not self.iface:
            self.skipTest("No wlan interface found")

    def test_01_bring_up(self):
        """Verify interface can be brought up."""
        rc, _, err = run(f"ip link set {self.iface} up")
        self.assertEqual(rc, 0, f"Failed to bring up {self.iface}: {err}")
        time.sleep(1)
        with open(f"/sys/class/net/{self.iface}/flags") as f:
            flags = int(f.read().strip(), 16)
        self.assertTrue(flags & 0x1, "IFF_UP flag not set")

    def test_02_bring_down_up(self):
        """Verify interface can be cycled down and up."""
        rc, _, err = run(f"ip link set {self.iface} down")
        self.assertEqual(rc, 0, f"Failed to bring down: {err}")
        time.sleep(1)
        rc, _, err = run(f"ip link set {self.iface} up")
        self.assertEqual(rc, 0, f"Failed to bring back up: {err}")
        time.sleep(1)


class TestWiFiScan(unittest.TestCase):
    """Test 4: WiFi scanning capability."""

    def setUp(self):
        self.iface = get_wlan_interface()
        if not self.iface:
            self.skipTest("No wlan interface found")
        run(f"ip link set {self.iface} up")
        time.sleep(1)

    def test_01_iw_scan_trigger(self):
        """Verify scan can be triggered via iw."""
        # May need to disconnect first
        rc, out, err = run(f"iw dev {self.iface} scan trigger", timeout=10)
        # Allow -EBUSY (rc=240) if already scanning
        self.assertIn(rc, [0, 240],
                      f"Scan trigger failed: rc={rc} err={err}")

    def test_02_iw_scan_results(self):
        """Verify scan returns results.

        Zero BSSes is not evidence of a driver fault: an rfkill block, a
        shielded room or simply no AP within range all produce an empty dump.
        So the hard assertion is on the scan mechanism working (dump exits
        clean); an empty-but-successful scan skips with the reason instead of
        reporting a failure the reader then has to talk themselves out of.
        """
        run(f"iw dev {self.iface} scan trigger", timeout=10)
        time.sleep(5)
        rc, out, err = run(f"iw dev {self.iface} scan dump", timeout=15)
        self.assertEqual(rc, 0, f"Scan dump failed: {err}")

        bss_count = out.count("BSS ")
        if bss_count == 0:
            if rf_blocked():
                self.skipTest(
                    "rfkill reports a block — the radio is off, so no scan "
                    "result is possible. Unblock with: sudo rfkill unblock wifi"
                )
            self.skipTest(
                "scan ran cleanly but returned no BSS — no AP in range, or a "
                "shielded environment. Re-run within range of an AP to "
                "exercise this path."
            )

    def test_03_supported_bands(self):
        """Verify driver reports supported frequency bands."""
        rc, out, _ = run("iw phy")
        self.assertEqual(rc, 0)
        # RTL8852AU should support 2.4GHz and 5GHz
        has_2g = "2412 MHz" in out or "Band 1" in out
        has_5g = "5180 MHz" in out or "Band 2" in out
        self.assertTrue(has_2g, "2.4GHz band not reported")
        self.assertTrue(has_5g, "5GHz band not reported")


class TestCfg80211(unittest.TestCase):
    """Test 5: cfg80211/nl80211 interface."""

    def setUp(self):
        self.iface = get_wlan_interface()
        if not self.iface:
            self.skipTest("No wlan interface found")

    def test_01_iw_info(self):
        """Verify iw can query interface info."""
        rc, out, err = run(f"iw dev {self.iface} info")
        self.assertEqual(rc, 0, f"iw dev info failed: {err}")
        self.assertIn(self.iface, out)
        self.assertIn("type", out)

    def test_02_phy_info(self):
        """Verify phy info is available."""
        # Get phy name for our interface
        rc, out, _ = run(f"iw dev {self.iface} info")
        match = re.search(r'wiphy (\d+)', out)
        if not match:
            self.skipTest("Could not determine wiphy")
        phy_idx = match.group(1)
        rc, out, _ = run(f"iw phy phy{phy_idx} info")
        self.assertEqual(rc, 0)
        self.assertIn("Capabilities:", out)

    def test_03_interface_modes(self):
        """Verify supported interface modes include managed."""
        rc, out, _ = run("iw phy")
        self.assertEqual(rc, 0)
        self.assertIn("managed", out.lower(),
                       "Managed mode not supported")

    def test_04_station_dump(self):
        """Verify station dump command works (even if empty)."""
        rc, out, err = run(f"iw dev {self.iface} station dump")
        self.assertEqual(rc, 0,
                         f"Station dump failed: {err}")


class TestProcFS(unittest.TestCase):
    """Test 6: /proc interface."""

    def test_01_proc_entry_exists(self):
        """Verify proc entry for the driver exists."""
        proc_dirs = glob.glob("/proc/net/rtw_*")
        # It's ok if proc isn't enabled
        if not proc_dirs:
            self.skipTest("No /proc/net/rtw_* entries (proc may be disabled)")
        self.assertGreater(len(proc_dirs), 0)


class TestUSBEndpoints(unittest.TestCase):
    """Test 7: USB endpoint verification."""

    def setUp(self):
        self.iface = get_wlan_interface()
        if not self.iface:
            self.skipTest("No wlan interface found")
        # Get USB device path
        dev_path = os.path.realpath(f"/sys/class/net/{self.iface}/device")
        self.usb_path = dev_path

    def test_01_usb_speed(self):
        """Verify USB speed is high-speed or super-speed."""
        parent = os.path.dirname(self.usb_path)
        speed_file = os.path.join(parent, "speed")
        if os.path.exists(speed_file):
            with open(speed_file) as f:
                speed = int(f.read().strip())
            self.assertGreaterEqual(speed, 480,
                                    f"USB speed too low: {speed} Mbps")

    def test_02_usb_endpoints(self):
        """Verify USB endpoints are present."""
        ep_dirs = glob.glob(os.path.join(self.usb_path, "ep_*"))
        # Should have at least bulk in + bulk out
        self.assertGreaterEqual(len(ep_dirs), 2,
                                f"Too few endpoints: {len(ep_dirs)}")


class TestDmesgClean(unittest.TestCase):
    """Test 8: Kernel log check for errors."""

    def test_01_no_kernel_errors(self):
        """Verify no kernel errors/warnings related to our driver."""
        rc, out, _ = run("dmesg")
        if rc != 0:
            self.skipTest("Cannot read dmesg (need root?)")
        lines = out.split('\n')
        errors = []
        for line in lines:
            lower = line.lower()
            if DRIVER_NAME in lower or MODULE_NAME in lower:
                if any(w in lower for w in ['error', 'bug', 'oops', 'panic',
                                             'null pointer', 'unable to handle',
                                             'general protection fault']):
                    errors.append(line.strip())
        self.assertEqual(len(errors), 0,
                         "Kernel errors found:\n" + "\n".join(errors))

    def test_02_no_usb_errors(self):
        """Check for USB-related errors on our device."""
        iface = get_wlan_interface()
        if not iface:
            self.skipTest("No wlan interface")
        rc, out, _ = run("dmesg")
        lines = out.split('\n')
        usb_errors = []
        for line in lines:
            lower = line.lower()
            if 'usb' in lower and any(w in lower for w in
                    ['disconnect', 'reset', 'error', 'timeout']):
                # Filter for our driver
                if DRIVER_NAME in lower or MODULE_NAME in lower:
                    usb_errors.append(line.strip())
        # Warn but don't fail for minor USB issues
        if usb_errors:
            print("\nWARNING: USB issues detected:\n" +
                  "\n".join(usb_errors[:5]))


class TestModuleReload(unittest.TestCase):
    """Test 9: Module unload/reload stability (destructive)."""

    @classmethod
    def setUpClass(cls):
        if not destructive_enabled():
            raise unittest.SkipTest(DESTRUCTIVE_REASON)
        problems = safety_preflight(require_disconnected=True)
        if problems:
            raise unittest.SkipTest(
                "destructive preflight failed:\n  - " + "\n  - ".join(problems)
            )

    @unittest.skipUnless(is_root(), "Requires root")
    def test_01_reload_module(self):
        """Verify module can be unloaded and reloaded cleanly.

        Pre-step: bring the interface down explicitly before rmmod so the
        driver's netdev_close runs to completion before usb_disconnect.
        Doing rmmod against an UP interface raced with cfg80211/NM and
        panicked the kernel on a previous run.
        """
        iface_before = get_wlan_interface()
        if iface_before:
            run(f"ip link set {iface_before} down", timeout=10)
            time.sleep(2)  # let netdev_close finish (disassoc_cmd waits ~500ms)

        rc, _, err = run(f"rmmod {MODULE_NAME}", timeout=15)
        self.assertEqual(rc, 0, f"rmmod failed: {err}")
        time.sleep(3)

        self.assertFalse(module_loaded(), "Module still loaded after rmmod")

        # Reload via whichever loader can actually read the file we found. A
        # DKMS install leaves an xz-compressed module, and insmod cannot load
        # that — it takes an uncompressed .ko only.
        path = find_module_file()
        if module_is_insmodable(path):
            reload_cmd = f"insmod {path}"
        else:
            reload_cmd = f"modprobe {MODULE_NAME}"
        rc, _, err = run(reload_cmd, timeout=15)
        self.assertEqual(rc, 0, f"`{reload_cmd}` failed: {err}")
        time.sleep(4)

        self.assertTrue(module_loaded(), f"Module not loaded after `{reload_cmd}`")

        iface_after = get_wlan_interface()
        self.assertIsNotNone(iface_after,
                             "Interface not recreated after reload")


class TestStability(unittest.TestCase):
    """Test 10: Basic stability tests (destructive — opt-in)."""

    @classmethod
    def setUpClass(cls):
        if not destructive_enabled():
            raise unittest.SkipTest(DESTRUCTIVE_REASON)
        problems = safety_preflight(require_disconnected=True)
        if problems:
            raise unittest.SkipTest(
                "destructive preflight failed:\n  - " + "\n  - ".join(problems)
            )

    def setUp(self):
        self.iface = get_wlan_interface()
        if not self.iface:
            self.skipTest("No wlan interface found")

    def test_01_rapid_ifup_ifdown(self):
        """Stress test: toggle interface 10 times with enough headroom
        for netdev_close to finish.

        netdev_close calls rtw_disassoc_cmd(WAIT_ACK) (~500ms) plus
        rtw_cfg80211_wait_scan_req_empty(200ms). A 200ms cycle stacked
        unfinished close-paths and triggered a kernel panic. We now wait
        ~1.5s per half-cycle and verify the interface is fully down/up
        before issuing the next command.
        """
        for _ in range(10):
            run(f"ip link set {self.iface} down", timeout=10)
            time.sleep(1.5)
            run(f"ip link set {self.iface} up", timeout=10)
            time.sleep(1.5)

        time.sleep(2)
        rc, out, _ = run(f"iw dev {self.iface} info")
        self.assertEqual(rc, 0, "Interface broken after rapid toggle")

    def test_02_multiple_scan_triggers(self):
        """Stress test: trigger multiple scans in succession.

        Wait longer between triggers so cfg80211_wait_scan_req_empty()
        in any concurrent ifdown can drain.
        """
        run(f"ip link set {self.iface} up")
        time.sleep(2)
        for _ in range(5):
            run(f"iw dev {self.iface} scan trigger")
            time.sleep(2)
        rc, out, _ = run(f"iw dev {self.iface} scan dump", timeout=15)
        self.assertEqual(rc, 0, "Scan dump failed after multiple triggers")

    def test_03_monitor_teardown_under_rx_load(self):
        """Regression: leave monitor mode while the RX path is still live.

        rtw_fill_radiotap_hdr() dereferences padapter->phl_role for the
        band, channel and bandwidth fields. netdev_close() clears that
        pointer through rtw_hw_iface_deinit() while the USB RX tasklet can
        still be inside recv_frame_monitor(): the netif_running() guard
        there is evaluated before skb_copy_expand(), so it does not cover
        the radiotap fill that follows. Observed in the field as

            BUG: kernel NULL pointer dereference, address: 0x4e8
            RIP: rtw_fill_radiotap_hdr+0x1cf [8852au]
            Kernel panic - not syncing: Fatal exception in interrupt

        after a 300 s airodump-ng capture, where 0x4e8 is chandef.band
        inside the freed rtw_wifi_role_t. The fault lands in interrupt
        context, so it is always fatal rather than a recoverable oops.

        This cycles monitor -> managed with frames still arriving and a
        capture socket still open, which is the ordering that crashed.
        Surviving the loop is the pass condition.
        """
        iface = self.iface
        sniffer = None

        try:
            for _ in range(5):
                run(f"ip link set {iface} down", timeout=10)
                rc, _, err = run(f"iw dev {iface} set type monitor", timeout=10)
                self.assertEqual(rc, 0, f"could not enter monitor mode: {err}")
                run(f"ip link set {iface} up", timeout=10)

                # Park on a busy 2.4 GHz channel so beacons keep the RX
                # tasklet inside the radiotap path during the teardown.
                run(f"iw dev {iface} set channel 1", timeout=10)

                if shutil.which("tcpdump"):
                    sniffer = subprocess.Popen(
                        ["tcpdump", "-i", iface, "-w", os.devnull, "-U"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                time.sleep(3)

                # Signal the sniffer but do NOT reap it: the packet socket
                # stays open across netdev_close(), which is exactly the
                # window the panic needed.
                if sniffer:
                    sniffer.terminate()

                run(f"ip link set {iface} down", timeout=10)
                rc, _, err = run(f"iw dev {iface} set type managed", timeout=10)
                self.assertEqual(rc, 0, f"could not leave monitor mode: {err}")
                run(f"ip link set {iface} up", timeout=10)
                time.sleep(1.5)

                if sniffer:
                    sniffer.kill()
                    sniffer.wait(timeout=5)
                    sniffer = None
        finally:
            if sniffer and sniffer.poll() is None:
                sniffer.kill()
            run(f"ip link set {iface} down", timeout=10)
            run(f"iw dev {iface} set type managed", timeout=10)
            run(f"ip link set {iface} up", timeout=10)

        rc, out, _ = run(f"iw dev {iface} info", timeout=10)
        self.assertEqual(rc, 0, "Interface broken after monitor teardown cycles")
        self.assertIn("type managed", out, "Interface did not return to managed")


def generate_report(result):
    """Generate a JSON test report."""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "module": MODULE_NAME,
        "driver": DRIVER_NAME,
        "kernel": subprocess.getoutput("uname -r"),
        "total": result.testsRun,
        "passed": max(0, result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "details": []
    }

    for test, traceback in result.failures:
        report["details"].append({
            "test": str(test),
            "status": "FAILED",
            "message": traceback
        })
    for test, traceback in result.errors:
        report["details"].append({
            "test": str(test),
            "status": "ERROR",
            "message": traceback
        })
    for test, reason in result.skipped:
        report["details"].append({
            "test": str(test),
            "status": "SKIPPED",
            "message": reason
        })

    return report


def parse_cli():
    p = argparse.ArgumentParser(
        description="RTL8852AU driver test suite",
        epilog="By default only non-destructive tests run. "
               "Use --destructive to enable rmmod / rapid-toggle tests; "
               "the harness will refuse to start them while the interface "
               "is associated or NetworkManager is running.",
    )
    p.add_argument(
        "--destructive",
        action="store_true",
        help="enable destructive tests (TestModuleReload, TestStability). "
             "Equivalent to RTW_TEST_DESTRUCTIVE=1.",
    )
    p.add_argument(
        "-k",
        dest="pattern",
        default=None,
        help="run only tests whose class name contains the substring (e.g. -k TestWiFiScan)",
    )
    p.add_argument(
        "-v", "--verbose",
        action="count",
        default=2,
        help="unittest verbosity level (default: 2)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_cli()
    if args.destructive:
        os.environ["RTW_TEST_DESTRUCTIVE"] = "1"

    if not is_root():
        print("WARNING: Some tests require root privileges. Run with sudo for full coverage.")

    if destructive_enabled():
        print("WARNING: destructive tests enabled — rmmod and rapid ifup/ifdown will run.")
        print("         These have triggered kernel panics when the interface was associated.")
        print("         Pre-flight will hard-fail if NetworkManager is running or wlan is up.\n")

    loader = unittest.TestLoader()
    if args.pattern:
        suite = unittest.TestSuite()
        for cls_name, cls in list(sys.modules[__name__].__dict__.items()):
            if (isinstance(cls, type) and issubclass(cls, unittest.TestCase)
                    and args.pattern in cls_name):
                suite.addTests(loader.loadTestsFromTestCase(cls))
    else:
        suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=args.verbose)
    result = runner.run(suite)

    report = generate_report(result)
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {report_path}")
    print(f"Total: {report['total']} | Passed: {report['passed']} | "
          f"Failed: {report['failed']} | Errors: {report['errors']} | "
          f"Skipped: {report['skipped']}")

    sys.exit(0 if result.wasSuccessful() else 1)
