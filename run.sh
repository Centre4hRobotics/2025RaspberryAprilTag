#!/bin/bash

cleanup() {
    local exit_code=$?

    echo "Running cleanup"

    rm "$(dirname $0)/camera_lock.lck"

    exit $exit_code
}

trap cleanup EXIT

if [ -f "$(dirname $0)/camera_lock.lck" ]; then
    echo "This program is already running somewhere else!"
    exit 1
fi

touch "$(dirname $0)/camera_lock.lck"
cd $(dirname $0)
./.venv/bin/python3 main.py
