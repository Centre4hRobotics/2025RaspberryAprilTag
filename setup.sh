 #!/bin/bash

# This script is ARM ONLY!!! It will not work on any x86/RISC-V processor
# This project requires Linux

cd "$(dirname $0)"

# Install Picamera2; nessecary for Luma P1 support.
sudo apt install -y python3-picamera2 --no-install-recommends

# Create python virtual environment
python -m venv --system-site-packages .venv
pydir=./.venv/bin/python

# Install required PIP packages

# Install robotpy
# Note: This is likely to error! If it does, resolve the issues manually.
$pydir -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy
$pydir -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy-cscore
$pydir -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy-apriltag

# Install opencv & other packages
$pydir -m pip install opencv-contrib-python-headless
