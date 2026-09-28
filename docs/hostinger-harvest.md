# Hostinger harvest (brc222.org)

Harvested **2026-09-09** via live site fetch (`curl https://brc222.org/`). Hostinger MCP
(`user-hostinger-mcp`) was **not available** in this Cursor session; MCP file listing for
builder sites typically returns Not found anyway (see bridgit.io harvest).

## Site metadata (from HTML payload)

| Field | Value |
|-------|-------|
| domain | brc222.org |
| generator | Hostinger AI Builder |
| website_type | builder (Zyro/Astro SSR) |
| siteId | AMq17zZwq0C6Qap6 |
| zyrosite assets | https://assets.zyrosite.com/AMq17zZwq0C6Qap6/ |

## DNS at harvest time

| Record | Value |
|--------|-------|
| brc222.org A | 77.37.76.222 (Hostinger) |
| www.brc222.org | CNAME to www.brc222.org.cdn.hstgr.net |

## Page content

Single-page site: **BRC-222 JSON-LD Schema** documentation (slug `schema` on builder).
Embedded HTML extracted from GridEmbed SSR payload into `sites/www/index.html`.

Hostinger `/schema` path returned **404** (builder quirk). VPS serves machine-readable
context at `/schema` -> `schema.json` for bridge-registry `@context` URLs.

## Contact / footer (from live site)

- info@bridgit.io (maintainers)
- contact@brc222protocol.com (footer form email on Hostinger)
- Placeholder social links on Hostinger (facebook/instagram/tiktok/x generic URLs)

## Zyro forms

Contact form used Zyrosite backend tokens (not migrated). No form on VPS static rebuild.
