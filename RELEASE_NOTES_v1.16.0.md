# rtl8852au-build v1.16.0

**An out-of-tree Linux driver for Realtek RTL8852AU / RTL8832AU USB WiFi 6 (AX1800) adapters that actually builds on modern kernels.**

The Realtek vendor source (`v1.15.0.1-2`) no longer compiles on recent kernels. This fork carries the version-gated patches that restore the build on **kernel 6.1 → 7.0+** and fixes the monitor-mode crashes that plagued the vendor RX path.

🌐 **Website & docs:** https://wimlee115.github.io/rtl8852au-build/

---

## Why this release

- **Builds on current kernels.** Twelve `LINUX_VERSION_CODE`-gated compatibility patches carry the vendor source across the 6.17+ API removals (WEXT removal, `proc_ops`, `timer_setup`, DMA API, `class_create`, cfg80211 channel-switch + MLO `radio_idx`, …). CI now compiles against distro kernels **and** the newest kernel.org stable and longterm releases, so post-6.18 breakage is caught before it reaches you.
- **Monitor mode that stays up.** Four distinct RX-path crashes are fixed — a UBSAN array out-of-bounds on every WPA key op, a NULL-deref, an SKB use-after-free, and a race with a double-free. A separate patch takes `hw_init_mutex` symmetrically so `rmmod`-while-associated no longer panics (hardware-validated on a TP-Link Archer TX20U Plus).
- **Batteries included.** Idempotent DKMS install, a loopback-only Flask dashboard with per-host auth, a Python `unittest` suite that exercises the live adapter, hash-locked Python dependencies, firmware-blob checksums verified in CI, and bilingual (EN/NL) documentation.

## Install

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) git
git clone https://github.com/WimLee115/rtl8852au-build
cd rtl8852au-build
make -j"$(nproc)"
sudo make install
sudo modprobe 8852au
```

Or install via **DKMS** so the module is rebuilt on every kernel upgrade:

```bash
sudo ./dkms-install.sh
```

Full instructions, troubleshooting, and the dashboard/test-suite guides are in the [README](https://github.com/WimLee115/rtl8852au-build/blob/main/README.md).

## Verified

- **Clean build against Linux 7.0.12+kali-amd64** (GCC 15.3.0): `make` exits 0, `8852au.ko` links with BTF, zero errors, no new patches required. Compile-verified on this kernel.
- **Hardware-validated** on a TP-Link Archer TX20U Plus (`2357:013f`) on Linux 6.19.14+kali: rapid `ip link up/down` cycles and `rmmod`-while-associated no longer panic; `rmmod` returns in ~200 ms, reload re-creates the interface and reassociates cleanly.

## Supported devices

RTL8852AU / RTL8832AU USB adapters — 15 USB IDs across TP-Link, ASUS, D-Link, Buffalo, Elecom and the Realtek reference boards. Full table: [supported devices](https://github.com/WimLee115/rtl8852au-build/blob/main/README.md#supported-devices). Have one working that's only *Recognised*? [Send an `lsusb -v` report](https://github.com/WimLee115/rtl8852au-build/issues/new?template=hardware_support.yml) and it moves to *Tested*.

## Known limitations

- **Kernel 7.1 is not yet supported.** 7.1 refactored a large set of `cfg80211_ops` callbacks from `net_device` to `wireless_dev`, which breaks the station/key callbacks. Kernels up to and including **7.0** build cleanly. A version-gated port is tracked as follow-up work.

## Versioning note

This is the first release under the fork's **own SemVer line**. Earlier fork tags used the vendor-derived `1.15.0.1+N` scheme (immediate predecessor: `1.15.0.1+8`). From here the fork uses plain SemVer, starting at **`1.16.0`** — one step above the Realtek `1.15.0.1` baseline, so the version keeps climbing from the previous tag rather than appearing to roll back. The upstream Realtek baseline remains `v1.15.0.1-2`. See the [CHANGELOG](https://github.com/WimLee115/rtl8852au-build/blob/main/CHANGELOG.md) for the full history.

## Credits

Realtek (original vendor driver), [lwfinger](https://github.com/lwfinger) and [morrownr](https://github.com/morrownr) (community packaging & USB-ID references), [jsiwrk](https://github.com/jsiwrk) (TP-Link Archer TX35U Plus USB ID and the kernel 6.8 build fix, PR #3), and [74Thirsty](https://github.com/74Thirsty) (D-Link DWA-1850 USB ID `2001:332c` and Parrot OS 6/7 testing, PR #14).

---

**Disclaimer.** Independent community fork — not affiliated with, endorsed by, or sponsored by Realtek Semiconductor Corp. or any hardware vendor named here. The firmware blob is © Realtek, redistributed unchanged from the vendor bundle and checksum-verified in CI. Released under the **GNU GPL-2.0**, provided "AS IS" without warranty of any kind.
