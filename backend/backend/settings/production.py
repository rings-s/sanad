"""
production.py — production settings.

Required environment variables:
  DJANGO_SECRET_KEY
  DATABASE_URL          postgresql://user:pass@host:5432/dbname
  REDIS_URL             redis://host:6379/0
  CELERY_BROKER_URL     redis://host:6379/1
  CELERY_RESULT_BACKEND redis://host:6379/2

Optional environment variables:
  ALLOWED_HOSTS                    comma-separated, e.g. api.sanad.app
  CORS_ALLOWED_ORIGINS             comma-separated front-end origin(s)
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_STORAGE_BUCKET_NAME
  AWS_S3_REGION_NAME
  AWS_S3_CUSTOM_DOMAIN             CDN domain, e.g. cdn.sanad.app
  SENTRY_DSN
  DEFAULT_FROM_EMAIL
  SHEIKH_NOTIFICATION_EMAIL
  YOUTUBE_OAUTH2_CREDENTIALS_JSON  OAuth2 JSON for YouTube Data API uploads
"""
import dj_database_url
from decouple import config, Csv

from .base import *  # noqa: F401, F403

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# ── Database: PostgreSQL ──────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── Cache: Redis ──────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'sanad',
        'VERSION': 1,
        'TIMEOUT': 300,
    }
}

# ── File Storage: S3 (thumbnails / audio only — videos go to YouTube) ─────────
_bucket = config('AWS_STORAGE_BUCKET_NAME', default='')
if _bucket:
    INSTALLED_APPS += ['storages']  # noqa: F405

    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = _bucket
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')

    STORAGES = {
        'default': {'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
    _cdn = AWS_S3_CUSTOM_DOMAIN or f"{_bucket}.s3.amazonaws.com"
    MEDIA_URL = f"https://{_cdn}/media/"

# ── Email: Amazon SES ─────────────────────────────────────────────────────────
_ses_region = config('AWS_SES_REGION_NAME', default='us-east-1')
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = _ses_region
AWS_SES_REGION_ENDPOINT = f"email.{_ses_region}.amazonaws.com"
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@sanad.app')

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# ── Sentry ────────────────────────────────────────────────────────────────────
_sentry_dsn = config('SENTRY_DSN', default='')
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        traces_sample_rate=0.2,
        send_default_pii=False,
        environment='production',
    )
