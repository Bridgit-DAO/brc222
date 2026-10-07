#!/usr/bin/env python3
"""
Generate the parts of brc222.org that come from the relationship vocabulary.

    python3 tools/build-vocabulary.py          # write sites/www/schema.json and the page table
    python3 tools/build-vocabulary.py --check  # exit 1 if either file is out of date

Source of truth: sites/www/vocabulary.json. To add a relationship, add an entry
there (name, inverse, definitions, labels, IRIs) and bump "version" and
"dateModified", then run this script. Nothing else on this site needs editing.

Written to:
  sites/www/schema.json   tools/schema.template.json + one JSON-LD term per name
  sites/www/index.html    between <!-- vocabulary:table:start --> and ...:end -->
"""

import html
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "sites/www/vocabulary.json"
TEMPLATE = ROOT / "tools/schema.template.json"
SCHEMA = ROOT / "sites/www/schema.json"
PAGE = ROOT / "sites/www/index.html"

START, END = "<!-- vocabulary:table:start -->", "<!-- vocabulary:table:end -->"
FIELDS = ("name", "label", "definition", "inverse", "inverseLabel", "inverseDefinition", "iri", "inverseIri")


def norm(s: str) -> str:
    """Matching key: lower case, letters and digits only."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load_vocabulary() -> dict:
    vocab = json.loads(VOCAB.read_text(), object_pairs_hook=OrderedDict)
    seen: dict[str, str] = {}
    iris: dict[str, str] = {}
    for rel in vocab["relationships"]:
        for f in FIELDS:
            if not isinstance(rel.get(f), str) or not rel[f].strip():
                raise SystemExit(f"vocabulary: {rel.get('name', '?')!r} is missing {f!r}")
        for f in ("aliases", "inverseAliases"):
            if not isinstance(rel.get(f), list):
                raise SystemExit(f"vocabulary: {rel['name']!r} needs a list {f!r}")
        if norm(rel["name"]) == norm(rel["inverse"]):
            raise SystemExit(f"vocabulary: {rel['name']!r} and its inverse match after normalisation")
        for key in [rel["name"], rel["inverse"], *rel["aliases"], *rel["inverseAliases"]]:
            if norm(key) in seen:
                raise SystemExit(f"vocabulary: {key!r} (in {rel['name']!r}) collides with {seen[norm(key)]}")
            seen[norm(key)] = f"{key!r} (in {rel['name']!r})"
        for iri in (rel["iri"], rel["inverseIri"]):
            if iri in iris:
                raise SystemExit(f"vocabulary: IRI {iri} used by {iris[iri]!r} and {rel['name']!r}")
            iris[iri] = rel["name"]
    return vocab


def build_schema(vocab: dict) -> str:
    schema = json.loads(TEMPLATE.read_text(), object_pairs_hook=OrderedDict)
    ctx = OrderedDict()
    for key, value in schema["@context"].items():
        ctx[key] = value
        if key == "explanation":
            ctx["relationship"] = OrderedDict([("@id", vocab["namespace"] + "relationship"), ("@type", "@vocab")])
            for rel in vocab["relationships"]:
                ctx[rel["name"]] = rel["iri"]
                ctx[rel["inverse"]] = rel["inverseIri"]
    for key in ctx:
        if key != "relationship" and list(ctx).count(key) != 1:
            raise SystemExit(f"schema: duplicate term {key!r}")
    schema["@context"] = ctx
    schema["version"] = vocab["version"]
    schema["dateModified"] = vocab["dateModified"]
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def build_table(vocab: dict) -> str:
    esc = html.escape
    rows = []
    for rel in vocab["relationships"]:
        rows.append(
            "      <tr>"
            f"<td><code>{esc(rel['name'])}</code></td><td>{esc(rel['definition'])}</td>"
            f"<td><code>{esc(rel['inverse'])}</code></td><td>{esc(rel['inverseDefinition'])}</td>"
            "</tr>"
        )
    return (
        f"{START}\n  <div class=\"table-wrap\">\n  <table>\n"
        "    <thead><tr><th>Canonical</th><th>Meaning</th><th>Inverse</th><th>Meaning of the inverse</th></tr></thead>\n"
        "    <tbody>\n" + "\n".join(rows) + "\n    </tbody>\n  </table>\n  </div>\n  " + END
    )


def build_page(vocab: dict) -> str:
    page = PAGE.read_text()
    if page.count(START) != 1 or page.count(END) != 1:
        raise SystemExit("index.html: expected exactly one vocabulary:table marker pair")
    head, rest = page.split(START)
    _, tail = rest.split(END)
    return head + build_table(vocab) + tail


def main() -> int:
    vocab = load_vocabulary()
    outputs = {SCHEMA: build_schema(vocab), PAGE: build_page(vocab)}
    if "--check" in sys.argv:
        stale = [p.relative_to(ROOT) for p, text in outputs.items() if p.read_text() != text]
        for p in stale:
            print(f"out of date: {p}  (run tools/build-vocabulary.py)")
        return 1 if stale else 0
    for path, text in outputs.items():
        path.write_text(text)
    print(f"vocabulary {vocab['version']}: {len(vocab['relationships'])} pairs, "
          f"{2 * len(vocab['relationships'])} names -> schema.json, index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
