 #!/bin/bash

# This script is can only be run on the actual coprocessor itself.
# This project requires Linux

cd "$(dirname $0)"

# Install Picamera2; nessecary for Luma P1 support.
sudo apt install -y python3-picamera2 --no-install-recommends

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

echo "Created Virtual Environment. It is located at $pydir"

# Enable systemd service
sudo cp rpivision.service /etc/systemd/system/
sudo systemctl daemon-reload
echo "Note: if this code isn't run on a photonvision device, the systemd service will need to be modified."
