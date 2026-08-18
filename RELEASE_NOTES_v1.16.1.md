# rtl8852au-build v1.16.1

**Maintenance release.** One monitor-mode kernel panic, three DKMS packaging faults, and a test suite that reported failures against perfectly healthy installs.

🌐 **Website & docs:** https://wimlee115.github.io/rtl8852au-build/

---

## What's fixed

### Kernel panic when leaving monitor mode under RX load

`rtw_fill_radiotap_hdr()` runs in softirq from the USB RX tasklet and dereferences `padapter->phl_role` for the band, channel and bandwidth fields. `netdev_close()` clears that pointer through `rtw_hw_iface_deinit()` while the tasklet can still be inside `recv_frame_monitor()` — the `netif_running()` guard there is evaluated *before* `skb_copy_expand()`, so it does not cover the radiotap fill that follows.

In the field this showed up after long `airodump-ng` captures:

```
BUG: kernel NULL pointer dereference, address: 0x4e8
RIP: rtw_fill_radiotap_hdr+0x1cf [8852au]
Kernel panic - not syncing: Fatal exception in interrupt
```

`0x4e8` is `chandef.band` inside the freed `rtw_wifi_role_t`. The fault lands in interrupt context, so it is always fatal rather than a recoverable oops. The radiotap path now drops the frame when any of `padapter`/`dvobj`/`phl_com`/`phl_role` is NULL, and `netdev_close()` skips the disassoc path for a monitor interface — it holds no MLME role to disconnect, and the ~700 ms `WAIT_ACK` only widened the teardown race. A regression test cycles monitor → managed under live RX with a capture socket open.

### DKMS install could abort with "DKMS tree already contains"

Both DKMS scripts piped `dkms status` into `grep -q`, which closes the pipe on its first match. `dkms status` then takes SIGPIPE and exits non-zero, so under `set -o pipefail` the whole condition evaluated false — and when it lost that race, the install skipped its cleanup and `dkms add` aborted. `PACKAGE_VERSION` was also interpolated into the regex unescaped, so the dots matched any character. Both scripts now let DKMS filter directly (`dkms status -m NAME -v VER`), with no pipe, no regex and no race. Reproduced under `pipefail` with a multi-line status stub: the old form matched 0/20 runs, the new form 20/20.

`dkms.conf` also still declared the Realtek baseline version `1.15.0.1` while the project had released `1.16.0`, so a fresh install registered under the old number — a factor in the collision above. It now tracks the release version.

### The test suite no longer fails on a healthy install

Reported in [#43](https://github.com/WimLee115/rtl8852au-build/issues/43), where five failures against a working `0bda:8832` adapter all turned out to be test-suite artefacts:

- **Module path was hard-coded** to `<repo>/8852au.ko`, so a DKMS install — the method the README recommends — failed three tests purely because the module sits in `/lib/modules/<release>/updates/dkms/` and is xz-compressed. The path now resolves at run time: in-tree build first (so a stale build still reports a genuine srcversion mismatch), then `modinfo -n`, then the DKMS directory.
- **Adapters behind a USB hub read as unbound.** The sysfs pattern only covered a device on a root port (`1-2:1.0`); behind a hub the port path is dot-separated (`1-8.4:1.0`, `2-1.4.3:1.0` when chained).
- **An empty scan counted as a failure.** Zero BSSes is not evidence of a fault — an rfkill block or a shielded room give the same result — so it now skips with the reason and hard-fails only when the scan mechanism itself errors.

A new hardware-free test class covers this parsing and runs in CI, reachable as `./tests/run_tests.sh --offline`. Every other class in the suite needs a physical adapter, which is why the gap stayed invisible.

## Upgrade

```bash
cd rtl8852au-build
git pull
sudo ./dkms-install.sh
```

The install script now clears **every** registered version of the package
before adding the new one, so the upgrade leaves exactly one DKMS entry
behind. Previously it only cleared the version `dkms.conf` currently named,
which meant a version bump orphaned the old entry — and two entries then
raced to install the same `8852au.ko` into `/updates/dkms` on every kernel
upgrade. If you are upgrading from `1.16.0`, that cleanup happens for you;
verify with `dkms status -m rtl8852au`.

A plain `make` install is unchanged:

```bash
make -j"$(nproc)" && sudo make install && sudo modprobe 8852au
```

## Verified

- **Green across the CI matrix**: Ubuntu 22.04 and 24.04 distro kernels, mainline longterm and stable from kernel.org, DKMS install/remove dry-run, ruff/pyflakes lint, and CodeQL.
- **Monitor-mode fix built clean against Linux 7.0.12** and validated on hardware.
- **Test-suite fix reproduced and verified** on a Kali 7.0.12 system in the reporter's exact configuration (DKMS install, no in-tree build): the affected tests failed on `1.16.0` and pass on this release.

## Known limitations

- **Kernel 7.1 is not yet supported.** 7.1 refactored a large set of `cfg80211_ops` callbacks from `net_device` to `wireless_dev`, which breaks the station/key callbacks. Kernels up to and including **7.0** build cleanly; verified up to Linux 7.0.12. A version-gated port is tracked as follow-up work.

## Supported devices

RTL8852AU / RTL8832AU USB adapters — 15 USB IDs across TP-Link, ASUS, D-Link, Buffalo, Elecom and the Realtek reference boards. Full table: [supported devices](https://github.com/WimLee115/rtl8852au-build/blob/main/README.md#supported-devices). Have one working that's only *Recognised*? [Send an `lsusb -v` report](https://github.com/WimLee115/rtl8852au-build/issues/new?template=hardware_support.yml) and it moves to *Tested*.

## Credits

Realtek (original vendor driver), [lwfinger](https://github.com/lwfinger) and [morrownr](https://github.com/morrownr) (community packaging & USB-ID references), [jsiwrk](https://github.com/jsiwrk) (TP-Link Archer TX35U Plus USB ID and the kernel 6.8 build fix, PR #3), [74Thirsty](https://github.com/74Thirsty) (D-Link DWA-1850 USB ID `2001:332c` and Parrot OS 6/7 testing, PR #14), and [Omelug](https://github.com/Omelug) (hardware report that surfaced both test-suite bugs in this release, issue #43).

---

**Disclaimer.** Independent community fork — not affiliated with, endorsed by, or sponsored by Realtek Semiconductor Corp. or any hardware vendor named here. The firmware blob is © Realtek, redistributed unchanged from the vendor bundle and checksum-verified in CI. Released under the **GNU GPL-2.0**, provided "AS IS" without warranty of any kind.
