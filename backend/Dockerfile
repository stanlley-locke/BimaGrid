# ============================================================
# Stage 1: builder — install Python deps in a virtual env
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY backend/requirements/base.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: runtime — lean production image
# ============================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid Backend"
LABEL org.opencontainers.image.description="Django 4.2 backend with gRPC support"

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Application environment defaults (overridden via env_file / environment in compose)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.base

WORKDIR /app/backend
COPY backend/ .

# Create a non-root system user and fix ownership
RUN useradd -r -u 1001 -s /bin/false bimagrid \
    && mkdir -p /app/static /app/media \
    && chown -R bimagrid:bimagrid /app

USER bimagrid

EXPOSE 8000 50051

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
