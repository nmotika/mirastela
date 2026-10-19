#!/bin/bash
# Nightly database backup (systemd timer mirastela-backup, 03:30).
# 1. Consistent SQLite snapshot (online backup API, safe while the API is running), gzip, keep 7 locally.
# 2. If /etc/mirastela-backup.env exists: encrypt with gpg (passphrase) and upload to Cloudflare R2
#    with rclone, keep 30 days there.
# Restore test: deploy/restore-test.sh
set -euo pipefail
DB=${MIRASTELA_DB:-/var/lib/mirastela/mirastela.db}
DIR=/var/backups/mirastela
mkdir -p "$DIR" && chmod 700 "$DIR"
STAMP=$(date -u +%Y%m%d-%H%M)
SNAP="$DIR/mirastela-$STAMP.db"
python3 - "$DB" "$SNAP" <<'PY'
import sqlite3, sys
src, dst = sqlite3.connect(sys.argv[1]), sqlite3.connect(sys.argv[2])
with dst:
    src.backup(dst)
ok = dst.execute("pragma integrity_check").fetchone()[0]
if ok != "ok":
    sys.exit("integrity check failed: " + ok)
PY
gzip -9 "$SNAP"
ls -1t "$DIR"/mirastela-*.db.gz | tail -n +8 | xargs -r rm --
echo "local backup $SNAP.gz $(du -h "$SNAP.gz" | cut -f1)"

if [ -f /etc/mirastela-backup.env ]; then
  set -a; . /etc/mirastela-backup.env; set +a   # BACKUP_PASSPHRASE, RCLONE_CONFIG_R2_* , R2_BUCKET
  ENC="$SNAP.gz.gpg"
  gpg --batch --yes --pinentry-mode loopback --passphrase "$BACKUP_PASSPHRASE" --symmetric --cipher-algo AES256 -o "$ENC" "$SNAP.gz"
  rclone copy "$ENC" "r2:$R2_BUCKET/db/" --s3-no-check-bucket
  rclone delete "r2:$R2_BUCKET/db/" --min-age 30d --s3-no-check-bucket || true
  rm -f "$ENC"
  echo "offsite backup uploaded to r2:$R2_BUCKET/db/"
else
  echo "offsite backup skipped: /etc/mirastela-backup.env missing"
fi
