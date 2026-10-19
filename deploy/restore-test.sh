#!/bin/bash
# Check that the newest backup can be restored: download from R2 (or take the newest local copy),
# decrypt, unpack into /tmp and count rows. Does not touch the live database.
set -euo pipefail
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
if [ -f /etc/mirastela-backup.env ]; then
  set -a; . /etc/mirastela-backup.env; set +a
  export RCLONE_CONFIG_R2_ACL=${RCLONE_CONFIG_R2_ACL:-private} RCLONE_CONFIG=/dev/null  # R2: private ACL avoids 501 on the first put; no config file needed
  LATEST=$(rclone lsf "r2:$R2_BUCKET/db/" --s3-no-check-bucket | sort | tail -1)
  rclone copy "r2:$R2_BUCKET/db/$LATEST" "$T" --s3-no-check-bucket
  gpg --batch --pinentry-mode loopback --passphrase "$BACKUP_PASSPHRASE" -d -o "$T/db.gz" "$T/$LATEST"
  echo "from R2: $LATEST"
else
  cp "$(ls -1t /var/backups/mirastela/mirastela-*.db.gz | head -1)" "$T/db.gz"
  echo "from local copy"
fi
gunzip "$T/db.gz"
python3 - "$T/db" <<'PY'
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
print("integrity:", con.execute("pragma integrity_check").fetchone()[0])
for t in ("leads", "orders", "items", "subs", "payments"):
    print(t, con.execute(f"select count(*) from {t}").fetchone()[0])
PY
