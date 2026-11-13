#!/usr/bin/env bash
# Supervisord entry point: collectstatic + migrate + seed_catalog must succeed, otherwise the app
# does not boot (supervisor reports FATAL). The backup and the deploy check only log on failure.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/.venv/bin/python"
cd "$REPO_ROOT/tephra"
"$PYTHON" manage.py collectstatic --noinput
bash "$REPO_ROOT/bin/backup.sh" || echo "start.sh: backup before migrate failed, continuing" >&2
"$PYTHON" manage.py migrate --noinput
"$PYTHON" manage.py seed_catalog
"$PYTHON" manage.py check --deploy || echo "start.sh: deploy check reported problems (see above)" >&2
exec "$PYTHON" -m gunicorn --workers 3 --access-logfile - --error-logfile - --bind 0.0.0.0:8000 tephra.wsgi:application
