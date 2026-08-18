#!/usr/bin/env bash
#
# Hardened apt-get for CI: update + install, with timeouts and retries.
#
# Why this exists: the hosted runners resolve archives through a mirrorlist.
# When the Azure mirror is unreachable, apt falls back to archive.ubuntu.com --
# and a connection there can stall with the response headers already received
# and the body never arriving. apt applies no transfer timeout by default, so
# it waits forever. Retries alone do not help either: a stall is not an error,
# so apt never retries it.
#
# On 2026-08-18 that cost four jobs 20-25 idle minutes each (runs 32156628064,
# 32160272125, 32161189076). The last line in every one of those logs is an
# ordinary-looking `Get:5 ... -security InRelease`.
#
# Three layers of defence, cheapest first:
#   1. Acquire::*::Timeout turns a stalled socket into an ordinary failure,
#      which Acquire::Retries then retries internally without leaving the run.
#   2. DPkg::Lock::Timeout rides out unattended-upgrades still holding the dpkg
#      lock on a freshly booted runner, instead of failing on the spot.
#   3. The outer `timeout` plus retry loop is the backstop for what those two
#      miss: a mirror that is slow rather than dead, or a hang inside dpkg.
#
# The whole thing is bounded by one shared budget, because a job killed by
# `timeout-minutes` reports `cancelled` -- which sends no failure notification
# and reads like someone pressed Cancel. Failing the step inside the budget
# turns the same stall into a real red X that names apt.
#
# Usage: .github/scripts/apt-install.sh <package>...
#
# SPDX-License-Identifier: GPL-2.0

set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "usage: $0 <package>..." >&2
    exit 2
fi

# Budget for this script as a whole. Sized to fail loudly well inside the
# tightest apt-using job timeout (20 minutes) with room to spare for the build
# that follows.
TOTAL_BUDGET="${APT_TOTAL_BUDGET:-600}"

# Per-attempt ceilings. Healthy runs finish update+install in 9-135s, so these
# leave several times the observed worst case before anything is killed.
UPDATE_TIMEOUT="${APT_UPDATE_TIMEOUT:-120}"
INSTALL_TIMEOUT="${APT_INSTALL_TIMEOUT:-300}"

ATTEMPTS="${APT_ATTEMPTS:-3}"

export DEBIAN_FRONTEND=noninteractive

# $1 is the wall-clock ceiling for this attempt; the rest is the apt-get
# command line.
apt_get() {
    local cap="$1"
    shift

    sudo timeout --signal=INT --kill-after=30s "$cap" \
        apt-get \
        -o Acquire::Retries=3 \
        -o Acquire::http::Timeout=20 \
        -o Acquire::https::Timeout=20 \
        -o DPkg::Lock::Timeout=60 \
        "$@"
}

# Runs one apt-get sub-command with retries: retry_apt_get <sub-command>
# <per-attempt timeout> [extra args...]
retry_apt_get() {
    local action="$1"
    local cap="$2"
    shift 2

    local attempt rc left this_cap

    for ((attempt = 1; attempt <= ATTEMPTS; attempt++)); do
        left=$((TOTAL_BUDGET - SECONDS))
        if [[ $left -lt 30 ]]; then
            echo "::error::apt-get $action exhausted the ${TOTAL_BUDGET}s budget for installing packages"
            return 124
        fi

        # Never let one attempt overrun what is left of the shared budget.
        this_cap=$cap
        if [[ $this_cap -gt $left ]]; then
            this_cap=$left
        fi

        rc=0
        apt_get "$this_cap" "$action" "$@" || rc=$?

        if [[ $rc -eq 0 ]]; then
            return 0
        fi

        if [[ $attempt -eq $ATTEMPTS ]]; then
            echo "::error::apt-get $action failed after $ATTEMPTS attempts (exit $rc)"
            return "$rc"
        fi

        # 124 is `timeout` reporting that it had to kill apt: the stall case.
        if [[ $rc -eq 124 ]]; then
            echo "::warning::apt-get $action stalled and was killed after ${this_cap}s (attempt $attempt/$ATTEMPTS); retrying"
        else
            echo "::warning::apt-get $action failed with exit $rc (attempt $attempt/$ATTEMPTS); retrying"
        fi

        sleep $((attempt * 10))
    done
}

retry_apt_get update "$UPDATE_TIMEOUT"
retry_apt_get install "$INSTALL_TIMEOUT" -y "$@"
