# ============================================================
# Stage 1: builder
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY ussd/requirements/ requirements/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements/base.txt

# ============================================================
# Stage 2: runtime
# ============================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid USSD Service"
LABEL org.opencontainers.image.description="Django USSD microservice for Africa's Talking gateway"

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=src.gateway.settings

RUN useradd -r -u 1002 -s /bin/false ussd \
    && mkdir -p /app/ussd \
    && chown -R ussd:ussd /app

WORKDIR /app/ussd
COPY --chown=ussd:ussd ussd/ .

USER ussd

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8001/health/ || exit 1

CMD ["gunicorn", "src.gateway.wsgi:application", \
     "--bind", "0.0.0.0:8001", \
     "--workers", "2", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
