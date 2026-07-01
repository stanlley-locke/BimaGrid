FROM nginx:1.27-alpine

COPY infrastructure/docker/configs/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
