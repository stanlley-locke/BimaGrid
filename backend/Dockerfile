# ============================================================
# Stage 1: builder — install Python deps in a virtual env
# ============================================================
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

ARG APT_MIRROR=cdn-fastly.deb.debian.org
RUN sed -i "s/deb.debian.org/${APT_MIRROR}/g" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY backend/requirements/base.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: runtime — lean production image
# ============================================================
FROM python:3.12-slim-bookworm AS runtime

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid Backend"
LABEL org.opencontainers.image.description="Django 4.2 backend with gRPC support"

ARG APT_MIRROR=cdn-fastly.deb.debian.org
RUN sed -i "s/deb.debian.org/${APT_MIRROR}/g" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Application environment defaults (overridden via env_file / environment in compose)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.base

# Create a non-root system user and fix ownership
RUN useradd -m -r -u 1001 -s /bin/false bimagrid \
    && mkdir -p /app/static /app/media /app/backend \
    && chown -R bimagrid:bimagrid /app

WORKDIR /app/backend
COPY --chown=bimagrid:bimagrid backend/ .
RUN chmod +x start.sh

USER bimagrid

EXPOSE 8000 50051

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["/app/backend/start.sh"]
