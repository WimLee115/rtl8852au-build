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
  unvalidated paths.

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
