#!/bin/bash
# Preview the new free summary for the latest leads (nothing is sent or saved).
# Run as root: /opt/mirastela/deploy/summary-preview.sh [N] [LANG]     e.g. summary-preview.sh 3 hr
set -a; . /etc/mirastela.env; set +a
cd /opt/mirastela/api && sudo -E -u mirastela /opt/mirastela/.venv/bin/python summary_preview.py "$@"
