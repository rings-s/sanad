#!/usr/bin/env bash
#
# Set the Fly.io secrets the Sanad API needs (everything except DATABASE_URL,
# which `fly mpg attach` sets for you). Run AFTER creating the app, Postgres,
# and Redis.
#
# Usage:
#   REDIS_URL='redis://default:...@fly-sanad-redis.upstash.io:6379' \
#   FRONTEND_URL='https://your-frontend.example' \
#   ./scripts/fly-secrets.sh
#
# REDIS_URL is required (copy it from `fly redis create` / `fly redis status`).
# FRONTEND_URL is optional (used for CORS + email links); defaults to localhost.

set -euo pipefail

APP="${APP:-sanad-api}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5173}"

if [[ -z "${REDIS_URL:-}" ]]; then
  echo "ERROR: REDIS_URL is required. Get it with: fly redis status <name>" >&2
  exit 1
fi

# A fresh, strong Django secret key — generated locally, never echoed.
SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')"

echo "Setting secrets on app: $APP"

fly secrets set --app "$APP" \
  DJANGO_SECRET_KEY="$SECRET_KEY" \
  REDIS_URL="$REDIS_URL" \
  CELERY_BROKER_URL="$REDIS_URL" \
  CELERY_RESULT_BACKEND="$REDIS_URL" \
  ALLOWED_HOSTS="${APP}.fly.dev" \
  CORS_ALLOWED_ORIGINS="$FRONTEND_URL" \
  FRONTEND_URL="$FRONTEND_URL" \
  AUTH_COOKIE_SECURE="true"

echo
echo "Done. Optional integrations — set these when ready:"
echo "  fly secrets set --app $APP GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=..."
echo "  fly secrets set --app $APP YOUTUBE_API_KEY=..."
echo "  fly secrets set --app $APP AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_STORAGE_BUCKET_NAME=... AWS_S3_REGION_NAME=..."
echo "  fly secrets set --app $APP DEFAULT_FROM_EMAIL=... SHEIKH_NOTIFICATION_EMAIL=..."
echo "  fly secrets set --app $APP SENTRY_DSN=..."
