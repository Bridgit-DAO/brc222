# Handoff: the BRC-222 bridge schema thread

**State as of 2026-10-09 ~19:00 UTC.** This is a snapshot for orienting a new session. It goes stale, so run the checks in section 9 before trusting any "live" claim. Read it top to bottom once; sections 5 and 6 are the working parts.

For the schema itself, read `docs/briefing-bridge-schema.md` in this repo. That is the contract other projects use. This document is about the *work*: what was done, where it runs, what is open, and what bit us.

---

## 1. What this thread was

A multi-day change to how bridges (typed, verifiable relationships between two pieces of content) are defined and handled across four codebases, driven by the owner (daveed@bridgit.io) making decisions as it went. In order:

1. Brought BRC-222 (brc222.org) up to the decided relationship list, added crosswalk bridges, deployed the Bridge Registry and connected Canopi to it, with a sync job from Canopi.
2. Redesigned the vocabulary: every relationship is an **inverse pair** (`isSupportedBy`/`supports`), one relationship is **symmetric** (`contradicts`), **`direction` was removed everywhere**, and the vocabulary became **data** (one JSON file) so adding a relationship needs no code change.
3. Added **deduplication**: the same bridge entered again, from either end, is an **endorsement** of the first.
4. Added `confirms`, a **likes** signal (the heart) reported by the feed and registry, and made the **in-app heart count** the same on both pages of a bridge.
5. Fixed Canopi's backups (they silently omitted every mixed-case table, including users) and its CI gate.

## 2. The system, in one picture

| Piece | Repo | Where it runs | Notes |
|---|---|---|---|
| Spec site + vocabulary | `Bridgit-DAO/brc222` (this repo) | **box 1 (40.160.38.189)**, nginx, `/var/www/brc222.org` (root-owned), behind Cloudflare. **Not** box 2 (it has only `staging.brc222.org`). This VPS keeps a retired, identical copy | `deploy-www.sh` here publishes to the retired copy only. Publish with the rsync in section 6 |
| Bridge Registry | `Bridgit-DAO/bridge-registry` | **new box 40.160.38.189** since 2026-10-08, `registry.theoverweb.org` via Cloudflare | Flask + gunicorn + SQLite. Public API is **read-only** (nginx blocks writes; `POST` has no auth) |
| Canopi (server + extension + embed) | `Bridgit-DAO/canopi` | **new box 40.160.38.189**, pm2 `canopi-prod` etc. | Bridges are created in Canopi; the registry fills itself from Canopi's public feed |
| The book (editorial docs) | `Bridgit-DAO/metaweb-book` | untracked copies in `/home/ubuntu/metaweb-book` | The plan and Chapter 11 redline live on branch `docs/second-edition-editorial` |

**Data flow:** a person makes a bridge in Canopi (`POST /v1/bridges`) -> stored as two message rows -> Canopi's public feed (`GET /api/meta/feed?tag_type=bridge`, standard-tier key) -> the registry's sync job (every 15 min, plus an hourly full reconcile) -> registry API (`/api/v1/bridges`, BRC-222 JSON-LD at `?format=jsonld`).

**Two VPSes.** This VPS ("old", `vultr`) is being decommissioned by another session. The registry and Canopi production moved to **40.160.38.189** ("box 1"). Do not assume anything runs here. See section 8. **The static site brc222.org also moved to box 1** (proven in section 8: a file written only on box 1 is served publicly, one written only here is not). Box 2 (40.160.38.190) is dev/staging and does not serve the real site.

## 3. The decisions (do not relitigate without the owner)

Recorded in `metaweb-book` `docs/second-edition-plan.md` as **D23, D28, D29, D30** (editorial branch).

- **Nine relationships, 17 names, schema 2.1.0.** Pairs: `cites`/`isCitedBy`, `isSupportedBy`/`supports`, `isCorroboratedBy`/`corroborates`, `isConfirmedBy`/`confirms`, `isRefutedBy`/`refutes`, `isQualifiedBy`/`qualifies`, `extends`/`isExtendedBy`, `isMemberOf`/`hasMember`. Symmetric: `contradicts`. The canonical (stored) form is the first name of each pair, with the claim as `from`.
- **"A R B" and "B inverse(R) A" are one bridge.** A symmetric relationship needs no swap.
- **No `direction`, anywhere.** Canopi and the registry refuse it with any value. The owner explicitly rejected tolerating it for cached browsers.
- **Retired for good, with no aliases:** `amplifies` (reach is not judgeable from the two passages), `contextualizes` (subjective catch-all; replaced by `qualifies`), `timeline`, `related`, `isContradictedBy`/"contradicted by".
- **Admission test for a relationship:** a verifier must be able to judge it from the two anchored passages and their dates alone.
- **`corroborates` is NOT symmetric** (evidence corroborates a claim, not the reverse). `contradicts` IS symmetric (mutual).
- **`confirms` was added** (the target settles the source as true: a primary record, a replication, a decisive check). Distinct from `corroborates` (independence) and `supports` (evidence, not conclusive).
- **Three separate signals, never conflated:** a **like** (the heart; cheap approval) < an **endorsement** (someone independently re-created the same bridge; effortful) < **verification** (enrolled verifiers attest; *not built*). The owner rejected a one-click "I agree" endorsement because it would just be a second heart.
- **Dedup identity:** a bridge = its two ends + canonical relationship. An end = its anchor identity hash, falling back to a hash of URL + anchor JSON. Endorsements count **distinct people**.
- **Vocabulary is data, not code.** Never hardcode relationship names. `https://brc222.org/vocabulary.json` is the single source of truth.

## 4. What is live (verified 2026-10-09)

| Thing | Version / commit | Live? |
|---|---|---|
| brc222.org schema + vocabulary | 2.1.0 (`fce272a`) | yes |
| Briefing for other projects | `docs/briefing-bridge-schema.md` | yes (its relationship table is generated from the vocabulary; its status section is hand-written and says everything is live except the Chrome extension, which is still accurate) |
| Bridge Registry (box 1) | `b4c9fcc` (dedup, endorsements, confirms, likes) | yes, restarted 2026-10-09 18:17 UTC |
| Canopi production (box 1) | `77b9b15d` (vocabulary, pairs, Swap, confirms, feed `bridge.likes`, heart counts shared across a bridge's two rows) | yes |
| Canopi web embed | serves the pair picker, Swap, confirms | yes (same compiled modules) |
| Canopi migration 058 | applied to prod 2026-10-07 | yes |
| Book: D30 + Chapter 11 redline + goldfish example | editorial branch `docs/second-edition-editorial` | yes (docs only) |
| **Chrome extension** new picker / Swap / confirms | not released | **no** (next extension release) |
| In-app heart counts (canopi PR #201) | merged `77b9b15d`, deployed 2026-10-09; verified on the real bridge (both rows report 3) | yes |

## 5. Recently finished, and what is still pending

### 5a. Canopi PR #201 (heart counts shown the same on both pages of a bridge): done

Merged (`77b9b15d`) after its checks passed and deployed to box 1 (server only; no extension release needed). Verified live on the one hearted bridge: both of its rows list 3 people (3 distinct) and report `reactionCount: 3`, where before they showed 2 and 3. The change is `lib/bridgeReactions.js` plus small edits to `routes/reactions.js` and `controllers/messagesController.js`; ordinary messages still use the old code path. Its tests include `tests/server/bridgeReactions.postgres.test.ts`, which needs a Postgres built from production's schema (setup in the file header).

### 5b. The Chrome extension release

The new relationship picker (pairs side by side), the Swap control, the "Source *relationship* Target" line and `confirms` reach extension users only with the next extension release. The server already accepts everything. An old extension that sends a retired name (`contextualizes`, `contradicted by`) or a `direction` gets a 400 until updated. Releasing is the owner's process, not something a session should do unprompted.

## 6. How to deploy (the routes that actually work)

**Never deploy without first confirming where the service runs** (section 8, "Mistakes").

### Canopi -> box 1 (server change)
```bash
cd /home/ubuntu/canopi-prod && git fetch -q origin
GIT_SSH_COMMAND="ssh -i $HOME/.ssh/ovh_canopi_prod_ed25519 -o BatchMode=yes" \
  git push ubuntu@40.160.38.189:canopi.git origin/main:refs/heads/main
ssh -i ~/.ssh/ovh_canopi_prod_ed25519 ubuntu@40.160.38.189 \
  'cd ~/canopi-prod && git pull -q --ff-only origin main && npm run build:presence && pm2 restart ecosystem.prod.config.js --only canopi-prod --update-env'
```
`npm run build:presence` is only needed when `presence/` changed (it rebuilds the extension files the web embed serves); skip it for a pure server change like #201. Then `curl http://127.0.0.1:3002/health/ready` on the box (expect 200) and check `https://api.canopi.live/`. `/home/ubuntu/canopi-prod` on the old VPS is a **worktree of `/home/ubuntu/canopi`** (which owns `main`), so it sits on a detached `origin/main`.

### Registry -> box 1
Box 1 has **no GitHub access by design**. From the old VPS:
1. Merge the PR. In `/home/ubuntu/bridge-registry` (must be on `main`, clean) `git pull`.
2. Push a side ref and fast-forward on the box:
   `GIT_SSH_COMMAND="ssh -i ~/.ssh/ovh_canopi_prod_ed25519 -o BatchMode=yes" git push ubuntu@40.160.38.189:bridge-registry HEAD:refs/heads/incoming`
   then on the box `git merge --ff-only incoming && git branch -D incoming`.
3. **Back up the DB first**, with sqlite's `.backup` into `~/bridge-registry-data/backups/` on the box. Startup migrations rewrite data in place.
4. Run the tests there (`.venv/bin/python -m unittest discover -s tests -t .`), then load production config and run the sync once: `set -a; . ./.env; set +a; python -m src.sync_canopi --reconcile` (**assert `SQLITE_PATH` is `/home/ubuntu/bridge-registry-data/bridges.db`** first).
5. `sudo systemctl restart bridge-registry` on the box. `ubuntu` there has passwordless sudo.

### brc222.org -> box 1 (NOT `deploy-www.sh`)
The public site is served from **box 1**. `bash deploy-www.sh` in this repo rsyncs to `/var/www/brc222.org` on **this VPS**, which Cloudflare no longer reads, so it silently publishes nothing. Edit `sites/www/vocabulary.json` (and prose in `index.html` outside the generated markers), run `python3 tools/build-vocabulary.py` (`--check` verifies), commit, then publish to box 1, whose docroot is `root:root`:
```bash
rsync -rlt --delete --chown=root:root --chmod=D755,F644 \
  --exclude='.well-known/' --exclude='._*' --exclude='.DS_Store' \
  --rsync-path="sudo rsync" -e "ssh -i $HOME/.ssh/ovh_canopi_prod_ed25519 -o BatchMode=yes" \
  sites/www/ ubuntu@40.160.38.189:/var/www/brc222.org/
```
Add `-n --itemize-changes` first to see what would change (right now: nothing). Verify with `curl -s https://brc222.org/schema` (the `version`). Keep `deploy-www.sh` in mind as a trap: it succeeds and prints "deploy complete".

### Adding a relationship (the payoff of the design)
1. Add one entry to `sites/www/vocabulary.json`: a pair (`name`, `inverse`, labels, definitions, IRIs, aliases) or `"symmetric": true` with just `name`, `label`, `definition`, `iri`, `aliases`. Bump `version` and `dateModified`. Prefer a CiTO IRI (`http://purl.org/spar/cito/...`) when the meaning matches; otherwise `https://brc222.org/schema#<name>`.
2. `python3 tools/build-vocabulary.py` (it refuses duplicate names, alias collisions, reused IRIs), deploy, commit.
3. Registry: `bash scripts/sync-vocabulary.sh`, run tests. Canopi: `node scripts/sync-bridge-vocabulary.mjs` (regenerates the extension's TS copy), run tests, add a changelog entry.
4. Update the handful of tests that hard-code counts (expect to bump "N relationships / M names" and swap any test that uses your new name as its "hypothetical new entry").
No application code changes. This was demonstrated four times.

## 7. What still needs doing

Ordered roughly by how much it matters. None of it is started unless noted.

1. **Make the brc222.org deploy path correct.** `deploy-www.sh` and the README's "Deploy (operator)" section still describe this VPS. Decide whether to point the script at box 1 (the rsync in section 6) or add a second script; until then follow section 6. (Not changed: it is the owner's deploy process.)
2. **Extension release** with the new bridge UI (5b). Owner's call.
3. **Verification is not built.** The `ValidationEntry` shape exists in the schema, and the briefing describes the intended model (agents + enrolled, compensated human verifiers; signed attestations; no fees or stakes), but there is no enrollment, no attestation storage and no API. Everything "verified" in the registry is currently just a status column nothing sets. This is the largest piece of real remaining work.
4. **Nothing uses endorsement or like counts yet** (ranking, display, verification input). Decide whether they should, and keep them separate from verification.
5. **Registry writes are unauthenticated**, which is why the public address is read-only. Any future direct-write or "endorse" API must be authenticated, and the owner leaned toward doing it in Canopi, not the registry.
6. **Crosswalk bridges** (`CrosswalkBridge`, `KnowledgeGraphNode`, required `match`, no direction) are specified on brc222.org but not stored or produced anywhere.
7. **Inscription on Bitcoin** is optional in the design and not built.
8. **Open vocabulary question:** none outstanding. (`confirms` was added; `corroborates` stays a pair.)
9. **Production hygiene found along the way** (not fixed): `reactions` has **no foreign key to `messages`** in the production database (Prisma's model declares one, the DB does not), so deleting a message leaves its reactions behind. Worth its own look.
10. **Live updates:** other open pages do not update live when someone reacts on a bridge's other row (realtime is per row). The next load is right.
11. **Old VPS cleanup:** the registry copy there is disabled and the brc222.org docroot and nginx vhost there are a retired identical copy; the registry checkout, data directory and my backups also remain. The owner has not asked for removal. Do not re-enable the old service.
12. **The book:** D30 and the Chapter 11 redline are done on the editorial branch (the goldfish example was rewritten at the owner's request). Chapter *text* is never edited directly (D25).

## 8. Gotchas and mistakes made (read before touching anything)

**Confirm where a service runs before deploying.** On 2026-10-09 I deployed the likes change to the *retired* registry copy on this VPS, because I assumed that is where it ran. It had been moved to box 1 the night before and disabled here. The public API was fine throughout. Checks that would have caught it: `dig +short registry.theoverweb.org` (Cloudflare IPs, not this VPS), `systemctl is-active bridge-registry` on **both** machines, `journalctl -u bridge-registry`.

**A site behind Cloudflare: DNS cannot tell you the origin, and neither can timestamps.** An earlier version of this document said brc222.org was served from this VPS, because my earlier deploys here did update the public site. At some point since (when is not recorded), Cloudflare's origin moved to box 1. Box 1's copy is identical because it was rsynced with timestamps preserved, so version, `Last-Modified` and `ETag` match on every machine, and DNS only shows Cloudflare's addresses. What settled it: write a uniquely named, harmless file in **one** machine's docroot only, fetch it through the public URL, then delete it. The file written here was a public 404 (and 200 straight to this VPS); the file written on box 1 was a public 200. Do this, and clean up, before trusting any "it is served from X" claim.

**The live registry checkout must stay on `main`.** On 2026-10-07 I developed on a feature branch inside the deployed checkout; the 15-minute sync cron ran my unmerged code and migrated the production database early. Develop in a worktree (`git worktree add ../bridge-registry-dev -b name origin/main`). A guard in `deploy/scripts/sync-canopi.sh` now refuses to run off `main`, but that is a backstop.

**Load production config before running registry code by hand.** `src.db` defaults to a *tracked sample database inside the repo* (`data/bridges.db`). I once migrated that instead of production because I skipped `.env`. Always `set -a; . ./.env; set +a` and assert `SQLITE_PATH`.

**Back up before anything that can migrate.** The registry migrates in place on startup and on the sync cron's first tick after a pull.

**CI, and how not to be fooled by it:**
- `check-changelog` requires a plain-language entry in `changelog.json` for changes under `presence/src/`, `routes/`, `controllers/`, `config/`, etc. Two PRs adding an entry at the top of the file conflict; resolve by keeping both.
- "Build, Test, And Security Gate" can go red while **every test passes**: vitest exits 1 on an unhandled `EnvironmentTeardownError` (an un-awaited `import()` in `MessageFeed`/`TabManager`/`UnifiedMessageModal`). Fixed for all presence tests in canopi#167 by a scoped setup file (`tests/presence/_setup/warmSmartTagModules.ts`). If it recurs, reproduce locally under full-suite load before changing anything.
- `tests/server/mcpRemote.test.ts` always fails on a fresh checkout (needs a built `mcp-server/dist`); CI builds it. Presence tests need `npm run build:presence` first.
- The merge-only-if-green watcher pattern (a background loop polling `check-runs`, merging on success) worked well; it dies with its session.

**GitHub quirks seen:** `git push` returned "Internal Server Error" on every repo for about 7 minutes (the REST API still worked; retrying until it recovered was right). `gh pr edit` and `gh pr create` hit a deprecated Projects-classic GraphQL error on some repos: use `gh api -X PATCH/POST repos/.../pulls` with `-F body=@file` instead.

**Terminals.** The terminal tool counts tabs per connection; tabs I opened become "user's" once typed in, and I cannot close them. Prefer doing things over SSH with the setup key. Registry/Canopi restarts on box 1 need no password; on this VPS they need the owner's sudo.

**Book docs.** In `/home/ubuntu/metaweb-book`, `docs/second-edition-plan.md` and `docs/redlines/*` are **untracked copies** of the editorial branch. Never `git checkout` another branch there (it deletes them); use `git worktree add <dir> docs/second-edition-editorial`, edit and push there, then copy the files back. I once lost and recovered them from the reflog.

**Privacy habit.** When inspecting data or config, print counts and an allowlist of fields, never values (an incident in another thread leaked part of a wallet recovery phrase through a denylist filter; the owner's notes record it).

**Testing recipe worth reusing** for anything that touches Canopi's SQL: a scratch Postgres 17 (Docker) built from a **read-only `pg_dump --schema-only` of production** plus Supabase stubs (roles `anon`/`authenticated`/`service_role`, schema `auth` with `users`/`uid()`/`role()`/`jwt()`, schema `realtime` with a no-op `broadcast_changes(... anyelement ...)`). `prisma db push` is not enough: the list query depends on columns and tables that only exist through SQL migrations. `tests/server/bridgeReactions.postgres.test.ts` (in canopi#201) documents the setup and skips without `BRIDGE_REACTIONS_TEST_DB`.

## 9. Check the state before trusting this document

```bash
# vocabulary live
curl -s https://brc222.org/schema | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['version'])"       # 2.1.0
# registry (public)
curl -s https://registry.theoverweb.org/api/v1/bridges | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['total'],[(b['relationship'],b['endorsements'],b['likes']) for b in d['bridges']])"
# which commits are deployed
ssh -i ~/.ssh/ovh_canopi_prod_ed25519 ubuntu@40.160.38.189 'cd ~/canopi-prod && git log --oneline -1; cd ~/bridge-registry && git log --oneline -1; systemctl is-active bridge-registry'
# is the old registry still off? (expect inactive/disabled)
systemctl is-active bridge-registry; systemctl is-enabled bridge-registry
# the real bridge's two rows should report the same reactionCount (both 3); ids via a read-only query on the prod DB
# which machine Cloudflare reads for brc222.org: see section 8 (probe file), not DNS
# Canopi main CI
gh api repos/Bridgit-DAO/canopi/commits/main/check-runs --jq '.check_runs[]|"\(.conclusion//.status)\t\(.name)"'
```
Expected at time of writing: schema `2.1.0`; registry `2` bridges (`contradicts`, 1 endorsement each, likes 3 and 0); Canopi `77b9b15d` and registry `b4c9fcc` on box 1; old registry `inactive`/`disabled`; every check that ran on Canopi `main` green (`007e2ee1` is a docs-only commit, so the test gate did not run for it; the last code commit's gate was green).

## 10. Working with the owner

- Decisions are theirs; they answer precisely and quickly. Recommend, then wait for the go on anything with product or reward consequences (the heart/endorsement/verification split, a one-click endorse, ranking).
- They do not want backward compatibility for names they have retired.
- They want things recorded: the book's decision log (`D##`), the briefing, this kind of document. Keep those current when you change a decision.
- Be plain about mistakes. Several sections above exist because of ones I made.
- Prefer doing, over asking, for reversible work in a worktree; ask before merging, deploying or restarting anything.

## 11. Where things are

| What | Path |
|---|---|
| This document / the briefing | `docs/HANDOFF-bridge-schema-thread.md`, `docs/briefing-bridge-schema.md` (this repo) |
| Vocabulary + generator | `sites/www/vocabulary.json`, `tools/build-vocabulary.py`, `README.md` ("Adding a relationship") |
| Registry code | `src/vocabulary.py` (loader), `src/identity.py` (dedup key), `src/submissions.py` (endorsements, likes), `src/sync_canopi.py`, `src/db.py` (migrations), `tests/` |
| Canopi bridge code | `lib/bridgeRelationships.js`, `routes/bridges.js`, `controllers/metaFeedController.js` (`getBridgeLikes`), `lib/bridgeReactions.js` (#201), `presence/src/config/bridgeVocabulary*.ts`, `presence/src/sidepanel/BridgeSessionPanel.ts`, `config/bridge-vocabulary.json`, `scripts/sync-bridge-vocabulary.mjs`, `migrations/058_*` |
| Canopi deploy/ops notes | `canopi` repo `deploy/README.md` (the server-move notes) and `docs/planning/SESSION_HANDOFF_2026-10-09.md` (another session's handoff, covering the server move and Canopi's own queue; read it alongside this one) |
| Decision log | `metaweb-book` branch `docs/second-edition-editorial`: `docs/second-edition-plan.md` (D23, D28, D29, D30), `docs/redlines/ch11-redline.md` |
| Backups made during this work | `~/bridge-registry-data/backups/` on both machines; `/home/ubuntu/canopi/backups/bridge-payload-058-before-*.json` |
