"""Data requests by email (GDPR), run on the server:
  sudo -u mirastela /opt/mirastela/.venv/bin/python admin.py export someone@example.com > data.json
  sudo -u mirastela /opt/mirastela/.venv/bin/python admin.py delete someone@example.com
Run from /opt/mirastela/api with the env loaded: see deploy/README.md (or use deploy/data.sh).
"""
from __future__ import annotations

import json
import sys

import app

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("export", "delete"):
        sys.exit(__doc__)
    what, email = sys.argv[1], sys.argv[2]
    if what == "export":
        print(json.dumps(app.export_data(email), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(app.forget(email)))
