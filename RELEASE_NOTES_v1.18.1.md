# rtl8852au-build v1.18.1

**Security release: three vulnerabilities, all shipped since `v1.15.0.1+8`
— one of them a root command execution reachable from radio range through
the dashboard.**

🌐 **Website & docs:** https://wimlee115.github.io/rtl8852au-build/

---

## Upgrade

```bash
cd rtl8852au-build
git pull
sudo ./dkms-install.sh     # rebuilds the module and replaces the /usr/src tree
```

Restart the dashboard if you run it. Then check each item below — the
checks are also in [`SECURITY.md`](SECURITY.md#published-advisories):

```bash
# DKMS tree: should print nothing
find /usr/src/rtl8852au-* \( ! -user root -o -perm /022 \) -print -quit
# Dashboard: should print nothing; an install/remove/softdep line is a compromise
grep -vE '^(#|options 8852au |$)' /etc/modprobe.d/8852au.conf
```

If either check prints something, or the machine may have run untrusted
code as the user who owns the checkout, don't trust the old tree or the
checkout: remove the driver with `sudo ./dkms-remove.sh`, delete any line
you did not write from `/etc/modprobe.d/8852au.conf`, clone fresh and
reinstall.

## What's fixed

### Dashboard: an SSID could get a command run as root

CVSS 3.1 **8.8 (High)** — `AV:A/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H`; CWE-79,
CWE-93. Dashboard users only.

Two flaws that chain. `app.js` built its tables by putting server data
into `innerHTML` unescaped — including SSIDs from scans and from
monitor-mode frames, text that any transmitter in range chooses, the SSID
of the connected network, and the USB product string, which the device
reports about itself. A 32-byte SSID is enough for
`<img src=x onerror=…>`, and script running in the dashboard runs with its
credentials.

The second flaw makes that root. `/api/advanced` validated number and
select parameters but passed `rtw_country_code`, a free-text field,
straight into `/etc/modprobe.d/8852au.conf`. A newline in it appended a
line of its own, and modprobe executes an `install 8852au <command>` line
as root on the next load of the module — which `/api/advanced/reload`
performs. Against 1.18.0, posting `NL` followed by a newline and an
`install` directive produced exactly that file:

```
options 8852au rtw_country_code=NL
install 8852au /bin/sh -c 'id > /tmp/pwned'
```

Fixed on both sides:

- every server value is escaped before it reaches the page (`esc()`), and
  the quick-connect button carries its SSID in a `data-` attribute rather
  than inside an inline `onclick` string;
- `rtw_country_code` must be two letters or digits; a text parameter
  without a declared pattern is rejected; numbers are written in canonical
  form, since `int()` happily accepts `" 36\n"`; and
  `write_modprobe_conf()` drops any value — new or already in the file —
  that is not a single safe token.

The dashboard also had **no CSRF defence**: the browser attaches HTTP
Basic credentials on its own, so any website could make it POST here —
disconnect Wi-Fi, toggle monitor mode, reload the module, run the tests.
State-changing requests whose `Origin` or `Sec-Fetch-Site` names another
origin are now refused, and every response carries
`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
`Referrer-Policy: no-referrer` and a CSP against framing, `<base>`,
`<object>` and foreign form targets.

### Driver: any local user could drive the private ioctls

CVSS 3.1 **6.6 (Medium)** — `AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H`;
CWE-862. Every release; the gap is in the vendor code this fork started
from.

The kernel performs no capability check for `SIOCDEVPRIVATE` — that is
the driver's job — and `rtw_ioctl()` did none. So an unprivileged user
could reach the vendor private-command table (MAC and RF register writes
via `write`, `rfw` and `phl_set_io`; the channel plan) and the Android
command set (`COUNTRY`, `STOP`). `rtw_ioctl()` now requires
`CAP_NET_ADMIN`. If you used `iwpriv` or these ioctls as a normal user,
use `sudo` now.

### `dkms-install.sh` left a root-executed tree writable by a normal user

CVSS 3.1 **7.3 (High)** — `AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H`; CWE-732.
Everyone who installed with `sudo ./dkms-install.sh`.

The script runs as root and copies the checkout to
`/usr/src/<name>-<version>` with `tar -c | tar -x`. A root-run `tar -x`
restores the owner recorded in the archive, so the copy kept the uid of
whoever owned the checkout — normally the user who cloned it and then ran
the script with `sudo` — and its `664`/`775` modes.

That tree is not inert. DKMS rebuilds it as root on every kernel upgrade,
unattended: it sources `dkms.conf` as a shell script and runs `make` in
it. So that user — or anything running as them: a package install hook, a
browser exploit, a script from a CTF — could rewrite `dkms.conf` or the
source and have root execute it at the next kernel upgrade without ever
knowing the sudo password; with the DKMS MOK key enrolled for Secure Boot,
DKMS would sign the result too.

The extract now runs with `--no-same-owner --no-same-permissions`;
`chown -R root:root` and `chmod -R u-s,g-s,go-w` then pin the result down
whatever root's umask is; and the install refuses a tree that contains a
symlink, since a link back into a user-writable directory would reopen the
same hole. That check runs on the copy, not the checkout, so a link slipped
in between a check and the copy is still caught.

Installing still needs root, exactly as before — `dkms add/build/install`
and `modprobe` are root's job. What changed is who can *modify* the tree
afterwards: only root.

### Also in this release

- **Hardening:** `CONFIG_PROC_DEBUG` proc entries are created `0600`
  instead of the vendor's `0666`. In a debug build, `write_reg` would let
  any local user write registers and `sec_cam` would show them the live
  Wi-Fi keys. Default builds create no proc entries, and debug builds do
  not currently compile, so no released module exposed them.
- `MOK.priv` and `MOK.der`, which `make sign` writes into the tree, are
  git-ignored: committing `MOK.priv` would let anyone sign modules your
  firmware trusts.
- **Fixed:** `suspend_rtw8852au` compared with `==`, which `dash` —
  `/bin/sh` on Debian and Ubuntu — rejects as an unexpected operator, so
  the sleep hook never unloaded or reloaded the module there.

## Verification

- **Each flaw reproduced before it was fixed.** The DKMS script's own copy
  block, run under `fakeroot -u` against a user-owned checkout, produced
  948 entries owned by that user and group-writable, with `dkms.conf` at
  `user:user 664` — the same as a real 1.18.0 install on Kali. The
  modprobe injection was driven through the 1.18.0 dashboard and wrote the
  `install` line shown above.
- **The fixes, against the same inputs.** The copy block now yields 0
  non-root and 0 group- or world-writable entries, `dkms.conf` at
  `root:root 644`; a planted set-id bit is stripped and a tree containing a
  symlink is refused. The dashboard writes nothing for the injection
  payload, and `esc()` neutralises tag, attribute and quote-breaking
  payloads.
- **Regression tests.** `tests/test_dashboard.py` — 13 offline tests
  through Flask's test client, run by CI — passes; 9 of them fail against
  1.18.0. The `DKMS scripts dry-run` job now fails if anything under the
  installed tree is not owned by `root:root`, is writable by group or
  other, or is a symlink; the runner's checkout is not root's, so the old
  script would trip it.
- **Builds.** The module builds cleanly with the `CAP_NET_ADMIN` check
  against `linux-headers-7.2.15+kali-amd64`; CI covers the other kernels.
  The sleep hook was checked under `dash`.

## Credits

Found in a security review of the maintainer's own install.

---

**Disclaimer.** Independent community fork — not affiliated with, endorsed by, or sponsored by Realtek Semiconductor Corp. or any hardware vendor named here. Released under the **GNU GPL-2.0**, provided "AS IS" without warranty of any kind.
