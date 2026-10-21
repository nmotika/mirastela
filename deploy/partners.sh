#!/bin/bash
# Partner (affiliate) report. Run as root: /opt/mirastela/deploy/partners.sh [CODE] [YYYY-MM]
#   no arguments: every partner, totals per month;  CODE YYYY-MM: that partner's payments in that month
set -a; . /etc/mirastela.env; set +a
sudo -u mirastela env MIRASTELA_AFFILIATES="$MIRASTELA_AFFILIATES" MIRASTELA_DB="${MIRASTELA_DB:-/var/lib/mirastela/mirastela.db}" \
  /opt/mirastela/.venv/bin/python /opt/mirastela/api/affiliates.py "$@"
