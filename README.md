# brc222.org

Static site for the **BRC-222 JSON-LD schema** (OrdinalBridge). VPS checkout `/home/ubuntu/brc222.org`.

Harvested from Hostinger AI Builder (Sep 2026). See `docs/hostinger-harvest.md`.

## Structure

```
sites/www/          # index.html (schema doc), schema.json, styles.css
deploy/scripts/     # deploy-www.sh, apply-nginx-and-tls.sh
deploy/nginx/       # HTTP bootstrap + HTTPS vhost
```

## Deploy (operator)

1. Point DNS A `@` and `www` to **216.238.91.120** (grey cloud for certbot).
2. Sync docroot and apply nginx + TLS:

```bash
bash /home/ubuntu/brc222.org/deploy-www.sh
sudo bash /home/ubuntu/brc222.org/deploy/scripts/apply-nginx-and-tls.sh
```

## Verify

```bash
curl -sI http://216.238.91.120/ -H 'Host: brc222.org' | head -5
curl -sk https://brc222.org/schema | head -5
```

Docroot: `/var/www/brc222.org`

Machine-readable schema: `https://brc222.org/schema` (JSON-LD context)
