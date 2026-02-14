#!/bin/bash

cd $(dirname $0)

if systemctl is-active --quiet rpivision.service; then
    sudo systemctl restart rpivision.service
else
    ./.venv/bin/python main.py
fi
