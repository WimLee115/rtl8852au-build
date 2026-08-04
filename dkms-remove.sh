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

echo "==> Removing ${PKG_NAME} ${PKG_VER}"

# A loaded module always has a /sys/module/<name> directory; check that
# instead of `lsmod | grep -qw`, which has the same SIGPIPE-under-pipefail
# race as the dkms-status check below.
if [[ -n "$MOD_NAME" && -d "/sys/module/${MOD_NAME}" ]]; then
    echo "==> Unloading ${MOD_NAME}"
    modprobe -r "$MOD_NAME" || rmmod "$MOD_NAME" || true
fi

# Filter by name+version directly rather than piping `dkms status` into
# `grep -q`; see the note in dkms-install.sh for why that pipeline was
# unreliable (grep closing the pipe trips `set -o pipefail`, and the version
# was an unescaped regex).
if [[ -n "$(dkms status -m "${PKG_NAME}" -v "${PKG_VER}" 2>/dev/null || true)" ]]; then
    echo "==> dkms remove"
    dkms remove -m "${PKG_NAME}" -v "${PKG_VER}" --all || true
fi

if [[ -d "$SRC_DIR" ]]; then
    echo "==> Removing ${SRC_DIR}"
    rm -rf "$SRC_DIR"
fi

depmod -a

echo "Done."
