#!/usr/bin/env bash
# Schedule King - one command to set up and run everything.
#
#   ./run.sh               set up (first time only) and launch the app
#   ./run.sh --sample      launch with the bundled sample catalog loaded
#   ./run.sh test          run the full test suite (headless)
#   ./run.sh screenshots   regenerate docs/screenshots
#   ./run.sh setup         only create/update the virtual environment
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$ROOT/Schedule-King"
VENV="$APP_DIR/.venv"
PY="$VENV/bin/python"
STAMP="$VENV/.requirements.sha"

info()  { printf '\033[1;35m▸\033[0m %s\n' "$*"; }
fail()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

find_python() {
    for candidate in python3.12 python3.11 python3.10 python3.9 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 &&
           "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

requirements_hash() {
    cat "$APP_DIR/requirements.txt" | shasum | cut -d' ' -f1
}

setup() {
    if [ ! -x "$PY" ]; then
        local base
        base="$(find_python)" || fail "Python 3.8+ is required. Install it from https://www.python.org/downloads/"
        info "Creating virtual environment with $("$base" --version)"
        "$base" -m venv "$VENV"
    fi
    if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP")" != "$(requirements_hash)" ]; then
        info "Installing dependencies (first run only - this can take a minute)"
        "$PY" -m pip install --quiet --upgrade pip
        "$PY" -m pip install --quiet -r "$APP_DIR/requirements.txt"
        requirements_hash > "$STAMP"
    fi
    # iCloud-synced folders on macOS can mark venv files as hidden, which stops
    # Qt from finding its plugins. Clearing the flag is cheap and safe.
    if [ "$(uname)" = "Darwin" ]; then
        chflags -R nohidden "$VENV" 2>/dev/null || true
    fi
}

cmd="${1:-run}"
case "$cmd" in
    setup)
        setup
        info "Environment ready: $VENV"
        ;;
    test|tests)
        shift
        setup
        info "Running tests"
        cd "$APP_DIR" && QT_QPA_PLATFORM=offscreen "$PY" -m pytest -q -p no:cacheprovider "$@"
        ;;
    screenshots)
        setup
        info "Rendering screenshots to docs/screenshots"
        cd "$APP_DIR" && "$PY" tools/take_screenshots.py "$ROOT/docs/screenshots"
        ;;
    -h|--help|help)
        sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
        ;;
    run|--*)
        [ "$cmd" = "run" ] && [ $# -gt 0 ] && shift
        setup
        info "Launching Schedule King"
        cd "$APP_DIR" && exec "$PY" main.py "$@"
        ;;
    *)
        fail "Unknown command '$cmd' (try ./run.sh --help)"
        ;;
esac
