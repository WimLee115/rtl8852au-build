# rtl8852au-build v1.18.0

**Kernel 7.2 support — and the cfg80211 half of it no longer guesses from a
version number.**

🌐 **Website & docs:** https://wimlee115.github.io/rtl8852au-build/

---

## What's new

### Builds on kernel 7.2

Kernel 7.2 broke the vendor tree three ways:

- **`strncpy()` is gone** from `include/linux/string.h`. Only `strscpy`,
  `strscpy_pad` and the `strtomem` family remain, so every call site failed
  with `implicit declaration of function 'strncpy'`.
- **`WIPHY_FLAG_SUPPORTS_5_10_MHZ` was dropped** from `enum wiphy_flags` —
  its `BIT(22)` is now a hole between `HAS_REMAIN_ON_CHANNEL` and
  `HAS_CHANNEL_SWITCH`.
- **`struct cfg80211_ops.remain_on_channel` gained a trailing
  `const u8 *rx_addr`**, which surfaced as an
  `incompatible pointer type` error on the `rtw_cfg80211_ops` initialiser.

All three are fixed. The initial port came in through
[#55](https://github.com/WimLee115/rtl8852au-build/pull/55), which also
fixed the include paths: kbuild 6.13+ leaves `$(src)` relative for
out-of-tree modules, so `-I$(src)/include` resolved against the kernel tree
and missed `drv_types.h`.

### The cfg80211 fixes ask the kernel, not its version number

[#58](https://github.com/WimLee115/rtl8852au-build/issues/58) established —
over three attempts, in this same file — that `LINUX_VERSION_CODE` is not a
usable signal for a `cfg80211` change. Distros backport individual
`cfg80211_ops` signature changes into kernels whose version macro never
moves with them, and no numeric threshold separates kernels that need
opposite prototypes: jammy's `linux-azure` `6.8.0-1064` reports the
*identical* `LINUX_VERSION_CODE` as noble's `6.8.0-147` and a *higher*
Ubuntu ABI, yet wants the older arity.

`remain_on_channel` is exactly that kind of change, so it uses the same
compile-time type probe #58 settled on — `__typeof__` on a NULL-cast member
access to read the kernel's own declared type for the member,
`__builtin_types_compatible_p()` to compare it, and
`__builtin_choose_expr()` to pick which of two thin shims is referenced.
`rx_addr` is accepted and dropped: the request goes to
`rtw_phl_remain_on_ch_cmd()`, which has no per-request RX address, so
behaviour is unchanged from a pre-7.2 kernel.

`WIPHY_FLAG_SUPPORTS_5_10_MHZ` can't use that trick — it's an enumerator,
invisible to the preprocessor, so `#ifdef` cannot see it and there is no
type to compare. The top-level `Makefile` greps the kernel's real
`include/net/cfg80211.h` instead, matching only the enumerator's
*definition* (`NAME =`) so the kerneldoc line above the enum (`@NAME: ...`)
cannot produce a false positive. If the header can't be located the flag
stays undefined: losing a monitor-mode debugging nicety is recoverable,
naming a removed enumerator is not.

`strncpy()` keeps its version gate. It is a tree-wide API removal, not the
kind of isolated signature change a stable series backports.

### New USB IDs

- **`3625:010d` — TP-Link Archer TX30U Plus.** Enumerates first as a
  Realtek mass-storage "DISK" (`0bda:1a2b`), then re-enumerates as
  `3625:010d`. Marked **Tested** (reported): binds, associates to a WPA2
  5 GHz AP, ~205 Mbit/s over USB 3 with `rtw_switch_usb_mode=1`.
- **`2357:012e` — TP-Link Archer TX20U.** Marked **Recognised** rather
  than Tested; reported in
  [#53](https://github.com/WimLee115/rtl8852au-build/issues/53) as
  untested hardware requesting support.

## What's fixed

### `rtw_dev_remove()` crashed on a surprise USB removal while associated

Teardown still called `rtw_disassoc_cmd()`. With the adapter already gone
the firmware is unreachable, and `rtw_disconnect_cmd()` dereferenced a NULL
`phl_role` — an oops at `RIP: rtw_disconnect_cmd` with interrupts off. The
disassoc path is now skipped on surprise-remove, the way `netdev_close()`
already did it, and bails out if the role is NULL
([#59](https://github.com/WimLee115/rtl8852au-build/pull/59)).

### `_connect_cmd_done()` had the same unguarded `phl_role` read 1.17.0 fixed one level up

1.17.0 closed the NULL-`phl_role` race in `_connect_msg_hdlr()`'s
top-level dispatch; `_connect_cmd_done()` carried the identical unchecked
dereference and is now guarded the same way.

## Verification

Built against the installed `linux-headers-7.2.15+kali-amd64` and
`linux-headers-7.1.5+kali-amd64` packages — each produces a clean
`8852au.ko`, with the `Makefile` probe reporting the enumerator present on
7.1.5 and absent on 7.2.15, i.e. both directions exercised against real
kernels rather than inferred from a changelog.

The type probe was also confirmed to be load-bearing rather than passing by
accident: inverting it reproduces the reported 7.2 error exactly —

```
error: initialization of 'int (*)(struct wiphy *, struct wireless_dev *,
struct ieee80211_channel *, unsigned int, u64 *, const u8 *)' from
incompatible pointer type 's32 (*)(struct wiphy *, struct wireless_dev *,
struct ieee80211_channel *, unsigned int, u64 *)'
```

## Credits

[pablobascunana](https://github.com/pablobascunana) — the kernel 7.2 port
and kbuild include-path fix in [#55](https://github.com/WimLee115/rtl8852au-build/pull/55).

Reporters on [#53](https://github.com/WimLee115/rtl8852au-build/issues/53),
[#58](https://github.com/WimLee115/rtl8852au-build/issues/58) and
[#61](https://github.com/WimLee115/rtl8852au-build/pull/61) for the device
IDs and build logs behind the fixes above.

---

**Disclaimer.** Independent community fork — not affiliated with, endorsed by, or sponsored by Realtek Semiconductor Corp. or any hardware vendor named here. Released under the **GNU GPL-2.0**, provided "AS IS" without warranty of any kind.
