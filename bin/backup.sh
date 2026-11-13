#!/usr/bin/env bash
# Database backup: mysqldump (or a copy of the SQLite file when LOCAL) with the settings from
# tephra/.env, gzipped into BACKUP_DIR (default ~/backups/tephra), files older than 14 days removed.
# Run nightly from cron and by start.sh before migrate.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/.venv/bin/python"
cd "$REPO_ROOT/tephra"

# One value per line: backup dir, engine, name, user, password, host, port (exactly what Django uses).
mapfile -t DB < <("$PYTHON" manage.py shell -v 0 -c "
from django.conf import settings
d = settings.DATABASES['default']
print(settings.BACKUP_DIR, d['ENGINE'], d['NAME'], d.get('USER', ''), d.get('PASSWORD', ''), d.get('HOST', ''), d.get('PORT', ''), sep='\n')")
DIR="${DB[0]}" ENGINE="${DB[1]}" NAME="${DB[2]}"
mkdir -p "$DIR"
chmod 700 "$DIR"
STAMP="$(date +%Y-%m-%d_%H%M%S)"
TMP="" CNF="" OUT=""
trap 'rm -f "$TMP" "$CNF" "$OUT.part"' EXIT

if [[ "$ENGINE" == *sqlite3 ]]; then
  if [[ ! -f "$NAME" ]]; then echo "backup.sh: no SQLite database yet ($NAME), nothing to back up"; exit 0; fi
  OUT="$DIR/tephra-$STAMP.sqlite3.gz"
  TMP="$(mktemp)"
  "$PYTHON" -c "import sqlite3, sys; sqlite3.connect(sys.argv[1]).backup(sqlite3.connect(sys.argv[2]))" "$NAME" "$TMP"
  gzip -c "$TMP" > "$OUT.part"
else
  OUT="$DIR/tephra-$STAMP.sql.gz"
  CNF="$(umask 077; mktemp)"
  PW="${DB[4]//\\/\\\\}"
  printf '[client]\nuser=%s\npassword="%s"\nhost=%s\nport=%s\n' "${DB[3]}" "${PW//\"/\\\"}" "${DB[5]:-localhost}" "${DB[6]:-3306}" > "$CNF"
  mysqldump --defaults-extra-file="$CNF" --single-transaction --routines --triggers "$NAME" | gzip > "$OUT.part"
fi
mv "$OUT.part" "$OUT"  # only complete dumps get the name /gm/ and the rotation look at
find "$DIR" -name 'tephra-*.gz' -mtime +13 -delete
echo "backup.sh: wrote $OUT"
