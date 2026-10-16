#!/bin/bash
# Who has done what so far (testers). Run as root: /opt/mirastela/deploy/status.sh
sudo -u mirastela /opt/mirastela/.venv/bin/python /opt/mirastela/api/stats.py
