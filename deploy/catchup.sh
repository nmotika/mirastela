#!/bin/bash
# One-off e-mail with the new summary for older leads. Run as root:
#   /opt/mirastela/deploy/catchup.sh count | preview [N] [LANG] | send [LIMIT]
set -a; . /etc/mirastela.env; set +a
cd /opt/mirastela/api && sudo -E -u mirastela /opt/mirastela/.venv/bin/python catchup.py "$@"
