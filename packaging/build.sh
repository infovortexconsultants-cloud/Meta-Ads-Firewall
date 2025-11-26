#!/usr/bin/env bash
set -euo pipefail
APPNAME=meta-ads-firewall
# Ensure pyinstaller is installed
python3 -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --onefile --name ${APPNAME} meta_ads_firewall/__main__.py
echo 'Built dist/${APPNAME}'
