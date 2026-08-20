#!/bin/bash
# Power Home Gym — startup script

set -e
cd "$(dirname "$0")"

echo "==> تثبيت الحزم المطلوبة..."
/usr/bin/python3 -m pip install -r requirements.txt --break-system-packages || pip3 install -r requirements.txt --break-system-packages || true

echo "==> تشغيل السيرفر..."
exec /usr/bin/python3 app.py
