# rtl8852au-build

**English** | [Nederlands](README.nl.md)

[![CI](https://github.com/WimLee115/rtl8852au-build/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/WimLee115/rtl8852au-build/actions/workflows/ci.yml)
[![License: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](LICENSE)
[![Kernel](https://img.shields.io/badge/kernel-6.1%20%E2%80%93%207.0%2B-informational.svg)](#compatibility)

Out-of-tree Linux driver for USB WiFi adapters based on the Realtek
**RTL8852AU** and **RTL8832AU** (WiFi 6, AX1800) chipsets. The upstream
vendor source (`v1.15.0.1-2`) no longer compiles on modern kernels; this
fork carries a set of targeted patches that restore the build on kernels
6.17 and newer and fix several runtime issues that surfaced under
sanitizer-enabled kernels.

The fork's scope is deliberately narrow: keep the driver building,
keep monitor-mode reliable, and stay close to the vendor source so
upstream changes can be re-applied later.

---

## Table of contents

- [What this fork changes](#what-this-fork-changes)
- [Install](#install)
- [DKMS install](#dkms-install)
- [Supported devices](#supported-devices)
- [Patch set](#patch-set)
- [Web dashboard](#web-dashboard)
- [Test suite](#test-suite)
- [Compatibility](#compatibility)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## What this fork changes

Relative to the Realtek vendor source `v1.15.0.1-2`:

- **Kernel 6.17+ compatibility** — twelve compile-time fixes for API
  removals and signature changes (WEXT removal, `netif_rx` rename,
  `proc_ops`, `ndo_get_stats64`, `timer_setup`, SKB header API, DMA
  API, USB pipe macros, `access_ok` arity, implicit fallthrough,
  `class_create` signature, cfg80211 channel-switch + MLO `radio_idx`).
- **UBSAN array-out-of-bounds** fix on every WPA/WPA2 key operation
  (`include/ieee80211.h`).
- **Monitor-mode NULL-deref, SKB use-after-free, race + double-free**
  in `core/rtw_recv.c`.
- **netdev_close race + rmmod-while-associated panic** —
  `netdev_close()` now takes `hw_init_mutex` symmetrically with
  `netdev_open()` and skips the disassoc cmd path when the device is
  surprise-removed (`os_dep/linux/os_intfs.c`).
- **Ethtool reports a real link speed** instead of `Speed: unknown`.
- **USB IDs added** for adapters confirmed to use the RTL8852AU
  chipset (TP-Link TX20U Plus, TX35U Plus).

Each change is a separate commit; the post-baseline ones are also
exported as standalone `git format-patch` files in
[`patches/`](patches/). See [CHANGELOG.md](CHANGELOG.md) for the full
history.

## Install

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) git
git clone https://github.com/WimLee115/rtl8852au-build.git
cd rtl8852au-build
make -j"$(nproc)"
sudo make install
sudo modprobe 8852au
```

Verify:

```bash
lsmod   | grep 8852au
ip link | grep wlan
dmesg   | grep -iE "8852|rtw"
```

If the adapter is plugged in but no `wlan*` interface appears, unplug
and replug after `modprobe` so the USB subsystem rebinds.

## DKMS install

DKMS rebuilds the module automatically when the kernel is upgraded.

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) git
git clone https://github.com/WimLee115/rtl8852au-build.git
cd rtl8852au-build
sudo ./dkms-install.sh
```

`dkms-install.sh` reads `PACKAGE_NAME` and `PACKAGE_VERSION` from
`dkms.conf`, copies the source to `/usr/src`, registers, builds and
installs the module via DKMS, and finally `modprobe`s it.

Uninstall:

```bash
sudo ./dkms-remove.sh
```

## Supported devices

USB adapters based on the **RTL8852AU** or **RTL8832AU** chipset. The
table below is generated from `os_dep/linux/usb_intf.c`.

| USB ID       | Device                         | Chipset    | Status     |
|--------------|--------------------------------|------------|------------|
| `0bda:8832`  | Realtek reference board        | RTL8832AU  | Recognised |
| `0bda:885a`  | Realtek reference board        | RTL8852AU  | Recognised |
| `0bda:885c`  | Realtek reference board        | RTL8852AU  | Recognised |
| `0b05:1997`  | ASUS USB-AX56 (variant)        | RTL8852AU  | Recognised |
| `0b05:1a62`  | ASUS USB-AX56 (no cradle)      | RTL8832AU  | Recognised |
| `0411:0312`  | Buffalo WI-U3-1200AX2(/N)      | RTL8852AU  | Recognised |
| `2001:0141`  | D-Link DWA-X1850               | RTL8852AU  | Recognised |
| `2001:3321`  | D-Link DWA-X1850 (variant)     | RTL8852AU  | Recognised |
| `35bc:0100`  | TP-Link AX1800 (generic)       | RTL8852AU  | Recognised |
| `2357:013f`  | TP-Link Archer TX20U Plus      | RTL8852AU  | **Tested** |
| `2357:0140`  | TP-Link AX1800 (variant)       | RTL8852AU  | Recognised |
| `2357:0141`  | TP-Link AX1800 (variant)       | RTL8852AU  | Recognised |
| `3625:010f`  | TP-Link Archer TX35U Plus      | RTL8852AU  | Recognised |
| `056e:4020`  | Elecom WDC-X1201DU3            | RTL8852AU  | Recognised |

**Tested** means the maintainer has verified bind, association and
traffic on that specific device. **Recognised** means the USB ID is in
the driver and the chipset matches, but a full end-to-end check is
pending.

To request a new ID, open a [hardware support
request](https://github.com/WimLee115/rtl8852au-build/issues/new?template=hardware_support.yml)
with `lsusb -v` output that proves the device uses an RTL8852AU /
RTL8832AU chipset.

## Patch set

The baseline commit (`2be21aa`) integrates the twelve kernel
compatibility patches that the vendor source needs to compile on Linux
6.17+:

| #  | Patch                          | Files                                                    | Note                                       |
|----|--------------------------------|----------------------------------------------------------|--------------------------------------------|
| 01 | `cfg80211-wext-removal`        | `os_dep/linux/ioctl_cfg80211.c`                          | cfg80211 dropped the WEXT bridge           |
| 02 | `netif-rx-timestamp`           | `os_dep/linux/recv_linux.c`                              | `netif_rx` → `netif_rx_any_context`        |
| 03 | `proc-ops-compat`              | `os_dep/linux/rtw_proc.c`                                | `proc_ops` instead of `file_operations`    |
| 04 | `ndo-get-stats-removal`        | `os_dep/linux/os_intfs.c`                                | `ndo_get_stats` → `ndo_get_stats64`        |
| 05 | `timer-setup-macro`            | `core/rtw_mlme_ext.c`, `core/rtw_tdls.c`                 | `timer_setup()`                            |
| 06 | `skb-header-api`               | `core/rtw_recv.c`, `os_dep/linux/recv_linux.c`           | SKB header accessor changes                |
| 07 | `pci-alloc-consistent`         | `hal/pci/pci_ops.c`                                      | DMA API replaces `pci_alloc_consistent`    |
| 08 | `usb-pipe-macros`              | `hal/usb/usb_ops.c`                                      | Stricter USB pipe type-checking            |
| 09 | `access-ok-args`               | `os_dep/linux/ioctl_linux.c`                             | 2-argument `access_ok()`                   |
| 10 | `implicit-fallthrough`         | multiple `core/`, `hal/`                                 | `fallthrough;` annotations                 |
| 11 | `class-create-api`             | `os_dep/linux/os_intfs.c`                                | `class_create()` lost the `owner` argument |
| 12 | `cfg80211-ch-switch`           | `os_dep/linux/ioctl_cfg80211.c`                          | `cfg80211_ch_switch_notify` new signature  |

Post-baseline fixes (bugfixes, hardware additions, build fixes for
intermediate kernels) live in [`patches/`](patches/) as standalone
`git format-patch` files; they are also already part of the current
tree. See [`patches/README.md`](patches/README.md) for the index.

## Web dashboard

A small Flask app that exposes the driver's runtime state and a few
controls (scan, connect, MTU, txpower, module reload). The dashboard
binds to `127.0.0.1` by default and protects every endpoint with HTTP
Basic Auth — the password is a per-host token generated on first run
and stored as mode `0600` in `~/.config/rtl8852au/dashboard.token`.

```bash
pip install --require-hashes -r dashboard/requirements.txt
sudo python3 dashboard/app.py
# Open the printed URL; username is ignored, password = the printed token.
```

Pass `--host 0.0.0.0` to expose the dashboard to the LAN. The auth
token is then the only thing standing between the network and
root-level operations on this host — keep it private.

A walkthrough of every tab, every control and a handful of common
scenarios is in [`docs/dashboard.md`](docs/dashboard.md).

## Test suite

`tests/test_driver.py` is a Python `unittest` suite that exercises the
driver against the running kernel and a connected adapter. A JSON
report is written to `tests/test_report.json` after each run.

```bash
sudo ./tests/run_tests.sh                # safe, non-destructive
sudo ./tests/run_tests.sh --module       # module + binding (read-only)
sudo ./tests/run_tests.sh --interface    # ifup/ifdown + cfg80211 queries
sudo ./tests/run_tests.sh --scan         # iw scan trigger + dump
sudo ./tests/run_tests.sh --usb          # USB endpoint + speed
sudo ./tests/run_tests.sh --dmesg        # kernel log scan for errors
```

The destructive classes (`TestModuleReload`, `TestStability`) tear
down the module and rapidly cycle the interface. They are opt-in and
the runner refuses to start them while `NetworkManager`,
`wpa_supplicant`, or an active association is present:

```bash
sudo systemctl stop NetworkManager wpa_supplicant
sudo ip link set wlan0 down
sudo ./tests/run_tests.sh --reload       # rmmod + insmod cycle
sudo ./tests/run_tests.sh --stability    # rapid ifup/ifdown + scans
sudo ./tests/run_tests.sh --all          # everything, including destructive
```

| Test class           | Verifies                                                              |
|----------------------|-----------------------------------------------------------------------|
| `TestModuleBasics`   | `.ko` exists, `modinfo` matches vermagic, driver registered in sysfs  |
| `TestDeviceBinding`  | USB device bound, `wlan*` created, valid MAC + MTU                    |
| `TestInterfaceUp`    | Interface up/down cycles cleanly, IFF_UP set                          |
| `TestWiFiScan`       | `iw scan trigger` returns BSS; 2.4 GHz + 5 GHz bands advertised       |
| `TestCfg80211`       | `iw dev info`, phy info, managed-mode supported, station dump         |
| `TestProcFS`         | `/proc/net/rtw_*` entries exist (skipped if `CONFIG_PROC_DEBUG=n`)    |
| `TestUSBEndpoints`   | USB speed ≥ 480 Mbps, at least two endpoints present                  |
| `TestDmesgClean`     | No `error`/`bug`/`oops`/`panic` in dmesg for this driver              |
| `TestModuleReload`   | *(destructive)* `rmmod` + `insmod`; interface comes back              |
| `TestStability`      | *(destructive)* 10× ifup/ifdown with 1.5 s spacing + 5× scan triggers |

## Compatibility

| Distribution               | Kernel             | Arch    | Verified by         |
|----------------------------|--------------------|---------|---------------------|
| Kali Linux Rolling 2026.1  | 6.19.14+kali-amd64 | x86_64  | Maintainer hardware |
| Kali Linux Rolling         | 7.0.12+kali-amd64  | x86_64  | Maintainer build    |
| Ubuntu 22.04 LTS           | distro default     | x86_64  | CI build matrix     |
| Ubuntu 24.04 LTS           | distro default     | x86_64  | CI build matrix     |

Other kernels in the 6.1 LTS → 7.0+ range are expected to compile
because every patch is gated on the relevant `LINUX_VERSION_CODE`, but
they are not verified by the maintainer.

## Troubleshooting

<details>
<summary><strong>Build fails with "implicit declaration of function 'wireless_send_event'"</strong></summary>

The patch that removes the WEXT references didn't take. Make sure
you're building from this repository, not a vanilla
[`lwfinger/rtl8852au`](https://github.com/lwfinger/rtl8852au)
checkout, and run a clean build:

```bash
make clean
make -j"$(nproc)"
```
</details>

<details>
<summary><strong><code>modprobe 8852au</code> reports "module not found"</strong></summary>

```bash
sudo depmod -a
sudo modprobe 8852au
find /lib/modules/"$(uname -r)" -name '8852au.ko*'
```
</details>

<details>
<summary><strong>Adapter is plugged in but no <code>wlanX</code> appears</strong></summary>

```bash
lsusb | grep -iE "realtek|tp-link|d-link|asus"
dmesg | tail -30
sudo modprobe -r 8852au && sudo modprobe 8852au
```

If the adapter shows up under `lsusb` but no interface is created,
the USB ID is probably not in the driver's table. Open a hardware
support request with `lsusb -v -d VVVV:PPPP` output.
</details>

<details>
<summary><strong>Monitor mode: <code>iw dev wlanX set type monitor</code> fails</strong></summary>

```bash
sudo ip link set wlan1 down
sudo iw dev wlan1 set type monitor
sudo ip link set wlan1 up
```

If `NetworkManager` interferes, either stop it or mark the interface
unmanaged in `/etc/NetworkManager/NetworkManager.conf`:

```ini
[keyfile]
unmanaged-devices=interface-name:wlan1
```
</details>

<details>
<summary><strong>USB 3.0 adapter only reaches ~100 Mbps</strong></summary>

```bash
lsusb -t | grep 8852         # should report "5000M"; "480M" = fell back to USB 2.0
```

If the link rate is right but throughput is low, disable aggressive
power management:

```bash
echo 'options 8852au rtw_power_mgnt=0' | sudo tee /etc/modprobe.d/8852au.conf
sudo modprobe -r 8852au && sudo modprobe 8852au
```
</details>

<details>
<summary><strong>Secure Boot: "module verification failed: signature and/or required key missing"</strong></summary>

Sign the freshly-built module with your Machine Owner Key (MOK):

```bash
sudo /usr/src/linux-headers-"$(uname -r)"/scripts/sign-file \
    sha256 \
    /var/lib/shim-signed/mok/MOK.priv \
    /var/lib/shim-signed/mok/MOK.der \
    /lib/modules/"$(uname -r)"/updates/dkms/8852au.ko
```

If you don't have a MOK yet, enrol one with `mokutil --import`, reboot
and complete the prompt, then re-sign.
</details>

## Security

- Vulnerability reports go to the maintainer via the address in
  [`SECURITY.md`](SECURITY.md), not via public issues.
- The repository has [private vulnerability
  reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)
  enabled.
- Firmware blobs are tracked in [`CHECKSUMS.sha256`](CHECKSUMS.sha256)
  and verified by CI on every build.
- The dashboard binds to loopback by default and requires HTTP Basic
  Auth on every endpoint.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for scope, bug-report and
hardware-addition guidelines, and the vendor-style requirement for
driver-source patches. In short:

- One logical change per commit; vendor-style for `core/`, `hal/`,
  `os_dep/` (tabs, K&R braces, no large reformats).
- Python (`dashboard/`, `tests/`, `tools/`) passes `ruff check` with
  the config in [`ruff.toml`](ruff.toml).
- Shell passes `shellcheck`.
- CI must be green before merge; branch protection on `main` enforces
  this.

## Credits

- **Realtek Semiconductor Corp.** — original vendor driver
  (`v1.15.0.1-2`).
- **[lwfinger](https://github.com/lwfinger)** — long-running community
  Linux packaging.
- **[morrownr](https://github.com/morrownr)** — USB WiFi adapter
  documentation, USB-ID references, maintenance patterns.
- **[Joan Sala (`jsiwrk`)](https://github.com/jsiwrk)** — TP-Link
  Archer TX35U Plus USB ID (PR #3).
- **[WimLee115](https://github.com/WimLee115)** — fork maintenance,
  kernel-compatibility patches, test suite, dashboard.

## Disclaimer

This is an **independent community fork**. It is not affiliated with,
endorsed by, or sponsored by **Realtek Semiconductor Corp.**, **TP-Link
Technologies**, **ASUSTeK Computer Inc.**, **D-Link Corporation**,
**Buffalo Inc.**, **Elecom Co., Ltd.**, or any other hardware vendor
named in this repository. Product names and USB IDs are listed for
identification purposes only.

The firmware blob in
[`phl/hal_g6/mac/fw_ax/rtl8852a/hal8852a_fw.c.xz`](phl/hal_g6/mac/fw_ax/rtl8852a/hal8852a_fw.c.xz)
is © Realtek Semiconductor Corp. and is redistributed **unchanged**
from the Realtek `v1.15.0.1-2` vendor source bundle. Its SHA-256 is
recorded in [`CHECKSUMS.sha256`](CHECKSUMS.sha256) and verified by CI
on every build.

As with any out-of-tree kernel module, **the software is provided "AS
IS" without warranty of any kind**, as stated in the
[GPL-2.0 licence](LICENSE) under which it is distributed.

## License

GNU General Public License v2.0 — see [`LICENSE`](LICENSE). The
driver originates from Realtek's GPL-licensed source; every change in
this repository is released under the same licence.

```
SPDX-License-Identifier: GPL-2.0
```
