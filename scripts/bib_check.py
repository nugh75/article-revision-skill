#!/usr/bin/env python3
"""Cross-check article citations against the .bib file.

Detects:
- Pandoc-style citations [@Key] in the article that don't appear in .bib;
- .bib entries with missing required fields;
- .bib entries never cited in the article (informational only).

Examples:
    bib_check.py article.md reference.bib
    bib_check.py article.md reference.bib --apa
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from pybtex.database import parse_file
except ImportError:
    print("ERROR: pybtex not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)


PANDOC_CITE_PATTERN = re.compile(r"\[@([A-Za-z0-9_:.-]+)(?:[,\s][^]]*)?\]")
PANDOC_INLINE_PATTERN = re.compile(r"@([A-Za-z0-9_:.-]+)\b")
APA_INLINE_PATTERN = re.compile(r"\(([A-Z][A-Za-zàèéìòù'.\- &]+?,\s*\d{4}[a-z]?)\)")


REQUIRED_FIELDS_BY_TYPE: dict[str, set[str]] = {
    "article": {"author", "title", "journal", "year"},
    "book": {"author", "title", "publisher", "year"},
    "incollection": {"author", "title", "booktitle", "year"},
    "inbook": {"author", "title", "publisher", "year"},
    "inproceedings": {"author", "title", "booktitle", "year"},
    "report": {"author", "title", "institution", "year"},
    "techreport": {"author", "title", "institution", "year"},
    "phdthesis": {"author", "title", "school", "year"},
    "mastersthesis": {"author", "title", "school", "year"},
    "misc": {"title", "year"},
}


def extract_pandoc_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for m in PANDOC_CITE_PATTERN.finditer(text):
        keys.add(m.group(1))
    # also catch bare @Key outside brackets — uncommon but possible
    for m in PANDOC_INLINE_PATTERN.finditer(text):
        # filter out emails and noise: @Key must look like a citation key
        candidate = m.group(1)
        if len(candidate) > 3 and any(c.isupper() for c in candidate):
            keys.add(candidate)
    return keys


def extract_apa_inline(text: str) -> set[str]:
    """Returns a set of `Author, Year` strings found in inline APA citations."""
    out: set[str] = set()
    for m in APA_INLINE_PATTERN.finditer(text):
        out.add(m.group(1).strip())
    return out


def check_bib(bib_path: Path) -> tuple[dict, list[tuple[str, str]]]:
    bib_data = parse_file(str(bib_path))
    issues: list[tuple[str, str]] = []
    for key, entry in bib_data.entries.items():
        etype = entry.type.lower()
        required = REQUIRED_FIELDS_BY_TYPE.get(etype, {"author", "title", "year"})
        for field in required:
            value = entry.fields.get(field)
            if field == "author":
                value = value or " and ".join(p.last_names[0] for p in entry.persons.get("author", []) if p.last_names)
            if not value:
                issues.append((key, f"missing field: {field}"))
    return bib_data.entries, issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-check article citations vs .bib.")
    ap.add_argument("article", type=Path)
    ap.add_argument("bib", type=Path)
    ap.add_argument("--apa", action="store_true", help="Also extract APA-style inline citations")
    args = ap.parse_args()

    if not args.article.exists():
        print(f"ERROR: article not found: {args.article}", file=sys.stderr)
        return 2
    if not args.bib.exists():
        print(f"ERROR: bib not found: {args.bib}", file=sys.stderr)
        return 2

    article_text = args.article.read_text(encoding="utf-8")
    pandoc_keys = extract_pandoc_keys(article_text)
    apa_keys = extract_apa_inline(article_text) if args.apa else set()

    bib_entries, bib_issues = check_bib(args.bib)
    bib_keys = set(bib_entries.keys())

    cited_not_in_bib = pandoc_keys - bib_keys
    in_bib_not_cited = bib_keys - pandoc_keys

    print(f"# Bib check: {args.article.name} vs {args.bib.name}")
    print(f"\n## Pandoc-cited keys (in article): {len(pandoc_keys)}")
    print(f"## Bib entries: {len(bib_entries)}")

    if cited_not_in_bib:
        print(f"\n## ❌ Cited but not in .bib ({len(cited_not_in_bib)})")
        for k in sorted(cited_not_in_bib):
            print(f"  - {k}")

    if bib_issues:
        print(f"\n## ⚠️ Bib entries with missing required fields ({len(bib_issues)})")
        for k, msg in bib_issues:
            print(f"  - {k}: {msg}")

    if in_bib_not_cited:
        print(f"\n## ℹ️ In .bib but never cited ({len(in_bib_not_cited)}) — informational only")
        for k in sorted(list(in_bib_not_cited)[:20]):
            print(f"  - {k}")
        if len(in_bib_not_cited) > 20:
            print(f"  … and {len(in_bib_not_cited) - 20} more")

    if apa_keys:
        print(f"\n## APA inline citations found: {len(apa_keys)} (informational)")
        for k in sorted(apa_keys)[:10]:
            print(f"  - ({k})")
        if len(apa_keys) > 10:
            print(f"  … and {len(apa_keys) - 10} more")

    return 1 if (cited_not_in_bib or bib_issues) else 0


if __name__ == "__main__":
    sys.exit(main())
