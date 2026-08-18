#!/usr/bin/env bash
#
# DKMS removal script for the rtl8852au driver.
#
# Unloads the module, removes the DKMS registration, and deletes the
# /usr/src tree. Safe to re-run.
#
# SPDX-License-Identifier: GPL-2.0

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "error: this script must be run as root (try: sudo $0)" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f dkms.conf ]]; then
    echo "error: dkms.conf not found in $SCRIPT_DIR" >&2
    exit 1
fi

PKG_NAME="$(awk -F'"' '/^PACKAGE_NAME=/{print $2}' dkms.conf)"
PKG_VER="$(awk -F'"' '/^PACKAGE_VERSION=/{print $2}' dkms.conf)"
MOD_NAME="$(awk -F'"' '/^BUILT_MODULE_NAME\[0\]=/{print $2}' dkms.conf)"

SRC_DIR="/usr/src/${PKG_NAME}-${PKG_VER}"

# See the note in dkms-install.sh: accept either separator, and stop at the
# first comma or colon so an "added"-only entry parses too.
# Trailing `|| true`: this script has no dkms sanity check, and removal is
# best-effort — a missing dkms should not abort the module unload and the
# /usr/src cleanup that follow.
dkms_versions() {
    dkms status -m "$1" 2>/dev/null \
        | sed -n "s|^$1[/,] *\([^,:]*\).*|\1|p" \
        | sort -u || true
}

echo "==> Removing ${PKG_NAME}"

# A loaded module always has a /sys/module/<name> directory; check that
# instead of `lsmod | grep -qw`, which has the same SIGPIPE-under-pipefail
# race as the dkms-status check below.
if [[ -n "$MOD_NAME" && -d "/sys/module/${MOD_NAME}" ]]; then
    echo "==> Unloading ${MOD_NAME}"
    modprobe -r "$MOD_NAME" || rmmod "$MOD_NAME" || true
fi

# Ask DKMS for the list rather than piping `dkms status` into `grep -q`; see
# the note in dkms-install.sh for why that pipeline was unreliable (grep
# closing the pipe trips `set -o pipefail`, and the version was an unescaped
# regex).
#
# Remove every version, not just the one dkms.conf currently names: after a
# version bump the checked-out dkms.conf no longer matches the entry that is
# actually installed, so a name+version match would leave it behind with no
# way to remove it from this script at all.
for ver in $(dkms_versions "${PKG_NAME}"); do
    echo "==> dkms remove ${PKG_NAME}/${ver}"
    dkms remove -m "${PKG_NAME}" -v "${ver}" --all || true
done

for src in "/usr/src/${PKG_NAME}"-*; do
    if [[ -d "$src" ]]; then
        echo "==> Removing ${src}"
        rm -rf "$src"
    fi
done

depmod -a

echo "Done."
