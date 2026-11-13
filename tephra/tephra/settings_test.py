"""Settings for the test suite: local SQLite, no SSL hardening."""

import os

os.environ["LOCAL"] = "True"
os.environ.setdefault("DEBUG", "True")

from .settings import *  # noqa: E402,F401,F403

# Throttle counters and card caches must not survive between test runs.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
