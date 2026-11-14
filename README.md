# tephraSheet

A digital character sheet for the steampunk pen & paper game **Tephra**. The sheet looks like the official two-page character sheet, but every value is calculated from the rules: creation, level-ups, equipment and augments are all built in.

- Guided character creation in 10 steps (race & nationality → finishings). Every step can be chosen by hand or rolled randomly, or you can roll a full random character.
- Each character is protected by its own password. The main page lists all characters as cards.
- Level-up wizard: +2/+1/+1 skill points, a new specialty, retrofitting at levels 4/8/12, AP by level, and new augments.
- Hover over (or click/tap) any combined number to see where it comes from, e.g. Accuracy = specialties + race + weapon augment. Truncated text and racial traits open the same way.
- Play controls: damage and healing (HP first, then wounds), breather, XP clock, money, stances, situational toggles, status effects and called-shot (wounded/fatal) effects. Effects change the numbers automatically (Fatigued halves max HP, Blinded −4 Acc/Eva, lost max wounds…).
- Printable (A4, both pages).
- Item catalog, an object creator for weapons, armor and items (with augment slots), and bulk import from CSV or a pasted table.
- Admin mode can raise or lower any value without rule checks. The narrator logs in with a Django staff account and can edit every character, the catalog and the global settings.

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -r tephra/requirements-dev.txt
cd tephra
cp .env.sample .env              # set LOCAL=True, DEBUG=True for development
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py seed_catalog
../.venv/bin/python manage.py create_random_character --if-empty   # optional demo sheet, password "demo"
../.venv/bin/python manage.py createsuperuser   # narrator account
../.venv/bin/python manage.py runserver
../.venv/bin/pytest                             # tests
```

The rule data (`tephra/rules/data/*.json`) is generated from `tephra/rules/data/source/Tephra_Reference_full.md` combined with the hand-curated modifiers in `tephra/rules/curated.py`:

```bash
../.venv/bin/python manage.py build_rules_data
```

## Deployment

Deployment follows the same setup as TheLog: Django served by Gunicorn behind a reverse proxy (Apache), with static files served by Whitenoise. `bin/start.sh` runs `collectstatic`, a database backup (`bin/backup.sh`), `migrate`, `seed_catalog` (creates missing book items only; narrator edits stay), `purge_trash` and `check --deploy`, then `exec`s gunicorn (3 workers, access log on stdout) on `0.0.0.0:8000`. If `collectstatic`, `migrate` or `seed_catalog` fails, the app does not boot (supervisor reports FATAL); a failed backup, trash purge or deploy check is only logged.

Security notes:
- **Group passphrase:** set it on `/gm/` (Narrator settings). Every browser must enter it once (remembered for a year); the narrator never needs it. Without a passphrase the site is open to anyone who finds it. A new passphrase makes everyone enter it again.
- The Django admin lives at `/narrator-admin/` (change with `ADMIN_URL`). Narrator logins, character unlocks and the passphrase are throttled per client address. The address is the **last** `X-Forwarded-For` value (the one the reverse proxy adds), else `REMOTE_ADDR`.
- Failed unlocks, wrong passphrases, failed narrator logins, CSRF failures and bad `Host` headers are logged to stderr (`tephra.security`, `django.security`), i.e. `~/logs/tephra.err.log`.
- Character passwords need at least 8 characters (older shorter ones keep working).

Environment variables go in `tephra/.env` (see `.env.sample`):

| Variable | Notes |
|---|---|
| `SECRET_KEY` | always (random 50+ characters) |
| `DEBUG` | default `False` |
| `LOCAL` | `True` skips SSL hardening and forces SQLite |
| `EXTERNAL_HOSTNAME` | needed when `LOCAL=False`; added to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` |
| `DB_*` | MySQL/MariaDB, used only when `DB_ENGINE`, `DB_NAME` and `DB_USERNAME` are all set and `LOCAL=False`; otherwise SQLite |
| `ADMIN_URL` | path of the Django admin, default `narrator-admin/` |
| `SECURE_HSTS_SECONDS` | HSTS max-age when `LOCAL=False`, default one year; `0` switches it off |
| `BACKUP_DIR` | where `bin/backup.sh` writes dumps, default `~/backups/tephra` |
| `SENTRY_DSN`, `EMAIL_*` | optional |

### Initial server setup (Uberspace)

The app is served on its own subdomain (e.g. `tephra.<domain>`), not a subpath of an existing domain — Uberspace forwards a path-based backend's prefix through unchanged, and this app's `urls.py` has no support for stripping one, so a subdomain avoids that mismatch entirely.

1. Clone the repo and create the virtualenv:
   ```bash
   git clone <repo-url> ~/tephraSheet
   cd ~/tephraSheet
   python3 -m venv .venv
   .venv/bin/pip install -r tephra/requirements.txt
   ```
2. If the domain is registered outside Uberspace (e.g. at Strato), create the subdomain there first and point it at Uberspace: add an `A` record (IPv4) and an `AAAA` record (IPv6) for `tephra.<domain>` using the IPs from `uberspace web domain show`.
3. Register the subdomain with Uberspace and route it to the app's port:
   ```bash
   uberspace web domain add tephra.<domain>
   uberspace web backend set tephra.<domain> --http --port 8000
   ```
   Uberspace issues the Let's Encrypt certificate automatically the first time it sees an HTTPS request for the domain (typically seconds to a few minutes after DNS has propagated) — nothing to configure manually. TLS terminates at Apache, which must forward `X-Forwarded-Proto` (already the case for Uberspace-managed domains).
4. Create the MariaDB database via Uberspace's database overview (https://mysql.uberspace.de/phpmyadmin/), then create `tephra/.env` from `.env.sample` and fill in `SECRET_KEY`, `DEBUG=False`, `LOCAL=False`, `EXTERNAL_HOSTNAME=tephra.<domain>`, and the `DB_*` values for that database.
5. Create the logs directory and the supervisord service file at `~/etc/services.d/tephra.ini`:
   ```bash
   mkdir -p ~/logs
   ```
   ```ini
   [program:tephra]
   command=bash /home/<user>/tephraSheet/bin/start.sh
   directory=/home/<user>/tephraSheet/tephra
   autostart=true
   autorestart=true
   startsecs=15
   stderr_logfile=/home/<user>/logs/tephra.err.log
   stdout_logfile=/home/<user>/logs/tephra.out.log
   environment=PYTHONUNBUFFERED="1",PATH="/home/<user>/tephraSheet/.venv/bin:/usr/local/bin:/usr/bin:/bin"
   ```
6. Tell supervisord about the new service and start it:
   ```bash
   supervisorctl reread
   supervisorctl update
   supervisorctl status tephra
   ```

7. Nightly backups: `crontab -e` and add
   ```
   30 3 * * * bash /home/<user>/tephraSheet/bin/backup.sh >> /home/<user>/logs/tephra-backup.log 2>&1
   45 3 * * * cd /home/<user>/tephraSheet/tephra && ../.venv/bin/python manage.py purge_trash >> /home/<user>/logs/tephra-backup.log 2>&1
   ```
   `bin/backup.sh` dumps the database configured in `tephra/.env` (`mysqldump`, or a copy of the SQLite file when `LOCAL=True`) to `BACKUP_DIR/tephra-<date>.sql.gz` and deletes dumps older than 14 days. `start.sh` also makes one before every `migrate`. `/gm/` shows the time of the newest backup. `purge_trash` deletes characters, wiki pages and custom catalog items that have been in the trash (on `/gm/`) for 30 days; `start.sh` runs it too.
8. Optional demo character (password `demo`): `.venv/bin/python tephra/manage.py create_random_character --if-empty`.

### Restoring a backup

```bash
supervisorctl stop tephra
gunzip -c ~/backups/tephra/tephra-<date>.sql.gz | mysql <db name>     # MariaDB (credentials from ~/.my.cnf)
# SQLite: gunzip -c ~/backups/tephra/tephra-<date>.sqlite3.gz > tephra/db.sqlite3
supervisorctl start tephra
```

### Each release

```bash
cd ~/tephraSheet && source .venv/bin/activate && git pull
pip install -r tephra/requirements.txt
supervisorctl restart tephra
```
