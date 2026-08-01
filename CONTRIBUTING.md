# Contributing

**English** | [Nederlands](CONTRIBUTING.nl.md)

This fork is maintained by a single developer in his spare time. Contributions
are welcome — please keep them focused and well-described.

## What's in scope

- Compatibility patches for newer Linux kernels (6.20, 6.21, …).
- Bugfixes for monitor mode, USB suspend, and the RX/TX path.
- USB ID additions for adapters confirmed to use the RTL8852AU / RTL8832AU
  chipset.
- Dashboard improvements, additional API endpoints.
- More tests in `tests/test_driver.py`.

## What's not in scope

- Adding support for other Realtek chipsets (RTL8852B / RTL8852C). They have
  separate forks; this one stays focused on RTL8852AU/8832AU.
- Wholesale code reformatting of the vendor source. The driver code follows
  Realtek's original style on purpose — it makes upstream syncing possible.
- Forks of the dashboard for unrelated use cases.

## Bug reports

Use the **bug report** issue template:

- USB ID (`lsusb | grep -i realtek`) and kernel version (`uname -r`).
- `dmesg | grep -iE "8852|rtl"` output.
- Build log if the build fails.
- Whether you can reproduce it in managed mode, monitor mode, or both.

For new hardware, use the **hardware support request** template instead.

## Hardware additions

To add a USB ID, edit `os_dep/linux/usb_intf.c` and place the entry in the
`rtw_usb_id_tbl[]` block under the matching vendor section. The format is:

```c
{USB_DEVICE_AND_INTERFACE_INFO(0xVVVV, 0xPPPP, 0xff, 0xff, 0xff), .driver_info = RTL8852A},
```

In the PR description, include:

- `lsusb -v -d VVVV:PPPP` output (manufacturer + product strings).
- Evidence the device uses the RTL8852AU or RTL8832AU chipset (FCC ID
  lookup, vendor datasheet, dmesg after binding).
- Confirmation that you have tested the change against the device — at
  minimum the driver loads and an interface is created.

## Submitting code changes

1. Fork and create a topic branch.
2. Keep each commit focused on one logical change. For driver patches, prefer
   the format used by the Linux kernel community: a short subject line,
   followed by a paragraph explaining *why* the change is needed.
3. Run the test suite (`sudo ./tests/run_tests.sh`) and confirm `make`
   succeeds on at least one current kernel (6.12 LTS or newer).
4. Open a PR. CI will build on Ubuntu 22.04 + 24.04 and run lint.

Once your PR is merged you appear in the GitHub contributors graph;
substantial contributions are also listed in
[`CONTRIBUTORS.md`](CONTRIBUTORS.md).

### Style

- Driver source: match Realtek's vendor style (tabs, K&R braces, no
  Lindent reformatting).
- Python (`dashboard/`, `tests/`, `tools/`): conservative — must pass
  `ruff check` with the config in `ruff.toml`.
- Shell: must pass `shellcheck`.

## Release process

The maintainer tags releases as SemVer `vMAJOR.MINOR.PATCH` (for
example `v1.16.0`). The CI builds artefacts; once green, a GitHub
release is cut with the changelog entry copy-pasted from `CHANGELOG.md`.
