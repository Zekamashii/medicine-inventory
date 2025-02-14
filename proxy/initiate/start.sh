#!/bin/sh

set -e

envsubst '${APP_HOST} ${APP_PORT} ${LISTEN_PORT} ${DOMAIN}' < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# start nginx with the dameon running in the foreground
nginx -g "daemon off;"