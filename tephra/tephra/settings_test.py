"""Settings for the test suite: local SQLite, no SSL hardening."""

import os

os.environ["LOCAL"] = "True"
os.environ.setdefault("DEBUG", "True")

from .settings import *  # noqa: E402,F401,F403
