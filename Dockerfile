# ── Stage 1: build dependencies ───────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.13-slim AS production

# Create a non-root user
RUN addgroup --system sanad && adduser --system --ingroup sanad sanad

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /build/.venv /app/.venv

# Copy application code
COPY backend/ ./

# Ensure our venv is on PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=backend.settings.production

# Collect static files (S3 bucket must be configured for media; static goes to /app/staticfiles)
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

USER sanad

EXPOSE 8000

# Use uvicorn workers for async support (ASGI).
# Gunicorn manages multiple worker processes; uvicorn handles each request.
CMD ["gunicorn", "backend.asgi:application", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "30", \
     "--keepalive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
