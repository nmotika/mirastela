#!/bin/bash
# Write the evergreen SEO pages in every language (Batch API, usually 30-90 minutes) and publish them.
# Run as root: /opt/mirastela/deploy/seo.sh [year] [signs] [compat]   (no argument = all three)
# Follow progress with: journalctl -fu mirastela-seo
set -euo pipefail
cd /opt/mirastela
sudo -u mirastela git pull --ff-only
systemd-run --unit=mirastela-seo --collect -p User=mirastela -p WorkingDirectory=/opt/mirastela/api \
  -p EnvironmentFile=/etc/mirastela.env -E MIRASTELA_PUBLISH=1 \
  /opt/mirastela/.venv/bin/python -u seo_gen.py run "$@"
echo "Started. Progress: journalctl -fu mirastela-seo"
