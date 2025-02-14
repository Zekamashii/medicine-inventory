# proxy/default.conf.tpl

server {
    listen [::]:${LISTEN_PORT};
    listen ${LISTEN_PORT};
    server_name ${DOMAIN};

    # Redirect all HTTP requests to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen [::]:443 ssl;
    listen 443 ssl;
    http2 on;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    server_name ${DOMAIN};
    root /var/www/html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 256;
    gzip_comp_level 5;
    gzip_proxied any;
    gzip_vary on;

    location /static/ {
        alias /app/staticfiles/;
        expires 365d;
    }

    location / {
        proxy_pass      http://${APP_HOST}:${APP_PORT};
        include         /etc/nginx/proxy_params;
    }

    location ~ /.well-known/acme-challenge/ {
        allow all;
        root /var/www/certbot;
    }
}
