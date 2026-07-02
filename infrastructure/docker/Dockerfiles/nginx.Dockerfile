FROM nginx:1.25-alpine

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid Nginx"
LABEL org.opencontainers.image.description="Nginx reverse proxy / static asset server"

RUN apk add --no-cache curl

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

COPY infrastructure/docker/configs/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1
