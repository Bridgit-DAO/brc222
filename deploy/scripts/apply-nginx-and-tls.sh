#!/usr/bin/env bash
# Apply brc222.org nginx vhost + Let's Encrypt cert. Requires root.
#   sudo bash /home/ubuntu/brc222.org/deploy/scripts/apply-nginx-and-tls.sh
#
# Prerequisite: DNS A for brc222.org + www -> 216.238.91.120 (grey cloud for certbot).
set -euo pipefail

REPO="${DEPLOY_PATH:-/home/ubuntu/brc222.org}"
CONF_FULL="$REPO/deploy/nginx/brc222.org.conf"
CONF_HTTP="$REPO/deploy/nginx/brc222.org.http-only.conf"
CONF_DST="/etc/nginx/sites-available/brc222.org.conf"
DOCROOT="${WWW_DOCROOT:-/var/www/brc222.org}"
CERT_DIR="/etc/letsencrypt/live/brc222.org"
VPS_IP="${VPS_IP:-216.238.91.120}"
EMAIL="${CERTBOT_EMAIL:-daveed@bridgit.io}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "error: run with sudo" >&2
  exit 1
fi

verify_acme_webroot() {
  local host="$1"
  local token="apply-test-$$"
  mkdir -p "$DOCROOT/.well-known/acme-challenge"
  echo ok > "$DOCROOT/.well-known/acme-challenge/$token"
  if ! curl -sfI "http://${VPS_IP}/.well-known/acme-challenge/${token}" -H "Host: ${host}" | head -1 | grep -q '200'; then
    echo "error: ACME webroot check failed for Host: ${host} via ${VPS_IP}" >&2
    rm -f "$DOCROOT/.well-known/acme-challenge/$token"
    exit 1
  fi
  rm -f "$DOCROOT/.well-known/acme-challenge/$token"
}

echo "==> rsync site to $DOCROOT"
sudo -u ubuntu env DEPLOY_PATH="$REPO" WWW_DOCROOT="$DOCROOT" \
  bash "$REPO/deploy/scripts/deploy-www.sh"

install -m 0644 "$CONF_HTTP" "$CONF_DST"
ln -sf "$CONF_DST" /etc/nginx/sites-enabled/brc222.org.conf

echo "==> nginx test + reload (HTTP)"
nginx -t
systemctl reload nginx

verify_acme_webroot brc222.org
verify_acme_webroot www.brc222.org

if [[ ! -f "$CERT_DIR/fullchain.pem" ]]; then
  echo "==> certbot (webroot) for brc222.org + www.brc222.org"
  certbot certonly --webroot -w "$DOCROOT" \
    -d brc222.org -d www.brc222.org \
    --non-interactive --agree-tos -m "$EMAIL"
fi

if [[ ! -f "$CERT_DIR/fullchain.pem" ]]; then
  echo "error: cert missing after certbot; keeping HTTP-only vhost at $CONF_DST" >&2
  exit 1
fi

echo "==> install HTTPS vhost"
install -m 0644 "$CONF_FULL" "$CONF_DST"
nginx -t
systemctl reload nginx

echo "==> verify (local)"
curl -sfI "http://${VPS_IP}/" -H 'Host: brc222.org' | head -5
curl -sfI "https://brc222.org/" | head -5 || echo "(HTTPS check skipped if DNS not on this host)"
echo "done: brc222.org -> $DOCROOT"
