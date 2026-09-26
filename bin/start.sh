#!/usr/bin/env bash
# Supervisord entry point: collectstatic + migrate + seed_catalog must succeed,
# otherwise the app does not boot (supervisor reports FATAL).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/.venv/bin/python"
cd "$REPO_ROOT/tephra"
"$PYTHON" manage.py collectstatic --noinput
"$PYTHON" manage.py migrate --noinput
"$PYTHON" manage.py seed_catalog
exec "$PYTHON" -m gunicorn --error-logfile - --bind 0.0.0.0:8000 tephra.wsgi:application
