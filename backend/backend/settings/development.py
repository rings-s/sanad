"""
development.py — local development settings.

- SQLite (no PostgreSQL required)
- Redis optional (LocMemCache fallback)
- Google SMTP email
- Verbose debug output
- CORS open to all origins
"""
import dj_database_url
from decouple import config

from .base import *  # noqa: F401, F403

# ── Security (deliberately relaxed for dev) ───────────────────────────────────
SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-dev-only-do-not-use-in-production-replace-me',
)
DEBUG = True
ALLOWED_HOSTS = ['*']

# ── Database: SQLite by default; PostgreSQL if DATABASE_URL is set ─────────────
# SQLite keeps local dev zero-dependency. Set DATABASE_URL (e.g. point at a local
# or Docker Postgres) to exercise the full PostgreSQL trigram search path.
_database_url = config('DATABASE_URL', default='')
if _database_url:
    DATABASES = {
        'default': dj_database_url.parse(_database_url, conn_max_age=600),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        }
    }

# ── Cache: Redis (falls back to LocMem if REDIS_URL is not set) ───────────────
_redis_url = config('REDIS_URL', default='')
if _redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _redis_url,
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'KEY_PREFIX': 'sanad',
            'TIMEOUT': 300,
        }
    }
else:
    # NOTE: LocMem cache is per-process — throttles do NOT share state between workers.
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'sanad-dev',
        }
    }

# ── Email: Google SMTP ────────────────────────────────────────────────────────
# Use a Gmail App Password (not your regular password).
# Enable 2FA → myaccount.google.com → Security → App Passwords.
_email_user = config('EMAIL_HOST_USER', default='')
if _email_user:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = _email_user
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = _email_user
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── CORS ──────────────────────────────────────────────────────────────────────
# CORS_ALLOW_ALL_ORIGINS cannot be True when CORS_ALLOW_CREDENTIALS is True —
# the browser rejects `Access-Control-Allow-Origin: *` with credentialed requests.
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# ── Celery: run tasks eagerly in dev (no broker required) ────────────────────
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default='True') == 'True'
CELERY_TASK_EAGER_PROPAGATES = True
