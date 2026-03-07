#!/bin/bash

if systemctl is-enabled photonvision >/dev/null 2>&1; then
	echo "Stopping Photonvision"
	sudo systemctl stop photonvision
	sudo systemctl disable photonvision
	echo "Starting Rpivision"
	sudo systemctl enable rpivision
	sudo systemctl start rpivision
else
	echo "Stopping Rpivision :("
	sudo systemctl stop rpivision
	sudo systemctl disable rpivision
	echo "Starting Photonvision"
	sudo systemctl start photonvision
	sudo systemctl enable photonvision
fi
