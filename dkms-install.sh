#!/usr/bin/env bash
#
# DKMS install script for the rtl8852au out-of-tree driver.
#
# Reads PACKAGE_NAME and PACKAGE_VERSION from dkms.conf and:
#   1. Copies the source tree to /usr/src/<name>-<version>
#   2. Registers, builds, and installs the module via DKMS
#   3. Loads the module with modprobe
#
# Re-running is safe: an existing DKMS entry for the same name+version is
# removed first so the install picks up the current source tree.
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

# Extract package metadata from dkms.conf
PKG_NAME="$(awk -F'"' '/^PACKAGE_NAME=/{print $2}' dkms.conf)"
PKG_VER="$(awk -F'"' '/^PACKAGE_VERSION=/{print $2}' dkms.conf)"
MOD_NAME="$(awk -F'"' '/^BUILT_MODULE_NAME\[0\]=/{print $2}' dkms.conf)"

if [[ -z "$PKG_NAME" || -z "$PKG_VER" ]]; then
    echo "error: could not parse PACKAGE_NAME / PACKAGE_VERSION from dkms.conf" >&2
    exit 1
fi

SRC_DIR="/usr/src/${PKG_NAME}-${PKG_VER}"

# Every version of $1 that DKMS currently knows about, one per line.
#
# `dkms status` prints "name/version, kernel, arch: state" on DKMS 3.x and
# "name, version, kernel, arch: state" on 2.x, and drops the kernel/arch part
# entirely for an entry that is only "added" — so accept either separator and
# stop at the first comma or colon.
dkms_versions() {
    dkms status -m "$1" 2>/dev/null \
        | sed -n "s|^$1[/,] *\([^,:]*\).*|\1|p" \
        | sort -u
}

# Sanity checks for build dependencies
for cmd in dkms make gcc; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "error: '$cmd' not found — install build-essential, dkms, and linux-headers-$(uname -r)" >&2
        exit 1
    fi
done

if [[ ! -d "/lib/modules/$(uname -r)/build" ]]; then
    echo "error: kernel headers for $(uname -r) are missing." >&2
    echo "       on Debian/Ubuntu/Kali: sudo apt install linux-headers-$(uname -r)" >&2
    exit 1
fi

echo "==> Installing ${PKG_NAME} ${PKG_VER} via DKMS"

# Remove every existing registration for this package, at any version.
#
# Ask DKMS for the list instead of piping `dkms status` into `grep -q`. That
# pipeline had two bugs: (1) `grep -q` closes the pipe on its first match,
# sending SIGPIPE to `dkms status`, which under `set -o pipefail` makes the
# whole condition fail — so the stale entry silently survived and the later
# `dkms add` collided with "module/version already in the tree"; (2)
# PACKAGE_VERSION was used unescaped in a regex, so the dots in 1.15.0.1
# matched any character.
#
# Matching on name+version alone was still not enough: on a version bump the
# *previous* version stayed registered, and both entries then install the same
# 8852au.ko into /updates/dkms on every kernel upgrade. Clearing all versions
# makes an upgrade leave exactly one entry behind.
for stale_ver in $(dkms_versions "${PKG_NAME}"); do
    echo "==> Removing existing DKMS entry ${PKG_NAME}/${stale_ver}"
    dkms remove -m "${PKG_NAME}" -v "${stale_ver}" --all || true
    stale_src="/usr/src/${PKG_NAME}-${stale_ver}"
    if [[ -d "$stale_src" && "$stale_src" != "$SRC_DIR" ]]; then
        echo "==> Removing ${stale_src}"
        rm -rf "$stale_src"
    fi
done

echo "==> Copying source to ${SRC_DIR}"
rm -rf "${SRC_DIR}"
mkdir -p "${SRC_DIR}"
# Copy everything except VCS / build artefacts
tar --exclude='./.git' \
    --exclude='./.github' \
    --exclude='./*.ko' \
    --exclude='./*.o' \
    --exclude='./Module.symvers' \
    --exclude='./modules.order' \
    -cf - . | tar -xf - -C "${SRC_DIR}"

echo "==> dkms add"
dkms add -m "${PKG_NAME}" -v "${PKG_VER}"

echo "==> dkms build"
dkms build -m "${PKG_NAME}" -v "${PKG_VER}"

echo "==> dkms install"
dkms install -m "${PKG_NAME}" -v "${PKG_VER}"

echo "==> depmod"
depmod -a

if [[ -n "$MOD_NAME" ]]; then
    echo "==> modprobe ${MOD_NAME}"
    modprobe "${MOD_NAME}" || echo "warning: modprobe ${MOD_NAME} failed — unplug/replug the adapter and try again"
fi

echo
echo "Done. Check status with:  dkms status | grep ${PKG_NAME}"
