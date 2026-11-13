"""Settings for the test suite: local SQLite, no SSL hardening."""

import os

os.environ["LOCAL"] = "True"
os.environ.setdefault("DEBUG", "True")

from .settings import *  # noqa: E402,F401,F403

# Per-run cache so throttles (wiki edits per IP) never carry over between test runs.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
