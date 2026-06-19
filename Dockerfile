# ── Stage 1: build dependencies ───────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Build the venv at its FINAL runtime path so console-script shebangs
# (gunicorn, celery, …) point at an interpreter that exists in the production
# image. Building under /build/.venv would bake in a broken /build shebang.
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# WhiteNoise serves Django's static files (admin, DRF, Swagger UI) in production.
# Installed directly into the venv to avoid regenerating uv.lock.
RUN VIRTUAL_ENV=/app/.venv uv pip install whitenoise


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.13-slim AS production

# Create a non-root user
RUN addgroup --system sanad && adduser --system --ingroup sanad sanad

WORKDIR /app

# Copy virtual environment from builder (already at /app/.venv with correct shebangs)
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY backend/ ./

# Ensure our venv is on PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=backend.settings.production

# Collect + compress static into /app/staticfiles for WhiteNoise. Must succeed so
# the manifest exists (admin pages 500 without it). Dummy env satisfies settings
# import at build time; collectstatic does not touch the database.
RUN DJANGO_SECRET_KEY=build-only-not-used \
    DATABASE_URL=postgres://u:p@localhost:5432/db \
    REDIS_URL=redis://localhost:6379/0 \
    python manage.py collectstatic --noinput

USER sanad

EXPOSE 8000

# Use uvicorn workers for async support (ASGI).
# Gunicorn manages multiple worker processes; uvicorn handles each request.
CMD ["gunicorn", "backend.asgi:application", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
