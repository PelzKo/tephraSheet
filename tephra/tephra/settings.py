"""Django settings for tephraSheet.

Configuration comes from environment variables, read from ``tephra/.env``
(see ``.env.sample``). Mirrors the TheLog deployment conventions:
``LOCAL=True`` forces SQLite and skips SSL hardening; MySQL is used only
when ``DB_ENGINE``, ``DB_NAME`` and ``DB_USERNAME`` are set and ``LOCAL=False``.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


LOCAL = env_bool("LOCAL", False)
DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if LOCAL or DEBUG:
        SECRET_KEY = "local-insecure-dev-key-do-not-use-in-production"
    else:
        raise RuntimeError("SECRET_KEY must be set when LOCAL and DEBUG are False")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]
CSRF_TRUSTED_ORIGINS = []
EXTERNAL_HOSTNAME = os.environ.get("EXTERNAL_HOSTNAME", "").strip()
if EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{EXTERNAL_HOSTNAME}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rules",
    "catalog",
    "characters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tephra.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tephra.wsgi.application"

_use_mysql = (
    not LOCAL
    and os.environ.get("DB_ENGINE")
    and os.environ.get("DB_NAME")
    and os.environ.get("DB_USERNAME")
)
if _use_mysql:
    DATABASES = {
        "default": {
            "ENGINE": os.environ["DB_ENGINE"],
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USERNAME"],
            "PASSWORD": os.environ.get("DB_PASS", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {"charset": os.environ.get("DB_CHARSET", "utf8mb4")},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "gm_login"
LOGIN_REDIRECT_URL = "character_list"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / ".cache",
    }
}

# Failed character-password attempts before a temporary lockout.
UNLOCK_MAX_ATTEMPTS = 8
UNLOCK_LOCKOUT_SECONDS = 300

if not LOCAL:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

if not DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# Unhandled 500s go to stderr regardless of DEBUG (supervisor captures it).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"stderr": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {"handlers": ["stderr"], "level": "ERROR", "propagate": False},
    },
}

SENTRY_DSN = os.environ.get("SENTRY_DSN", "").strip()
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(dsn=SENTRY_DSN, send_default_pii=False)
