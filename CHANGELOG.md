# Changelog

All notable changes to this fork are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project uses
the Realtek vendor version `1.15.0.1` as its baseline and tracks fork-local
changes in this file.

## [Unreleased]

### Added
- **USB ID `2357:012e` for the TP-Link Archer TX20U**, reported in
  [#53](https://github.com/WimLee115/rtl8852au-build/issues/53) as
  "Interface not created" — the device's `lsusb -v` shows a plain
  vendor-specific interface (class/subclass/protocol `ff/ff/ff`) typical
  of this chipset family, but `2357:012e` had no entry in
  `rtw_usb_id_tbl[]`, so the kernel never matched the device to this
  driver and no `wlan` interface appeared. The pre-fork vendor README
  once listed this exact ID (under the name "TX20U Nano") as supported,
  but it never actually made it into `os_dep/linux/usb_intf.c` at any
  point in this fork's history — confirmed with `git log -p -S012e`
  against the whole file history, back to the `1.15.0.1` baseline. Added
  next to the other TP-Link entries in `usb_intf.c` and to both device
  tables; marked **Recognised** rather than Tested since the reporter
  flagged this as untested hardware requesting support, not a confirmed
  working device — pending their confirmation that the interface now
  binds and associates.

### Fixed
- **`_connect_cmd_done()` had the same unguarded `phl_role` read that 1.17.0
  fixed one level up.** 1.17.0 closed the NULL-`phl_role` race in
  `_connect_msg_hdlr()`'s top-level dispatch, but `_connect_cmd_done()` —
  called from three cases in that same switch (`MSG_EVT_CONNECT_END`,
  `MSG_EVT_DISCONNECT`, and the `send_disconnect` fallback) — re-reads
  `a->phl_role` on its own and dereferences `role->hw_band` with no check
  of its own:
  ```
  BUG: kernel NULL pointer dereference, address: 000000000000001e
  RIP: _connect_cmd_done+0x47/0x90 [8852au]
  ```
  Same hazard as before: `rtw_hw_iface_deinit()` frees the role and clears
  `phl_role` from `netdev_close()` with no lock shared with the connect
  dispatcher thread, so a queued connect-module message can still be
  in flight against a role that was just freed. Matches the trigger and
  hardware from [#52](https://github.com/WimLee115/rtl8852au-build/issues/52):
  TP-Link Archer TX35U Plus (`3625:010f`), two failed WPA attempts against a
  phone hotspot on 2.4GHz, WiFi switched off from the network panel
  afterward, kernel `6.8.0-138-generic` — hit again after upgrading to
  1.17.0 expecting the earlier fix to cover it. Now guarded the same way as
  the rest of the switch: skip `rtw_phl_free_cmd_token()` and log instead of
  dereferencing a NULL role, still clearing `connect_token`/`connect_state`
  so the adapter doesn't get stuck (`core/rtw_mlme.c`). Build-verified clean
  against Linux `7.1.5+kali-amd64` headers, and now field-verified on the
  reporter's own `3625:010f` hardware: a `wpa_supplicant -dd` capture against
  the same phone hotspot shows six consecutive `CTRL-EVENT-ASSOC-REJECT
  status_code=1` attempts against the same BSSID — three times what used to
  crash the kernel — with no `BUG` in dmesg, confirming the guard holds under
  the exact failure pattern that found the bug. The station-mode
  authentication failure itself is unchanged and remains the open question in
  #52: every attempt is rejected at association, before the 4-way handshake,
  so this is the hotspot declining the STA rather than a PSK/key problem.
  Reading the request-building path (`_issue_assocreq()` in
  `core/rtw_mlme_ext.c`, fed by the HT/VHT/HE/RSN restructuring in
  `rtw_joinbss_cmd()`, `core/rtw_cmd.c`) found no malformed-IE cause — both
  build the STA's own capability elements from local hardware state rather
  than echoing the AP's, so the next step is an over-the-air capture of the
  actual association exchange, which `wpa_supplicant`'s log can't show on its
  own.

## [1.17.0] — 2026-08-29

Extends kernel compatibility on top of `1.16.1`: kernel 7.1 support, two
more MLME/HAL crash fixes, and CI hardened against silent failures.

### Added
- **Every CI job now carries an explicit `timeout-minutes`** — 20 for the
  distro build matrix, 25 for `build-mainline`, 20 for the DKMS dry-run,
  and 10 for the Python job and both Pages jobs. GitHub's default is six
  hours, and a run on `main` showed what that costs: `Install build
  dependencies` sat for 22 minutes on an `apt-get update` retrying an
  unreachable `azure.archive.ubuntu.com` mirror, against a normal job time
  of under two minutes. Weekly scheduled runs make that worse — nobody is
  watching a Monday-morning build, so a hung job would hold a runner slot
  most of the day before the default fired. Each limit is roughly ten times
  the observed runtime, so ordinary mirror slowness still passes.
- **CI runs weekly on a schedule** (Mondays, 05:17 UTC) in addition to push
  and pull-request triggers. The `build-mainline` job resolves the newest
  kernel.org stable and longterm releases at run time, so what it tests moves
  on its own — on a push-only trigger a quiet week produced no signal at all,
  and a new LTS that broke the build would sit undetected until the next
  commit. Monday because Linus cuts releases on Sunday; off the hour because
  scheduled runs cluster and get delayed at `:00`.

### Changed
- **Both READMEs and the project site now say kernel 7.1 builds.** The
  kernel badge, compatibility table and CI notes moved from "verified up to
  7.0.12, 7.1 does not build" to "verified up to 7.1.5" now that the
  cfg80211/pppoe fix above closes the two blockers that actually hit that
  kernel. The remaining two blockers (`strncpy`, the dropped wiphy flag)
  are reattributed to "somewhere between 7.1.0 and 7.2" instead of being
  listed as reasons 7.1 fails, since neither reproduced on 7.1.5.
- **`0bda:8832` (Realtek RTL8832AU reference board) moves from
  Recognised to Tested (reported)** in the supported-devices table.
  The reporter in
  [#43](https://github.com/WimLee115/rtl8852au-build/issues/43) ran the
  full suite on a DKMS install under kernel `7.0.12+kali-amd64` — 30
  tests, 27 passed, 0 failed — and confirmed association and monitor
  mode on the device. The status carries a *(reported)* suffix, and the
  legend in both READMEs and on the landing page now says what that
  means: the verification comes from the person who filed the hardware
  request, with the evidence in their issue, rather than from the
  maintainer on hardware in hand. Without that distinction *Tested*
  would quietly claim more than the project can vouch for.
- **`build-mainline` now records the kernel it resolved** in the job summary,
  on success as well as failure. A bare green tick did not say which version
  was actually tested, which is precisely the question a scheduled run raises.
- **Both READMEs now say what actually blocks kernel 7.x.** They named the
  cfg80211 callback refactor as the sole reason 7.1 does not build, and pinned
  the expected newest-stable failure to 7.1. A probe against 7.2 found four
  independent blockers rather than one — the cfg80211 refactor, the removal of
  `strncpy`, the reworked pppoe structs behind `CONFIG_RTW_BR_EXT`, and a
  dropped wiphy flag — and the newest stable has since moved on to 7.2, so the
  version-pinned wording was going stale on its own. The build claim now reads
  "7.1 and newer", and the CI note is phrased against the outstanding port
  rather than one release.
- **The DKMS dry-run no longer waits on the build matrix.** It shares no
  artefact with those jobs — `dkms-install.sh` strips `*.ko` and `*.o` out of
  the tree it copies, and `dkms build` compiles from source — so `needs: build`
  only ever ordered them. The cost was real: a job skipped because its `needs`
  went unmet reports *success*, and `DKMS scripts dry-run` is a required check,
  so a single stalled Ubuntu mirror in one build leg turned a required check
  green without running it. It also gated the repository's only `shellcheck`
  run behind an apt step on a different runner.

### Fixed
- **Kernel 7.1.0 broke the cfg80211 station/key callbacks and the pppoe
  bridge-extension code.** Nine `cfg80211_ops` callbacks (`add_key`,
  `get_key`, `del_key`, `set_default_mgmt_key`, `get_station`,
  `add_station`, `del_station`, `change_station`, `dump_station`) and the
  three call sites of `cfg80211_new_sta`/`cfg80211_del_sta` switched from a
  `net_device *` to a `struct wireless_dev *` parameter; each is now
  version-gated on `LINUX_VERSION_CODE >= KERNEL_VERSION(7, 1, 0)`, deriving
  `net_device` from `wdev->netdev` so the function bodies stay unchanged
  (`os_dep/linux/ioctl_cfg80211.c`). The same kernel dropped
  `pppoe_hdr.tag`/`pppoe_tag.tag_data` from kernel-visible headers; the two
  direct field accesses in `core/rtw_br_ext.c` are replaced with pointer
  arithmetic on `sizeof(struct pppoe_hdr)` / the existing `TAG_HDR_LEN`
  macro, which is correct on every kernel version because those were always
  flexible array members and never counted toward `sizeof`. Verified with a
  clean build and a real DKMS autoinstall against Linux
  `7.1.5+kali-amd64` headers, and confirmed functionally on that kernel
  against a real RTL8852AU adapter: `tests/run_tests.sh --scan`
  (`TestWiFiScan`, 3/3 — scan trigger, scan results, supported bands), a
  manual monitor-mode cycle (`iw` reports `type monitor`; a `tcpdump`
  capture on the interface showed beacon/RTS/CTS/ACK/BA frames with correct
  radiotap headers and zero kernel-side drops), and the full non-destructive
  suite via the dashboard's *Run tests* control (26/30 passed, 0 failed, 0
  errors; the 4 skips are the expected ones — the two destructive classes
  opting out by default, `TestProcFS` with `CONFIG_PROC_DEBUG=n`, and one
  scan pass that returned no BSS). Of the four blockers a 2026-08-18 probe found
  against 7.2, this closes two; the `strncpy` removal and a dropped wiphy
  flag did not reproduce on 7.1.5, so they sit somewhere between 7.1.0 and
  7.2 — exact boundary still unconfirmed.
- **A stale connect message could crash on a freed `phl_role`.**
  `_connect_msg_hdlr()` read `padapter->phl_role` and immediately
  dereferenced it (`role->hw_band`) before the switch on the message event,
  with no NULL check — a later case in the same switch
  (`MSG_EVT_SWCH_START`) already guarded against a NULL role, so the race
  was known but not closed at this earlier point. Reported in
  [#52](https://github.com/WimLee115/rtl8852au-build/issues/52): TP-Link
  Archer TX35U Plus, two failed WPA attempts followed by turning WiFi off
  from the network panel, kernel `6.8.0-138-generic`. The handler now falls
  through to the existing `send_disconnect` cleanup path, same as every
  other unrecoverable failure it handles (`core/rtw_mlme.c`).
- **The dashboard install instructions failed outright on Debian/Kali.**
  `pip install --require-hashes -r dashboard/requirements.txt` hit
  `error: externally-managed-environment` (PEP 668) on any current
  Debian/Kali Python, which refuses a system-wide `pip install` by
  default. Both READMEs and `docs/dashboard(.nl).md` now create a venv
  first (`python3 -m venv .venv`) and install/run through it; `.venv/` is
  already covered by the blanket `.*` rule in `.gitignore`, so no rule
  needed adding there. Found while live-testing the dashboard after the
  kernel 7.1 fix above.
- **CI no longer hangs on a stalled Ubuntu mirror.** The runners resolve
  archives through a mirrorlist; when the Azure mirror is unreachable, apt
  falls back to `archive.ubuntu.com`, where a connection can stall with the
  response headers received and the body never arriving. apt applies no
  transfer timeout by default, and retries do not help because a stall is not
  an error — so it waits forever. On 2026-08-18 that cost four jobs 20-25
  idle minutes each, in three separate runs, always on the same
  `<suite>-security InRelease` fetch; jobs that reached the Azure mirror in
  those same runs finished in about two minutes. Package installation now
  goes through `.github/scripts/apt-install.sh`, which sets
  `Acquire::http/https::Timeout` (turning a stall into a retryable failure),
  `Acquire::Retries`, and `DPkg::Lock::Timeout` for a runner where
  unattended-upgrades still holds the dpkg lock, with `timeout(1)` plus a
  shared 600-second budget as the backstop. That budget matters beyond speed:
  a job killed by `timeout-minutes` reports `cancelled`, for which GitHub
  sends no failure notification, so a stall on the weekly schedule would have
  passed silently — a failing *step* is a real red X that names apt.
- **The two `curl` downloads in `build-mainline` carry the same protection.**
  `kernel.org/releases.json` and the ~150 MB kernel tarball ran without a
  connect timeout, retry or stall detection, which is the same failure class
  in the job with the largest transfers. Both now use `--retry` with
  `--speed-limit`/`--speed-time`, which aborts a transfer that has gone quiet
  rather than one that is merely slow, and `--retry-max-time` to bound the
  retry sequence. That last part was the catch: `--max-time` applies to a
  single attempt, so `--retry 3 --max-time 900` on the ~150 MB tarball was
  really a 3615-second ceiling — over an hour, against a job limited to 25
  minutes. The stall protection was real; the total was bounded by nothing
  except the job timeout it was written to stay inside.
- **A failed `make` no longer passes the build step.** `make | tee build.log`
  reports tee's exit status, not make's, so the distro matrix relied entirely
  on the `test -f 8852au.ko` that follows — and that only catches failures
  which leave no module behind. `all:` builds `firmware` and `modules` as
  independent goals with no ordering between them, so under `-j` make can fail
  on the firmware step and still link `8852au.ko`, exiting non-zero into a
  green tick. The step now sets `pipefail`, as the mainline job always has.
  `Module metadata` had the same defect from the other direction: `modinfo` on
  a missing or unreadable module exits 0 once piped into `head`, so that step
  could never fail either. It reads through `sed` now, which does not close the
  pipe early and therefore reports modinfo's real status.
- **`hal_bcn_deinit()` freed beacon-pool memory while holding the pool's
  spinlock.** Freeing goes through `_os_mem_free()`, which bottoms out in
  `vfree()` on Linux — not safe to call from atomic context, and holding
  `bcn_pool->bcn_lock` across the loop put every call there. `_os_mem_free()`
  has its own `in_atomic()` guard for exactly this and dumps a stack trace
  when it fires, but the explanatory `RTW_ERR()` line ahead of it compiles
  out in a non-debug build (`CONFIG_RTW_DEBUG=0` is the Makefile default),
  so only the bare trace reached dmesg. It only surfaces when a beacon
  entry is still in the pool at teardown — what a surprise USB removal
  during AP mode leaves behind, since a graceful AP-stop frees the entry
  first via `rtw_free_bcn_entry()`. Reported in
  [#52](https://github.com/WimLee115/rtl8852au-build/issues/52), same
  thread as the connect-crash fix above: TP-Link Archer TX35U Plus, dongle
  hard-unplugged while running as a hotspot, kernel `6.8.0-138-generic`.
  Trace anchored at `hal_bcn_deinit+0xbe/0xc0`, called from
  `rtw_hal_deinit` → `rtw_phl_deinit` → `rtw_hw_deinit` →
  `rtw_dev_remove`. Harmless on that kernel — Ubuntu's generic config
  doesn't enable `CONFIG_DEBUG_ATOMIC_SLEEP` — but freeing vmalloc memory
  under a spinlock is broken regardless of whether a given config catches
  it. Pool entries are now detached from the list under the lock and freed
  after `_os_spinunlock` (`phl/hal_g6/hal_init.c`).

## [1.16.1] — 2026-08-18

A maintenance release on top of `1.16.0`: one monitor-mode kernel panic, three
DKMS packaging faults, and a test suite that reported failures against
perfectly healthy installs.

### Fixed

- **Kernel panic when leaving monitor mode under RX load.**
  `rtw_fill_radiotap_hdr()` runs in softirq from the USB RX tasklet and
  dereferences `padapter->phl_role` for the band, channel and bandwidth
  fields. `netdev_close()` clears that pointer through
  `rtw_hw_iface_deinit()` while the tasklet can still be inside
  `recv_frame_monitor()` — the `netif_running()` guard there is evaluated
  before `skb_copy_expand()`, so it does not cover the radiotap fill that
  follows. The result was a fatal in-interrupt NULL deref (fault address
  `0x4e8` = `chandef.band` in the freed `rtw_wifi_role_t`) after long
  `airodump-ng` captures. The radiotap path now bails out and drops the frame
  when any of `padapter`/`dvobj`/`phl_com`/`phl_role` is NULL, and
  `netdev_close()` skips the disassoc path for a monitor interface, which
  holds no MLME role to disconnect and whose ~700 ms `WAIT_ACK` only widened
  the teardown race. Regression test included.
- **DKMS status checks were racy and matched too loosely.** Both install and
  remove scripts piped `dkms status` into `grep -q`, which closes the pipe on
  its first match; `dkms status` then takes SIGPIPE and exits non-zero, so
  under `set -o pipefail` the whole condition evaluated false. When it lost
  that race the install skipped its cleanup and `dkms add` aborted with
  "DKMS tree already contains". `PACKAGE_VERSION` was also interpolated into
  the regex unescaped, so the dots in a version matched any character. Both
  scripts now let DKMS filter directly (`dkms status -m NAME -v VER`), and the
  module-loaded check tests `/sys/module/<name>` instead of piping `lsmod`.
  Reproduced under `pipefail` with a multi-line status stub: the old form
  matched 0/20 runs, the new form 20/20.
- **DKMS registered under the vendor version.** `dkms.conf` still declared
  `PACKAGE_VERSION` `1.15.0.1` — the Realtek baseline — while the project had
  released `1.16.0` on its own SemVer line, so a fresh install registered
  under the old number. That stale entry was a factor in the install collision
  above.
- **A version bump orphaned the previous DKMS entry.** Both scripts acted only
  on the version `dkms.conf` currently names, so upgrading left the old entry
  registered — and two entries then install the same `8852au.ko` into
  `/updates/dkms` on every kernel upgrade. Worse, `dkms-remove.sh` could no
  longer remove the orphan at all, since the checked-out `dkms.conf` no longer
  matched it. Both scripts now enumerate every registered version of the
  package and clear them, and `dkms-remove.sh` also sweeps the matching
  `/usr/src/<name>-*` trees. The version parser accepts DKMS 2.x and 3.x
  output as well as an "added"-only entry that carries no kernel/arch fields.
- **Kernel-range claims corrected.** Both READMEs advertised "kernel
  6.1 → 7.0+" and claimed CI catches post-6.18 breakage before you hit it.
  Neither held: the newest-stable CI job is non-blocking, and kernel 7.1 does
  not build. The "+" is gone and the 7.1 limitation is named, with "verified
  up to Linux 7.0.12".
- **The test suite no longer fails on a working DKMS install.**
  `tests/test_driver.py` hard-coded the module path to `<repo>/8852au.ko`, so
  anyone who installed with `./dkms-install.sh` — the method the README
  recommends — failed `test_01_module_file_exists`, `test_02_module_info` and
  `test_04_module_srcversion_matches` purely because the module was in
  `/lib/modules/<release>/updates/dkms/` instead, and xz-compressed. The path
  is now resolved at run time: an in-tree build first (so a stale build still
  reports a real srcversion mismatch), then `modinfo -n`, then the DKMS
  directory. `TestModuleReload` picks `insmod` or `modprobe` accordingly,
  since `insmod` cannot load a compressed module.
- **Adapters behind a USB hub are recognised as bound.** `test_01_device_bound`
  matched sysfs entries against `\d+-\d+:\d+\.\d+`, which only covers a device
  on a root port. Behind a hub the port path is dot-separated (`1-8.4:1.0`,
  and `2-1.4.3:1.0` behind chained hubs), so a correctly bound adapter was
  reported as "No USB devices bound to driver". The failure message now also
  lists what the directory actually contained.
- **An empty scan result no longer reports as a failure.**
  `test_02_iw_scan_results` failed whenever no AP was in range. Zero BSSes is
  not evidence of a driver fault — an rfkill block or a shielded room produce
  the same result — so the test now hard-fails only when the scan mechanism
  itself errors, and skips with the reason otherwise.
- Reported in [#43](https://github.com/WimLee115/rtl8852au-build/issues/43),
  where all five failures against a working `0bda:8832` adapter turned out to
  be test-suite artefacts rather than driver faults.

### Added
- `TestSysfsParsing`, a hardware-free test class covering the sysfs and
  module-path parsing above, and a CI step that runs it. Every other class in
  the suite needs a physical adapter, so this logic previously had no
  automated coverage at all.
- `./tests/run_tests.sh --offline` selects that class from the runner — the
  one selection that is meaningful without an adapter or root.

### Removed
- `tools/tapo_rtsp_brute.py` and the whole `tools/` directory. The RTSP
  credential brute-forcer was unrelated to the WiFi driver and out of scope
  for this repository; its CI compile-check, its ruff per-file ignore and its
  entry in the architecture docs are removed along with it.

## [1.16.0] — 2026-08-01

First release under the fork's **own SemVer line**.

> **Versioning note.** Earlier fork tags used the vendor-derived
> `1.15.0.1+N` scheme; the immediate predecessor of this release is
> `1.15.0.1+8` (2026-05-11). Starting here the fork adopts plain
> SemVer, beginning at `1.16.0` — one step above the Realtek
> `1.15.0.1` baseline, so the version keeps climbing from the previous
> tag instead of appearing to roll back. The upstream Realtek baseline
> remains `v1.15.0.1-2`, and every fork change is still tracked in this
> file and exported under [`patches/`](patches/).

### Highlights

- **Builds on kernel 6.1 → 7.0+** — twelve version-gated compatibility
  patches, now continuously built against distro kernels *and* the
  newest kernel.org stable and longterm releases in CI.
- **Stable monitor mode** — four RX-path crash fixes (UBSAN OOB,
  NULL-deref, SKB use-after-free, race/double-free) plus a
  hardware-validated fix for the `rmmod`-while-associated panic.
- **Batteries included** — idempotent DKMS install, a loopback-only
  Flask dashboard with per-host auth, a live-adapter `unittest` suite,
  hash-locked Python deps, firmware-blob checksums, and EN/NL docs.

The entries below are the changes since `1.15.0.1+8`.

### Changed

- **Documented kernel 7.0 support.** The compatibility badge and table now
  advertise the 6.1 → 7.0 range. No driver source changed — the existing
  6.17/6.18 `LINUX_VERSION_CODE` gates already carry the build across the
  7.0 boundary.
- **CI now builds against current mainline kernels.** A new `build-mainline`
  job compiles the module against the latest kernel.org stable and longterm
  releases, resolved at run time (so it tracks 6.19 / 7.0 and beyond without
  edits). Previously CI only exercised the GitHub runner's distro kernel
  (~6.8-6.11), so post-6.18 breakage could reach users unnoticed. The
  `stable` channel is currently informational (non-blocking): kernel 7.1
  refactored a large set of `cfg80211_ops` callbacks from `net_device` to
  `wireless_dev`, which needs a dedicated version-gated port; `longterm`
  (LTS) stays a hard signal.

### Fixed

- **`-Werror=empty-body` on strict (CONFIG_WERROR) kernel trees.** With
  `CONFIG_DBG_COUNTER` off, the `DBG_COUNTER()` macro expanded to nothing,
  leaving empty `if`/`else` bodies (80+ call sites). It now expands to
  `do {} while (0)`. Surfaced by the new mainline CI build; harmless on
  distro headers, which do not build the module with `-Werror`.

### Known limitations

- **Kernel 7.1 is not yet supported.** The `cfg80211_ops` net_device →
  wireless_dev refactor in 7.1 breaks the station/key callbacks. Kernels up
  to and including 7.0 build cleanly. A version-gated port is tracked as
  follow-up work.

### Verified

- **Clean build against Linux 7.0.12+kali-amd64** (Kali `7.0.12-2kali1`,
  2026-06-18, GCC 15.3.0): `make` exits 0 and `8852au.ko` links with BTF
  (vermagic `7.0.12+kali-amd64 SMP preempt mod_unload`). Only the vendor
  tree's usual `-Wmissing-prototypes` warnings, **zero errors, no new
  patches required.** Compile-verified only — not hardware-tested on this
  kernel (no adapter attached to the build host).

- **Patch 0007 (`netdev_close` mutex + skip-on-remove) is now
  hardware-validated** on a TP-Link Archer TX20U Plus (`2357:013f`)
  running on Linux 6.19.14+kali. Concretely:
    - 10× `ip link up/down` cycle @ 200 ms spacing (the exact pattern
      that previously panicked the kernel without the patch): no
      panic, full 5.3 s, system stable.
    - 30× `ip link up/down` cycle @ 50 ms spacing (4× faster than the
      original trigger): no panic, full 6.9 s, module remained loaded.
    - `rmmod 8852au` while the interface was UP: returned in **198 ms**
      with exit 0; previously the disassoc cmd path would block up to
      2 s and panic under load.
    - `insmod ./8852au.ko` reload: 478 ms, `wlan1` re-created with a
      fresh MAC, NetworkManager auto-reconnected to the WPA2 AP at
      780 Mbit/s, -43 dBm. No kernel taint beyond the expected
      out-of-tree / unsigned-module messages.

## [1.15.0.1+8] — 2026-05-11

First tagged release of this fork. Carries the twelve baseline kernel
6.17+ compatibility patches plus eight post-baseline fixes for runtime
bugs, hardware additions, and the security hardening pass below.

### Security
- **Branch protection on `main`.** Required status checks (all four CI
  jobs), force-push and deletion blocked. Maintainer can still merge
  without explicit review because the project is solo-maintained, but
  every push must pass CI.
- **Dashboard now requires HTTP Basic Auth on every endpoint.** Token
  is generated on first run and persisted to
  `~/.config/rtl8852au/dashboard.token` (mode `0600`). Username is
  ignored, password = token. Bind default changed from `0.0.0.0` to
  `127.0.0.1`; `--host 0.0.0.0` is now an explicit opt-in with a
  printed warning.
- **wpa_supplicant.conf injection fix.** `/api/connect` previously
  interpolated `ssid`/`password` raw into the conf file; a crafted SSID
  could inject extra `network={...}` blocks (rogue-AP redirect) or
  override `ctrl_interface`. SSID and passphrase are now validated
  (1–32 bytes / 8–63 chars) and escaped for the quoted-string parser
  before being written.
- **Host-header whitelist on the dashboard.** Defends against
  DNS-rebinding attacks that target the loopback bind from a remote
  tab.
- **wpa_supplicant error stripped from the JSON response.** The
  passphrase could appear in stderr on failure paths; the dashboard now
  returns a generic `"wpa_supplicant failed to start"` and discards
  stderr.
- **Third-party GitHub Actions SHA-pinned.** `actions/checkout@v5.0.0`,
  `actions/setup-python@v6.0.0` and `actions/upload-artifact@v5.0.0`
  are pinned to their commit SHA with a version comment, so a
  supply-chain compromise of the Actions org cannot inject malicious
  code into our CI. This also moves the CI off Node.js 20 (deprecated).
- **Python dependencies hash-locked.** `dashboard/requirements.txt`
  is generated by `pip-compile --generate-hashes` from a new
  `dashboard/requirements.in`. CI installs runtime deps with
  `pip install --require-hashes`, so transitive dependency tampering
  is detected at install time.
- **Firmware blob checksums.** `CHECKSUMS.sha256` lists the SHA256 of
  every firmware `.xz` shipped in the tree; CI verifies it before each
  build (`sha256sum -c CHECKSUMS.sha256`).

### Added
- `LICENSE` file (GNU GPL-2.0 full text).
- `dashboard/requirements.in` (source) plus `dashboard/requirements.txt`
  (`pip-compile --generate-hashes` output, hash-locked).
- `CHECKSUMS.sha256` — SHA256 of firmware blobs, verified in CI.
- Per-user dashboard auth token at `~/.config/rtl8852au/dashboard.token`
  (generated on first run, mode `0600`, survives restarts).
- `dkms-install.sh` and `dkms-remove.sh` helper scripts (idempotent).
- `tests/run_tests.sh` wrapper around the Python test suite, with category flags.
- `tests/__init__.py` so the test module can be imported by `unittest -m`.
- `patches/` directory containing post-baseline fixes as standalone
  `git format-patch` files, plus `patches/README.md`.
- `.github/workflows/ci.yml` — build matrix (Ubuntu 22.04 + 24.04), DKMS dry-run,
  Python lint + offline tests.
- `.github/ISSUE_TEMPLATE/` — structured forms for bug reports and hardware
  support requests.
- `.github/dependabot.yml` — monthly updates for GitHub Actions and pip.
- `ruff.toml` — conservative Python lint config.
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`.
- `tools/README.md` — explicit authorised-testing-only disclaimer for the
  RTSP brute-force tool.

### Changed
- **README rewritten** — removed marketing decoration (capsule renders,
  typing-SVG, animated dividers, decorative badges) in favour of a
  sober factual layout. Compatibility table now distinguishes
  maintainer-verified hardware from CI-build-only matrix entries; no
  more "Working" claims for distros the maintainer has not personally
  exercised. Length: 652 → 374 lines.
- README "Supported Devices" table regenerated from
  `os_dep/linux/usb_intf.c` (the previous list contained USB IDs that were
  not in the driver).
- README "Test Suite" section rewritten to reflect the actual
  `tests/test_driver.py` classes and `tests/run_tests.sh` flags.
- README "Patches Applied" section clarifies that the 12 baseline patches
  are integrated; the `patches/` directory holds post-baseline fixes.
- `.gitignore` no longer ignores `patches/` (was matching quilt's pattern).
- Dashboard `--host` default changed from `0.0.0.0` to `127.0.0.1`.
- CI install steps now use `pip install --require-hashes` against the
  locked `dashboard/requirements.txt`; dev tools (ruff, pyflakes) are
  pinned by major version.

### Fixed
- **Build: kernel 6.17 incompatible-pointer-types (`patches/0008`).**
  The cfg80211 MLO refactor (`radio_idx` on `set_wiphy_params`,
  `set_tx_power`, `get_tx_power`; `struct net_device *` on
  `set_monitor_channel`) landed in 6.17, not 6.18. The four
  `LINUX_VERSION_CODE` guards in `os_dep/linux/ioctl_cfg80211.c` were
  lowered from `>= 6.18` to `>= 6.17` so CI builds on the Ubuntu 24.04
  runner (kernel 6.17.0-1010-azure) no longer fail with
  `incompatible pointer type` for `.set_wiphy_params`, `.set_tx_power`,
  `.get_tx_power` and `.set_monitor_channel` in `rtw_cfg80211_ops`.
- **Build: `tests/test_driver.py` and `dashboard/app.py` ruff lint.**
  Six F541 (`f`-prefixed strings without placeholders) and two B007
  (unused loop variable `i`) findings cleared so the `Ruff (lint)` job
  in CI passes.
- **Driver: kernel panic on rapid `ifup`/`ifdown` and `rmmod`-while-associated
  (`patches/0007`).** `netdev_open()` took `hw_init_mutex` but
  `netdev_close()` did not, so a rapid `ip link up/down` cycle could race
  `rtw_hw_iface_init` against an in-flight `rtw_hw_iface_deinit` on the
  same adapter — a use-after-free of HAL state. In addition,
  `rtw_disassoc_cmd(WAIT_ACK)` blocked the close path for up to 2 s ×
  N cmds while `rtw_dev_remove()` was in progress, leaving the cmd path
  alive while NetworkManager raced against partially-torn-down state.
  Fix: `netdev_close()` now takes `hw_init_mutex` symmetrically, returns
  early if the interface is already down, and skips the disassoc / scan
  cmd path (jumps straight to `rtw_hw_iface_deinit`) when
  `dev_is_surprise_removed()` or `processing_dev_remove` is set.
- **Test suite no longer panics the kernel.** `TestModuleReload` and
  `TestStability` previously issued `rmmod` and 10× rapid ifup/ifdown
  (200 ms cycle) against an actively-associated interface. The 200 ms
  cycle is shorter than the time `netdev_close()` needs to drain
  (`rtw_disassoc_cmd(WAIT_ACK)` ≈ 500 ms + `wait_scan_req_empty(200 ms)`),
  causing stacked close-paths to race against incoming open() calls and a
  concurrent NetworkManager reassociation — a hard kernel panic with no
  written traceback was observed on kernel 6.19.14. Fix:
  - Both destructive classes are now opt-in (`--destructive` /
    `RTW_TEST_DESTRUCTIVE=1`) and refuse to start unless wlan is
    disconnected and NetworkManager / wpa_supplicant are stopped.
  - `TestModuleReload` brings the interface down and waits 2 s before
    `rmmod`, letting `netdev_close()` finish cleanly.
  - `TestStability` toggle cadence raised from 200 ms to 1.5 s per
    half-cycle; scan triggers spaced 2 s apart.
  - `tests/run_tests.sh` adds a shell-level pre-flight that exits 2 with
    instructions if the system is unsafe; new `--reload`, `--stability`,
    `--all` flags make the destructive selection explicit.

## [1.15.0.1] — Baseline

Fork inception. Realtek vendor driver `1.15.0.1-2` with the 12 compile-time
patches required to build on Linux kernel 6.18+:

- `cfg80211-wext-removal` — drop deprecated `wireless_ext` references.
- `netif-rx-timestamp` — `netif_rx` → `netif_rx_any_context`.
- `proc-ops-compat` — `file_operations` → `proc_ops` for /proc entries.
- `ndo-get-stats-removal` — switch to `ndo_get_stats64`.
- `timer-setup-macro` — `init_timer` → `timer_setup`.
- `skb-header-api` — update `skb_*_header()` calls for new API.
- `pci-alloc-consistent` — `pci_alloc_consistent` → DMA API.
- `usb-pipe-macros` — stricter type-checked USB pipe macros for 6.18.
- `access-ok-args` — 2-arg `access_ok()` signature.
- `implicit-fallthrough` — add `fallthrough;` annotations.
- `class-create-api` — drop `owner` arg from `class_create()`.
- `cfg80211-ch-switch` — updated `cfg80211_ch_switch_notify` signature.

### Post-baseline fixes (carried in the `patches/` directory and the tree)
- UBSAN array-out-of-bounds + NULL deref in monitor mode.
- `ethtool` reporting `Speed: unknown` — added `get_link_ksettings`.
- Monitor mode hard freeze: SKB use-after-free in RX path.
- Monitor mode kernel panic under load: race condition + double-free.
- Build fix for kernel 6.8.
- USB ID `3625:010f` for TP-Link Archer TX35U Plus (PR #3, contributor: jsiwrk).
