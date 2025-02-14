# proxy/default.conf.tpl

server {
    listen [::]:${LISTEN_PORT};
    listen ${LISTEN_PORT};
    server_name ${DOMAIN};

    location ~/.well-known/acme-challenge {
        allow all;
        root /var/www/certbot;
    }
}
