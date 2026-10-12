# Portfolio: pure static site, served by Caddy.
# Same serving pattern as Kevin's other VPS sites (see Sports_Predictor).
FROM caddy:2-alpine
COPY index.html photos.html /usr/share/caddy/
COPY css/ /usr/share/caddy/css/
COPY js/ /usr/share/caddy/js/
COPY assets/ /usr/share/caddy/assets/
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 80
