# Briefing: the BRC-222 bridge schema

For any project that needs to **read, write, display or reason about bridges**. Self-contained; written 2026-10-07 against vocabulary **2.0.0**. The authoritative sources are linked at the end. If this document and those disagree, they win.

## 1. What a bridge is

A **bridge** is a typed, verifiable relationship between two pieces of content, each pinned to an exact passage, image region or moment (a *context anchor*). "This sentence is refuted by that investigation." It is the unit of the Overweb's Bridge Registry and of Canopi's bridge flow.

**BRC-222** is the public format: JSON-LD, released CC0, at https://brc222.org. Inscribing a bridge on Bitcoin is optional; a bridge is fully useful without it. Verification (by agents plus enrolled, compensated human verifiers, no fees or stakes) covers **both anchors and the relationship**, and is recorded as signed attestations inside the bridge (`validation`).

There are two kinds:

- **Content bridge** (`OrdinalBridge`): passage to passage, with a relationship. Almost everything is this.
- **Crosswalk bridge** (`CrosswalkBridge`): a node in one knowledge graph to the matching node in another (a Wikidata item and its library-authority record). Different shape; see section 6. The registry does not store these yet.

## 2. The shape of a content bridge

```json
{
  "@context": "https://brc222.org/schema",
  "@type": "OrdinalBridge",
  "@id": "bitcoin:inscription:<id>",
  "from": {
    "@type": "WebPage",
    "@id": "https://example.org/post",
    "content": { "@type": "TextQuoteSelector", "exact": "the quoted words", "prefix": "text before ", "suffix": " text after" }
  },
  "to": { "@type": "WebPage", "@id": "https://example.org/report" },
  "relationship": "isSupportedBy",
  "explanation": "Optional, human-readable.",
  "validation": [ { "@type": "ValidationEntry", "validator": "https://v.example/profile.json", "timestamp": "2026-10-07T00:00:00Z", "signature": "..." } ]
}
```

- `from` is the **claim** (or the thing being described); `to` is the related material. `@type` of an end may be `WebPage`, `Video`, `Image`, `Audio`, `DigitalArtifact`, `Inscription`, `Sat` or `Claim`.
- `@id` of the bridge is the inscription if there is one, otherwise any stable IRI.
- **There is no `direction` field.** Version 2.0.0 removed it. If you find code that sends or expects one, it predates 2.0.0.

## 3. Relationships: inverse pairs

Every relationship is an **inverse pair**, or is **symmetric** (its own inverse, because it reads the same from either end; only `contradicts` today). **"A R B" and "B inverse(R) A" are the same bridge**, written from opposite ends, so a bridge can be constructed from either end. It is stored **once**, in the **canonical form** (the first column), with the claim as `from`. A symmetric relationship needs no swap: "A contradicts B" is "B contradicts A".

<!-- vocabulary:briefing-table:start -->
| Canonical | Inverse | Canonical form means | Maps to |
|---|---|---|---|
| `cites` | `isCitedBy` | The source quotes or references the target. | CiTO |
| `isSupportedBy` | `supports` | The target gives evidence or argument in favour of the source, which is typically a claim. The target need not be independent of it. | CiTO |
| `isCorroboratedBy` | `corroborates` | The target independently confirms the source: a separate account, dataset or investigation reaching the same result. | BRC-222 |
| `contradicts` | *(symmetric)* | The source and the target are in tension, or inconsistent with each other. It does not say which of the two is right. It reads the same from either end. | BRC-222 |
| `isRefutedBy` | `refutes` | The target shows the source to be false, with evidence. | CiTO |
| `isQualifiedBy` | `qualifies` | The target limits, conditions or distinguishes the source: it holds, but not as broadly or as simply as stated. | CiTO |
| `extends` | `isExtendedBy` | The source builds on the target, taking its idea, method or finding further. | CiTO |
| `isMemberOf` | `hasMember` | The source belongs to the collection, series, set or group the target describes. | BRC-222 |
<!-- vocabulary:briefing-table:end -->

Read each as "`from` *relationship* `to`". Full definitions for both forms: https://brc222.org/#relationships.

**Why these and not others.** A relationship is in the list only if a verifier can judge it **from the two anchored passages and their dates alone**. The set escalates on two axes: `supports` gives evidence for, `corroborates` adds that the evidence is *independent*; `contradicts` says two passages conflict without saying who is right, `refutes` says one is false, with evidence. `qualifies` says the target holds, but not as broadly as stated.

**Retired, and why.** Do not add these back, and reject them on input:

- `amplifies`: reach and repetition depend on audience size and the author's process, neither of which is in the passages. Spread is shown by *counting* `isCitedBy` bridges on a source.
- `contextualizes`: "background needed to understand" is subjective and became a catch-all. `qualifies` is sharper.
- `timeline`, `related`, `relates to`: they named no specific relationship. `related` holds between any two things, so it cannot be verified.
- `isContradictedBy` / "contradicted by": contradiction is mutual, so `contradicts` is symmetric and has no passive form. There is no alias for the old passive spelling.

### The one algorithm every consumer needs

Normalise the input (lower-case, keep only letters and digits), look it up among every `name`, `inverse` and alias in the vocabulary, and get back the canonical name plus whether it was the inverse. If it was, **swap `from` and `to`** (URL, anchor, content type, hash) before storing or comparing. A symmetric relationship (`contradicts`) is its own inverse and never reports a swap.

```python
import re
def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
# lookup: norm(key) -> (canonical_name, swapped), built from each entry's name, inverse (absent when symmetric), aliases, inverseAliases
name, swapped = lookup[norm(raw)]        # KeyError / None => reject with 400
if swapped: src, dst = dst, src
```

```js
const norm = (s) => String(s ?? '').toLowerCase().replace(/[^a-z0-9]/g, '');
const hit = lookup.get(norm(raw));      // { name, swapped } or undefined => reject
if (hit?.swapped) [src, dst] = [dst, src];
```

Matching ignores case and punctuation, so `is-supported-by`, `Is Supported By` and `isSupportedBy` are the same. Aliases (for example the old Canopi label "supported by") are accepted on input only and never output. The old "contradicted by" is not an alias: `contradicts` is symmetric and accepts only its own name.

## 4. The vocabulary is data: do not hardcode names

`https://brc222.org/vocabulary.json` is the **single source of truth**. The schema (`/schema`) and the table on the page are generated from it. Each entry holds: `name`, `inverse`, `label`, `inverseLabel`, both definitions, both IRIs, and `aliases` / `inverseAliases`. A symmetric entry has `"symmetric": true` and only `name`, `label`, `definition`, `iri` and `aliases`; it has no inverse fields.

- **Vendor a copy** and drive validation, UI, error messages and filters from it. The Bridge Registry and Canopi both do. Nothing in their code names a relationship, so adding one is a new JSON entry.
- Each vendored copy needs a `--check` that fails when it falls behind the published file.
- **To add a relationship:** add one entry to `sites/www/vocabulary.json` in the `brc222` repo, bump `version` and `dateModified`, run `python3 tools/build-vocabulary.py` (it refuses duplicate names, alias collisions and reused IRIs), deploy, then sync each consumer. Details in that repo's README.
- A relationship must pass the test in section 3 before it goes in.

## 5. RDF

BRC-222 is JSON-LD, so a bridge expands to RDF. `relationship` is typed `@vocab`, so its value is an **IRI**, not a string: `isSupportedBy` becomes `http://purl.org/spar/cito/isSupportedBy`. CiTO (the Citation Typing Ontology) IRIs are used wherever the meaning matches; `corroborates`, `contradicts` and `isMemberOf` (and their inverses) use `https://brc222.org/schema#<name>`. Crosswalk `match` values expand to SKOS IRIs.

Caveat: `TextQuoteSelector` is in the BRC-222 namespace (`https://brc222.org/schema#TextQuoteSelector`), **not** the W3C Web Annotation one (`http://www.w3.org/ns/oa#TextQuoteSelector`). Same shape, different IRI, so RDF tools will not treat them as the same thing.

Fetching the context from Python: brc222.org (behind Cloudflare) returns 403 to the bare `Python-urllib` user agent. `requests`, `rdflib`, Java, Go and Node are fine.

## 6. Crosswalk bridges

Link entities, not passages. Ends are `KnowledgeGraphNode` (`@id`, `graph`, optional `identifier`, `label`). The link is a **required** `match`, read "`from` *match* `to`": `exactMatch`, `closeMatch`, `broadMatch` (`from` is broader), `narrowMatch` (`from` is narrower), `relatedMatch`. These are the SKOS mapping properties. There is no default and no `direction`: swap the ends and a `broadMatch` becomes a `narrowMatch`; exact, close and related read the same either way.

## 7. Where bridges live and how to use them

| What | Where |
|---|---|
| Spec page and definitions | https://brc222.org |
| JSON-LD context | https://brc222.org/schema (also `/schema.json`) |
| Vocabulary (source of truth) | https://brc222.org/vocabulary.json |
| Bridge Registry (read-only public API) | https://registry.theoverweb.org/api/v1/ |
| Canopi (where people make bridges) | `POST /v1/bridges` at https://api.canopi.live, signed-in users only |
| Canopi public feed (bridge posts) | `GET https://api.canopi.live/api/meta/feed?tag_type=bridge` |

**Reading.** Registry: `GET /api/v1/bridges` (filters `relationship` (either form), `status`, `source_hash`, `target_hash`, `limit`, `offset`), `GET /api/v1/bridges/<id>?format=jsonld` for the BRC-222 form, `GET /api/v1/bridges/export` for NDJSON bulk export (`?since=<ISO>`). The public address is **read-only**: writes are refused at nginx because the registry's `POST` has no authentication yet. A filter or write with an unknown relationship returns 400 listing every accepted name.

**Writing.** Go through Canopi. Send any accepted form of the relationship; it is stored canonically with the ends swapped if needed. A request that carries `direction` is rejected, with any value. In Canopi's bridge panel a person says what they mean in either of two ways: pick the **inverse form** of the relationship (the picker shows each pair side by side), or **swap** the two anchors (a Swap control, shown once both are chosen; the panel reads "Source *relationship* Target" so the statement is plain before submitting). Both end up as the same stored bridge. The registry fills itself from Canopi's public feed (incremental sync every 15 minutes, plus an hourly reconcile that adds missing and removes no-longer-public bridges). Only bridges Canopi already shows publicly are synced.

**Displaying.** Show a bridge **in the voice of the page it appears on**: "supported by B" on the claim, "supports A" on the evidence; use `label` / `inverseLabel`; a symmetric relationship shows the same label on both. Do not show raw identifiers. To show how far a claim spread, count `isCitedBy` bridges on its source.

## 8. Status (2026-10-07) and known gaps

The decisions are recorded in the Metaweb second-edition plan (D23, D28, D29; a D30 for the pairs change, and the matching Chapter 11 wording, are still to be written).

- **Live:** BRC-222 **2.0.0** (spec, schema, `vocabulary.json`).
- **In flight (pull requests open, not yet merged or deployed):** the Bridge Registry change (`Bridgit-DAO/bridge-registry#8`: inverse pairs, `direction` removed, in-place database migration) and Canopi's matching change (`Bridgit-DAO/canopi#164`: server, public feed, extension picker). Until both ship, the registry and Canopi still speak the previous 1.x vocabulary (`supports`, `contradicts`, `is-member-of`, `direction`), so **their live output does not yet match this briefing**. Deploy order: registry first, then Canopi. The extension's new picker reaches users with its next release; the web embed picks it up on deploy.
- **No deduplication yet.** Two submissions of the same bridge are two records, even though "the same bridge from either end" is the model. A uniqueness rule on (from anchor, relationship, to anchor) is the obvious next step.
- **Symmetric relationships and deduplication.** `contradicts` is symmetric, so "A contradicts B" and "B contradicts A" are the same bridge; a future uniqueness rule must treat both orders as one (for example by ordering the two anchors). `corroborates` is logically symmetric too but is still modelled as a pair.
- **Registry writes are unauthenticated**, hence read-only public access.
- **Crosswalk bridges** are specified but not stored or produced anywhere yet.
- **Data volume is tiny:** two bridges exist. Changing vocabulary now is cheap; it gets expensive with volume.

## 9. Do and don't

- **Do** vendor `vocabulary.json` and resolve through it; **do** swap the ends for inverse forms; **do** treat unknown names as errors.
- **Don't** hardcode relationship names, invent new ones outside the vocabulary, or reintroduce `direction`, `amplifies`, `contextualizes`, `isContradictedBy`, `timeline` or `related`.
- **Don't** tolerate `direction` for "older clients". There are none worth keeping, and silently ignoring `to-from` would invert a bridge's meaning.
- **Don't** treat a bridge as proof. It is a *claim* that one passage relates to another; it is verified only when it carries attestations.
- **Don't** put personal data in a bridge or inscribe one without the author's consent: inscription is public and permanent.

## 10. Links

- Spec and definitions: https://brc222.org
- Vocabulary: https://brc222.org/vocabulary.json
- Repos: `Bridgit-DAO/brc222` (spec and generator), `Bridgit-DAO/bridge-registry` (registry), `Bridgit-DAO/canopi` (bridge creation)
- CiTO: http://purl.org/spar/cito/ · SKOS mapping properties: https://www.w3.org/TR/skos-reference/#mapping
- Changelog: https://brc222.org/#changelog
