# rtl8852au-build v1.17.0

**Kernel 7.1 support, plus two more crash fixes from the same hardware report.**

🌐 **Website & docs:** https://wimlee115.github.io/rtl8852au-build/

---

## What's new

### Builds on kernel 7.1

Kernel 7.1.0 refactored nine `cfg80211_ops` callbacks (`add_key`, `get_key`,
`del_key`, `set_default_mgmt_key`, `get_station`, `add_station`,
`del_station`, `change_station`, `dump_station`) and the
`cfg80211_new_sta`/`cfg80211_del_sta` call sites from a `net_device *`
parameter to `struct wireless_dev *`, and dropped
`pppoe_hdr.tag`/`pppoe_tag.tag_data` from kernel-visible headers, breaking
the `CONFIG_RTW_BR_EXT` bridge-extension code. Both are now version-gated on
`LINUX_VERSION_CODE >= KERNEL_VERSION(7, 1, 0)`.

Verified with a clean build and a real DKMS install against Linux
`7.1.5+kali-amd64`, and confirmed functionally against a physical RTL8852AU
adapter: `tests/run_tests.sh --scan` (3/3), a manual monitor-mode cycle with
a `tcpdump` capture showing correct radiotap headers and zero kernel-side
drops, and the full non-destructive suite via the dashboard (26/30 passed,
4 expected skips).

## What's fixed

Both of the following were surfaced by the same report —
[#52](https://github.com/WimLee115/rtl8852au-build/issues/52), a TP-Link
Archer TX35U Plus on kernel `6.8.0-138-generic`.

### A stale connect message could crash on a freed `phl_role`

`_connect_msg_hdlr()` read `padapter->phl_role` and immediately dereferenced
it (`role->hw_band`) before the switch on the message event, with no NULL
check — reachable when WiFi is switched off while a connect attempt is
still in flight:

```
BUG: kernel NULL pointer dereference, address: 000000000000001e
RIP: _connect_msg_hdlr+0xee/0x3f0 [8852au]
```

The handler now falls through to the existing `send_disconnect` cleanup
path, the same as every other unrecoverable failure it handles.

### Beacon-pool cleanup could free memory while holding a spinlock

`hal_bcn_deinit()` held `bcn_pool->bcn_lock` — a spinlock — while freeing
each leftover beacon-pool entry, and that free bottoms out in `vfree()`,
which isn't safe to call from atomic context:

```
CPU: 7 PID: 427 Comm: kworker/7:2 Tainted: G           OE      6.8.0-138-generic
Call Trace:
 dump_stack_lvl+0x76/0xa0
 hal_bcn_deinit+0xbe/0xc0 [8852au]
 rtw_hal_deinit+0x23/0x120 [8852au]
 rtw_dev_remove+0x10c/0x140 [8852au]
```

It only shows up when a beacon entry is still in the pool at teardown —
what a surprise USB removal during AP mode leaves behind, since a graceful
AP-stop frees the entry first. Harmless on a kernel without
`CONFIG_DEBUG_ATOMIC_SLEEP`, which is why nothing else went wrong here, but
freeing vmalloc memory under a spinlock is broken regardless of whether a
given kernel config catches it. Entries are now detached from the pool
under the lock and freed after it's released.

## Known limitations

Kernel 7.1 is supported as of this release. A follow-up probe against 7.2
found two further blockers that don't reproduce on 7.1.5 — a removed
`strncpy` and a dropped `wiphy` flag — so the exact boundary between the two
is still unconfirmed; tracked as follow-up work.

## Credits

[PierreGrillet](https://github.com/PierreGrillet) — the crash reports and
retesting on issue #52 that surfaced both fixes above.

---

**Disclaimer.** Independent community fork — not affiliated with, endorsed by, or sponsored by Realtek Semiconductor Corp. or any hardware vendor named here. Released under the **GNU GPL-2.0**, provided "AS IS" without warranty of any kind.
