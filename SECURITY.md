# Security policy

**English** | [Nederlands](SECURITY.nl.md)

## Reporting a vulnerability

If you find a security issue in this driver, the dashboard, or the helper
scripts, please **do not** open a public issue. Email the maintainer
directly:

**almass-only@protonmail.com**

Include:

- A description of the issue and the impact (what can an attacker do?).
- Steps to reproduce.
- The version (commit hash or release tag).
- Your name and a way to credit you in the fix, if you'd like.

A first response will follow within 7 days. Severity is assessed against
the [CVSS 3.1](https://www.first.org/cvss/calculator/3.1) calculator.

Reporters of valid issues are credited in
[`CONTRIBUTORS.md`](CONTRIBUTORS.md) unless they ask to stay anonymous.

## Scope

In scope:

- The kernel module (`8852au.ko`) — privilege escalation, kernel memory
  corruption, denial-of-service via crafted frames in monitor mode.
- The Flask dashboard (`dashboard/app.py`) — command injection,
  unauthenticated access to privileged endpoints, path traversal.
- The DKMS scripts (`dkms-install.sh`, `dkms-remove.sh`) — TOCTOU,
  unvalidated paths, files that root runs later but another user can
  modify.

Out of scope:

- The contents of `tools/`. These are research/CTF tools meant for
  authorised testing on systems you control. They are deliberately not
  hardened against being run against unauthorised targets — see
  `tools/README.md` for the authorised-use policy.
- Bugs in the upstream Realtek vendor source that are unmodified in this
  fork. Report those to Realtek directly.

## Disclosure timeline

- **Day 0** — report received, acknowledged within 48 hours.
- **Day 7** — initial assessment + severity rating.
- **Day 30** — fix landed in a private branch.
- **Day 60** — coordinated public disclosure, CVE requested if applicable.

The maintainer reserves the right to disclose earlier for actively
exploited issues.

## Published advisories

All three were fixed in `v1.18.1` (2026-11-12). Upgrading means: pull,
re-run `sudo ./dkms-install.sh`, and restart the dashboard if you run it.

### Dashboard: SSID markup plus modprobe.d injection gives root from radio range

- **Affected:** the dashboard in `v1.15.0.1+8` through `v1.18.0`, while it
  is running. The driver itself is not involved.
- **Impact:** the web UI rendered SSIDs — from scans, from monitor-mode
  frames, of the connected network — and the USB product string as HTML.
  Script hidden in a broadcast SSID ran in the dashboard with its
  credentials, and `/api/advanced` wrote `rtw_country_code` into
  `/etc/modprobe.d/8852au.conf` unvalidated: a newline in it added an
  `install 8852au <command>` line, which modprobe runs as root on the next
  load (`/api/advanced/reload`). Separately, any website could make the
  browser POST to the dashboard (CSRF).
- **Severity:** CVSS 3.1 8.8 (High),
  `AV:A/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H`; CWE-79, CWE-93.
- **Check:** `grep -vE '^(#|options 8852au |$)' /etc/modprobe.d/8852au.conf`
  — any line it prints was not written by the dashboard; treat an
  `install`, `remove` or `softdep` line there as a compromise.
- **Fix:** upgrade to `v1.18.1` and restart the dashboard.

### Driver: private ioctls reachable without CAP_NET_ADMIN

- **Affected:** every release; the gap is in the vendor code this fork
  started from.
- **Impact:** `rtw_ioctl()` checked no capability, and the kernel leaves
  `SIOCDEVPRIVATE` for drivers to guard, so any local user could write MAC
  and RF registers, change the channel plan and regulatory country, or stop
  the driver through the private and Android command tables.
- **Severity:** CVSS 3.1 6.6 (Medium),
  `AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H`; CWE-862.
- **Fix:** upgrade to `v1.18.1` and reinstall the module.

### DKMS source tree writable by the installing user

- **Affected:** installs made with `dkms-install.sh` from `v1.15.0.1+8`
  through `v1.18.0`. Installs made with `make install` are not affected.
- **Impact:** local privilege escalation to root. The tree under
  `/usr/src/rtl8852au-<version>` kept the owner of the checkout, and DKMS
  rebuilds that tree as root on every kernel upgrade — so that user, or
  anything running as them, could have code executed as root without
  sudo, and, where the DKMS MOK key is enrolled, a signed module loaded.
- **Severity:** CVSS 3.1 7.3 (High),
  `AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H`; CWE-732.
- **Check:**
  `find /usr/src/rtl8852au-* \( ! -user root -o -perm /022 \) -print -quit`
  — any output means the install is affected.
- **Fix:** upgrade to `v1.18.1` and re-run `sudo ./dkms-install.sh`. If
  untrusted code may have run as the checkout's owner, remove the driver
  with `sudo ./dkms-remove.sh` and reinstall from a fresh clone: changing
  the ownership alone keeps whatever was written in the meantime.
- **Details:** [`RELEASE_NOTES_v1.18.1.md`](RELEASE_NOTES_v1.18.1.md).
