# Contributors

**English** | [Nederlands](CONTRIBUTORS.nl.md)

Everyone who has helped make **rtl8852au-build** what it is. This mirrors
the credits in the [README](README.md) and [CHANGELOG](CHANGELOG.md); the
GitHub [contributors graph](https://github.com/WimLee115/rtl8852au-build/graphs/contributors)
is generated automatically from commit history.

## Maintainer

- **[WimLee115](https://github.com/WimLee115)** — fork maintenance, the
  twelve kernel 6.17+ compatibility patches, the kernel 7.1 cfg80211/pppoe
  port, the monitor-mode crash fixes, DKMS packaging, the Flask dashboard,
  the test suite, and CI.

## Contributors

- **[Joan Sala — `jsiwrk`](https://github.com/jsiwrk)** — TP-Link Archer
  TX35U Plus USB ID (`3625:010f`) and the kernel 6.8 build fix
  ([PR #3](https://github.com/WimLee115/rtl8852au-build/pull/3)).
- **[74Thirsty — `gadgetsaavy`](https://github.com/74Thirsty)** — D-Link
  DWA-1850 USB ID (`2001:332c`) and Parrot OS 6/7 testing
  ([PR #14](https://github.com/WimLee115/rtl8852au-build/pull/14)).
- **[Omelug](https://github.com/Omelug)** — hardware report for `0bda:8832`
  on kernel 7.0.12, which surfaced two test-suite bugs: the module path was
  hard-coded to an in-tree build, and adapters behind a USB hub read as
  unbound ([issue #43](https://github.com/WimLee115/rtl8852au-build/issues/43)).
  Re-ran the suite after the fix and confirmed association and monitor mode,
  which is what moved that ID to *Tested (reported)*.
- **[PierreGrillet](https://github.com/PierreGrillet)** — crash reports on
  a TP-Link Archer TX35U Plus that surfaced two driver bugs: a NULL-deref
  in the connect state machine on a stale message after a failed WPA
  attempt, and an atomic-context free in the beacon-pool cleanup on
  surprise USB removal during AP mode
  ([issue #52](https://github.com/WimLee115/rtl8852au-build/issues/52)).

## Acknowledgements

Not commit contributors to this repository, but this fork stands on their
work:

- **Realtek Semiconductor Corp.** — the original vendor driver
  (`v1.15.0.1-2`) this fork is based on.
- **[lwfinger (Larry Finger)](https://github.com/lwfinger)** — long-running
  community Linux packaging of the Realtek WiFi drivers.
- **[morrownr](https://github.com/morrownr)** — USB WiFi adapter
  documentation, USB-ID references, and maintenance patterns.

## Adding yourself

New contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
Open a pull request; once it is merged you appear in the GitHub
contributors graph automatically, and substantial changes are recorded
here and in the README credits.

---

*Bots (e.g. Dependabot) that appear in the commit history are intentionally
excluded from this list.*
