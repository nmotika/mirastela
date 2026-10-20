#!/bin/bash
# Pull the latest code and restart the API. Run as root: /opt/mirastela/deploy/update.sh
set -euo pipefail
cd /opt/mirastela
sudo -u mirastela git pull --ff-only
# System libraries for the PDF reports (WeasyPrint), installed once.
# ffmpeg for the social media reels.
dpkg -s libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 ffmpeg >/dev/null 2>&1 || \
  { apt-get update -q && DEBIAN_FRONTEND=noninteractive apt-get install -y -q libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 ffmpeg >/dev/null; }
sudo -u mirastela /opt/mirastela/.venv/bin/pip install -q -r api/requirements.txt
cp deploy/mirastela-api.service deploy/mirastela-daily.service deploy/mirastela-daily.timer deploy/mirastela-pages.service deploy/mirastela-pages.timer \
   deploy/mirastela-backup.service deploy/mirastela-backup.timer \
   deploy/mirastela-social-morning.service deploy/mirastela-social-morning.timer \
   deploy/mirastela-social-evening.service deploy/mirastela-social-evening.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now mirastela-daily.timer mirastela-pages.timer mirastela-backup.timer \
  mirastela-social-morning.timer mirastela-social-evening.timer >/dev/null
install -d -o mirastela -g mirastela /var/lib/mirastela/social
systemctl restart mirastela-api
sleep 3 && curl -fsS http://127.0.0.1:8000/api/health && echo " OK"
# Generate today's horoscopes now if they are missing (runs in the background).
systemctl start --no-block mirastela-pages.service
