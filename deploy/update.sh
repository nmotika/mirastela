#!/bin/bash
# Pull the latest code and restart the API. Run as root: /opt/mirastela/deploy/update.sh
set -euo pipefail
cd /opt/mirastela
sudo -u mirastela git pull --ff-only
sudo -u mirastela /opt/mirastela/.venv/bin/pip install -q -r api/requirements.txt
cp deploy/mirastela-api.service deploy/mirastela-daily.service deploy/mirastela-daily.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now mirastela-daily.timer >/dev/null
systemctl restart mirastela-api
sleep 2 && curl -fsS http://127.0.0.1:8000/api/health && echo " OK"
