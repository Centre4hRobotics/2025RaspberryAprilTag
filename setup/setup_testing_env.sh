#!/bin/bash
# This project requires Linux

cd "$(dirname $0)/.."

echo "WARNING: This script is supposed to only set up for pytest and not for actual usage!"

# Create python virtual environment
python3 -m venv --system-site-packages .venv
pydir=./.venv/bin/python


# Install required PIP packages

# Install robotpy
# Note: This is likely to error! If it does, resolve the issues manually.
$pydir -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy
$pydir -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy-cscore
$pydir -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy-apriltag

# Install opencv & other packages
$pydir -m pip install opencv-contrib-python-headless
$pydir -m pip install matplotlib

# Install pytest
$pydir -m pip install pytest

echo "Created Virtual Environment. It is located at $pydir"
