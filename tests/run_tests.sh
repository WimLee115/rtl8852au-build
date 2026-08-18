#!/usr/bin/env bash
#
# Wrapper around tests/test_driver.py.
# Detects root, runs the Python unittest suite, and surfaces test_report.json.
#
# Usage:
#   sudo ./tests/run_tests.sh                # safe tests only (default)
#        ./tests/run_tests.sh --offline      # parsing tests only (no hardware, no root)
#   sudo ./tests/run_tests.sh --module       # module load + binding (read-only)
#   sudo ./tests/run_tests.sh --interface    # interface up/down + cfg80211
#   sudo ./tests/run_tests.sh --scan         # iw scan trigger + dump
#   sudo ./tests/run_tests.sh --usb          # USB endpoint + speed
#   sudo ./tests/run_tests.sh --dmesg        # check for kernel errors
#   sudo ./tests/run_tests.sh --reload       # *destructive* rmmod/insmod cycle
#   sudo ./tests/run_tests.sh --stability    # *destructive* stress: rapid toggle, scans
#   sudo ./tests/run_tests.sh --all          # everything including destructive
#   sudo ./tests/run_tests.sh --list         # list all test classes
#   sudo ./tests/run_tests.sh -k <pattern>   # forward a unittest-style filter
#
# Destructive tests previously triggered a hard kernel panic when wlan was
# actively associated. The harness now performs a pre-flight check and will
# refuse to start them while NetworkManager runs or the interface is connected.
#
# SPDX-License-Identifier: GPL-2.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_TESTS="${SCRIPT_DIR}/test_driver.py"

if [[ ! -f "$PY_TESTS" ]]; then
    echo "error: $PY_TESTS not found" >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 not found" >&2
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo "warning: not running as root — module-load, monitor-mode and dmesg tests will be skipped."
    echo "         for full coverage, run:  sudo $0 $*"
fi

# Filter pattern (substring matched against class name by test_driver.py -k).
FILTER=""
# Whether to opt in to destructive tests (rmmod, rapid toggle).
DESTRUCTIVE=0

case "${1:-}" in
    --offline)
        # Pure parsing logic — needs neither an adapter nor root, so it is
        # the one selection that is meaningful on any machine (and the one
        # CI runs).
        FILTER="TestSysfsParsing"
        ;;
    --module|--load)
        FILTER="TestModuleBasics TestDeviceBinding"
        ;;
    --reload)
        FILTER="TestModuleReload"
        DESTRUCTIVE=1
        ;;
    --interface|--up)
        FILTER="TestInterfaceUp TestCfg80211"
        ;;
    --scan)
        FILTER="TestWiFiScan"
        ;;
    --stability|--stress)
        FILTER="TestStability"
        DESTRUCTIVE=1
        ;;
    --usb)
        FILTER="TestUSBEndpoints"
        ;;
    --dmesg)
        FILTER="TestDmesgClean"
        ;;
    --all)
        FILTER=""
        DESTRUCTIVE=1
        ;;
    --list)
        echo "Available test classes:"
        grep -E '^class Test' "$PY_TESTS" | sed 's/class /  /; s/(unittest.TestCase)://'
        echo ""
        echo "Destructive (opt-in via --reload / --stability / --all):"
        echo "  TestModuleReload  TestStability"
        exit 0
        ;;
    -k)
        shift
        if [[ $# -eq 0 ]]; then
            echo "error: -k requires a pattern argument" >&2
            exit 1
        fi
        FILTER="$1"
        ;;
    "")
        : # safe default: run everything except destructive classes
        ;;
    -h|--help)
        # Header block only — it ends at the SPDX line, and the previous
        # bound ran five lines past it into the code.
        sed -n '3,24p' "$0"
        exit 0
        ;;
    *)
        echo "error: unknown option '$1' (try --help)" >&2
        exit 1
        ;;
esac

cd "$(dirname "$SCRIPT_DIR")"

DESTRUCTIVE_FLAG=""
if [[ $DESTRUCTIVE -eq 1 ]]; then
    echo
    echo "================================================================"
    echo "  DESTRUCTIVE test selection — these can panic the kernel if"
    echo "  the interface is associated to an AP."
    echo "================================================================"

    # Pre-flight: refuse to continue if the system is clearly unsafe.
    if systemctl is-active --quiet NetworkManager 2>/dev/null; then
        echo "  NetworkManager is active; it will fight the driver during the test."
        echo "  Stop it first:  sudo systemctl stop NetworkManager"
        echo "  Then re-run this script."
        exit 2
    fi
    if systemctl is-active --quiet wpa_supplicant 2>/dev/null; then
        echo "  wpa_supplicant is active; stop it:  sudo systemctl stop wpa_supplicant"
        exit 2
    fi
    iface=$(ip -br link show 2>/dev/null \
            | awk '/^wlan[0-9]+/ {print $1; exit}' \
            || true)
    if [[ -n "$iface" ]]; then
        if iw dev "$iface" link 2>/dev/null | grep -q "Connected to"; then
            echo "  $iface is associated to an AP."
            echo "  Bring it down first:  sudo ip link set $iface down"
            exit 2
        fi
    fi

    echo "  Pre-flight passed — proceeding."
    echo
    DESTRUCTIVE_FLAG="--destructive"
fi

if [[ -n "$FILTER" ]]; then
    echo "==> Running filtered tests: $FILTER"
    overall_rc=0
    for cls in $FILTER; do
        echo "---- $cls ----"
        python3 "$PY_TESTS" $DESTRUCTIVE_FLAG -k "$cls" || overall_rc=$?
    done
    exit $overall_rc
else
    echo "==> Running test suite (safe by default — pass --all for destructive too)"
    python3 "$PY_TESTS" $DESTRUCTIVE_FLAG
fi
