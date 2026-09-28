#!/usr/bin/env bash
# Rsync sites/www to the nginx docroot.
set -euo pipefail

REPO_PATH="${DEPLOY_PATH:-/home/ubuntu/brc222.org}"
DOCROOT="${WWW_DOCROOT:-/var/www/brc222.org}"
SOURCE="${REPO_PATH}/sites/www"

if [[ ! -d "$SOURCE" ]]; then
  echo "error: missing $SOURCE" >&2
  exit 1
fi

echo "==> rsync $SOURCE/ -> $DOCROOT/"
mkdir -p "$DOCROOT"
rsync -a --delete \
  --exclude='._*' \
  --exclude='.DS_Store' \
  "$SOURCE/" "$DOCROOT/"

echo "deploy complete: www -> $DOCROOT"
