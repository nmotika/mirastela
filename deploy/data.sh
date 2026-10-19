#!/bin/bash
# GDPR requests by email. Usage (as root):
#   /opt/mirastela/deploy/data.sh export someone@example.com > someone.json
#   /opt/mirastela/deploy/data.sh delete someone@example.com
set -euo pipefail
set -a; . /etc/mirastela.env; set +a
cd /opt/mirastela/api
exec sudo -E -u mirastela /opt/mirastela/.venv/bin/python admin.py "$@"
