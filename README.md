# brc222.org

Static site for the **BRC-222 JSON-LD schema** (OrdinalBridge). VPS checkout `/home/ubuntu/brc222.org`.

> **Where the live site is served from (checked 2026-10-09): box 1 (40.160.38.189), not this VPS.** Cloudflare reads box 1's `/var/www/brc222.org`; this VPS keeps an identical, retired copy. `deploy-www.sh` and the "Deploy (operator)" steps below publish to this VPS only, so they succeed without changing the public site. To publish, use the rsync in [docs/HANDOFF-bridge-schema-thread.md](docs/HANDOFF-bridge-schema-thread.md) (section 6) and check `curl -s https://brc222.org/schema`.

Harvested from Hostinger AI Builder (Sep 2026). See `docs/hostinger-harvest.md`.

## Structure

```
sites/www/          # index.html (schema doc), schema.json (generated), vocabulary.json (source), styles.css
tools/              # build-vocabulary.py, schema.template.json
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

## Relationship vocabulary

`sites/www/vocabulary.json` (published at https://brc222.org/vocabulary.json) is the single source of truth for bridge relationships. Each entry is an **inverse pair** (`isSupportedBy` / `supports`); "A isSupportedBy B" and "B supports A" are the same bridge, stored once in the canonical form (the entry's `name`). There is no direction field.

`schema.json`, the table on the page and the table in `docs/briefing-bridge-schema.md` are **generated** from it. Don't edit them by hand.

### Adding a relationship

1. Add an entry to `sites/www/vocabulary.json`: `name` (canonical), `inverse`, `label`/`inverseLabel`, both definitions, both IRIs (use a [CiTO](http://purl.org/spar/cito/) IRI when the meaning matches, otherwise `https://brc222.org/schema#<name>`), and `aliases` / `inverseAliases` for alternative spellings accepted on input. Bump `version` and `dateModified`.
   A relationship that reads the same from either end (like `contradicts`) is **symmetric**: give it `"symmetric": true` and only `name`, `label`, `definition`, `iri` and `aliases`. It is its own inverse and has no inverse fields.
2. `python3 tools/build-vocabulary.py` (it refuses duplicate names, alias collisions and reused IRIs). `--check` verifies the generated files are current.
3. `bash deploy-www.sh`, then commit.
4. Pull the new file into the consumers, which vendor a copy and need no code change:
   - Bridge Registry: `bash scripts/sync-vocabulary.sh`
   - Canopi: `node scripts/sync-bridge-vocabulary.mjs`

Test a relationship before committing it by adding the entry to a scratch copy of the repo.
