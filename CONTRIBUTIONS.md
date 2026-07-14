# D-Link DWA-1850 Linux Driver Patch

## Background

The D-Link DWA-1850 is a WiFi 6 (AX1800) USB adapter based on the Realtek
RTL8832AU chipset. D-Link ships it with Windows-only drivers. The open-source
Linux driver ecosystem for this chipset includes:

- **Realtek vendor source** (`RTL8852AU_WiFi_linux_v1.15.0.1-0-g487ee886`) — only builds on kernels up to 5.9
- **lwfinger/rtl8852au** — community fork, now archived
- **WimLee115/rtl8852au-build** — actively maintained fork with kernel 6.17+ support, bugfixes, dashboard, and test suite

## The Problem

The upstream driver included USB IDs for two DWA-1850 variants (`2001:0141`
and `2001:3321`) but did NOT include the USB ID for the variant with
`2001:332c`. This meant the adapter was not recognized on Linux — it would
show up in `lsusb` but the driver would not bind to it, leaving the user
without WiFi.

## What Was Patched

A single USB device ID was added to `os_dep/linux/usb_intf.c` in the
`rtw_usb_id_tbl[]` array:

```c
/*=== D-Link DWA-1850 (802.11ax, RTL8832AU) ====*/
{USB_DEVICE_AND_INTERFACE_INFO(USB_VENDOR_ID_DLINK, 0x332c, 0xff, 0xff, 0xff), .driver_info = RTL8852A},
```

**File modified:** `os_dep/linux/usb_intf.c` (line 163)
**Change:** One line added — USB ID `2001:332c` under the D-Link section

## Base Driver

This patch is built on top of `WimLee115/rtl8852au-build` (commit
`c144836`) which includes:

- 12 baseline kernel 6.17+ compatibility patches (WEXT removal, netif_rx rename, proc_ops, timer_setup, SKB header API, DMA API, USB pipe macros, etc.)
- 8 post-baseline bugfixes:
  - UBSAN array-out-of-bounds + NULL deref in monitor mode
  - ethtool speed reporting fix
  - SKB use-after-free in monitor mode RX path
  - Kernel panic race condition + double-free
  - Build fix for kernel 6.8
  - netdev_close mutex serialization (rmmod-while-associated panic)
  - cfg80211 MLO signature guards lowered to 6.17
- Full DKMS support
- Web dashboard for runtime diagnostics
- Python test suite

Upstream repo: https://github.com/WimLee115/rtl8852au-build

## Supported Devices

| USB ID     | Device              | Chipset      | Source       |
|------------|---------------------|--------------|--------------|
| `2001:0141`| D-Link DWA-1850     | RTL8832AU    | Upstream     |
| `2001:3321`| D-Link DWA-1850     | RTL8832AU    | Upstream     |
| `2001:332c`| D-Link DWA-1850     | RTL8832AU    | **This patch** |

## Tested On

| Distribution     | Kernel                  | Status |
|------------------|-------------------------|--------|
| Parrot OS 6      | Debian-based, 6.x LTS  | Working |
| Parrot OS 7      | Debian-based, 6.x LTS  | Working |

## Installation

### Prerequisites

```bash
sudo apt update
sudo apt install -y build-essential dkms linux-headers-$(uname -r) git
```

### Build and install

```bash
git clone https://github.com/74Thirsty/rtl8852au-dwa1850.git
cd rtl8852au-dwa1850
make -j"$(nproc)"
sudo make install
sudo modprobe 8852au
```

### DKMS installation (recommended — survives kernel updates)

```bash
sudo ./dkms-install.sh
```

### Verification

```bash
lsusb | grep -i "2001:332c"    # should show your adapter
lsmod | grep 8852au            # should show the module loaded
ip link | grep wlan            # should show a wlan interface
dmesg | grep -i 8852           # check for errors in kernel log
```

## Troubleshooting

**Adapter shows in lsusb but no wlan interface appears:**
```bash
sudo modprobe -r 8852au && sudo modprobe 8852au
# If still nothing, unplug and replug the adapter
```

**Build fails on kernel 6.18+:**
This driver already includes patches for 6.17+. If you hit issues on
newer kernels, check the upstream repo for updates.

## Credits

- **Realtek Semiconductor Corp.** — original vendor driver (v1.15.0.1-2)
- **lwfinger (Larry Finger)** — original community Linux packaging (archived)
- **WimLee115** — kernel 6.17+ compatibility patches, test suite, dashboard, CI
- **Joan Sala (jsiwrk)** — TP-Link Archer TX35U Plus USB ID, kernel 6.8 build fix
- **gadgetsaavy / 74Thirsty** — D-Link DWA-1850 USB ID `2001:332c` addition, Parrot OS 6/7 testing

## License

GNU General Public License v2.0 — same as the upstream driver.
See [LICENSE](LICENSE) for full text.
