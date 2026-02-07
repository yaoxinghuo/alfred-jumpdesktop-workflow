#!/bin/bash

# Try to find python3
if command -v python3 >/dev/null 2>&1; then
    python3 ConnectionSearcher.py "$@"
    exit $?
fi

# Common paths for python3
PATHS=(
    "/usr/local/bin/python3"
    "/opt/homebrew/bin/python3"
    "/usr/bin/python3"
    "${HOME}/.pyenv/shims/python3"
    "${HOME}/anaconda3/bin/python3"
    "${HOME}/miniconda3/bin/python3"
)

for py in "${PATHS[@]}"; do
    if [ -x "$py" ]; then
        "$py" ConnectionSearcher.py "$@"
        exit $?
    fi
done

# Fallback
if command -v python >/dev/null 2>&1; then
    # Check if it looks like python 3
    VER=$(python --version 2>&1)
    if [[ "$VER" == *"Python 3"* ]]; then
        python ConnectionSearcher.py "$@"
        exit $?
    fi
fi

echo "Python 3 not found. Please install Python 3." >&2
exit 1
