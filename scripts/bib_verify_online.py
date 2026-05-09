#!/usr/bin/env python3
"""Verify .bib entries against Crossref and OpenAlex.

For each entry, queries Crossref first, then OpenAlex as fallback,
returns a similarity score, and flags entries with low scores
as candidates for manual review (e.g. fictitious or wrong references).

Examples:
    bib_verify_online.py reference.bib
    bib_verify_online.py reference.bib --keys Falcone2008Fiducia,Castelfranchi2017RischioFidarsi
    bib_verify_online.py reference.bib --threshold 0.5 --output audit.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)

try:
    from pybtex.database import parse_file
except ImportError:
    print("ERROR: pybtex not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


CACHE_DIR = Path(".cache/bib-verify")
CROSSREF_API = "https://api.crossref.org/works"
OPENALEX_API = "https://api.openalex.org/works"


def normalize(s: str) -> str:
    return " ".join(s.lower().split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def load_env() -> tuple[str, str]:
    if load_dotenv:
        for parent in [Path.cwd(), *Path.cwd().parents]:
            env_path = parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                break
    crossref_ua = os.getenv("CROSSREF_USER_AGENT", "article-revision-skill/1.0")
    openalex_ua = os.getenv("OPENALEX_USER_AGENT", "article-revision-skill/1.0")
    return crossref_ua, openalex_ua


def cache_get(key: str) -> dict | None:
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def cache_set(key: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def query_crossref(title: str, authors: list[str], year: str, ua: str) -> dict | None:
    params = {
        "query.title": title,
        "rows": 3,
    }
    if authors:
        params["query.author"] = " ".join(authors[:2])
    headers = {"User-Agent": ua}
    try:
        r = requests.get(CROSSREF_API, params=params, headers=headers, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}
    data = r.json()
    items = data.get("message", {}).get("items", [])
    if not items:
        return None
    best = items[0]
    best_title = (best.get("title") or [""])[0]
    score = similarity(title, best_title)
    return {
        "source": "crossref",
        "score": score,
        "matched_title": best_title,
        "matched_year": (best.get("issued", {}).get("date-parts", [[None]]) or [[None]])[0][0],
        "doi": best.get("DOI"),
        "url": best.get("URL"),
    }


def query_openalex(title: str, authors: list[str], year: str, ua: str) -> dict | None:
    params = {
        "search": title,
        "per-page": 3,
    }
    headers = {"User-Agent": ua}
    try:
        r = requests.get(OPENALEX_API, params=params, headers=headers, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}
    data = r.json()
    results = data.get("results", [])
    if not results:
        return None
    best = results[0]
    best_title = best.get("title") or ""
    score = similarity(title, best_title)
    return {
        "source": "openalex",
        "score": score,
        "matched_title": best_title,
        "matched_year": best.get("publication_year"),
        "doi": best.get("doi"),
        "url": best.get("id"),
    }


def verify_entry(key: str, entry, crossref_ua: str, openalex_ua: str) -> dict:
    cached = cache_get(key)
    if cached:
        return cached

    title = entry.fields.get("title", "").strip("{}")
    year = entry.fields.get("year", "")
    authors = []
    for p in entry.persons.get("author", []):
        if p.last_names:
            authors.append(p.last_names[0])

    cr = query_crossref(title, authors, year, crossref_ua) or {}
    oa = query_openalex(title, authors, year, openalex_ua) or {}

    result = {
        "key": key,
        "title": title,
        "authors": authors,
        "year": year,
        "crossref": cr,
        "openalex": oa,
    }
    cache_set(key, result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify .bib entries online.")
    ap.add_argument("bib", type=Path)
    ap.add_argument("--keys", default="", help="Comma-separated subset of keys to verify (default: all)")
    ap.add_argument("--threshold", type=float, default=0.6, help="Score below which an entry is flagged")
    ap.add_argument("--output", type=Path, default=None, help="Write markdown audit to this path")
    ap.add_argument("--rate-limit", type=float, default=1.0, help="Seconds between API calls")
    args = ap.parse_args()

    if not args.bib.exists():
        print(f"ERROR: bib not found: {args.bib}", file=sys.stderr)
        return 2

    crossref_ua, openalex_ua = load_env()
    bib_data = parse_file(str(args.bib))

    keys_filter = {k.strip() for k in args.keys.split(",") if k.strip()}
    keys = list(bib_data.entries.keys())
    if keys_filter:
        keys = [k for k in keys if k in keys_filter]

    results: list[dict] = []
    for i, key in enumerate(keys, 1):
        print(f"[{i}/{len(keys)}] {key} …", file=sys.stderr)
        try:
            result = verify_entry(key, bib_data.entries[key], crossref_ua, openalex_ua)
            results.append(result)
            time.sleep(args.rate_limit)
        except Exception as e:
            print(f"  error: {e}", file=sys.stderr)
            results.append({"key": key, "error": str(e)})

    flagged = []
    for r in results:
        if "error" in r:
            continue
        cr_score = r.get("crossref", {}).get("score", 0)
        oa_score = r.get("openalex", {}).get("score", 0)
        best_score = max(cr_score, oa_score)
        if best_score < args.threshold:
            flagged.append((r, best_score))

    print()
    print(f"# Audit: {len(results)} entries verified")
    print(f"# Flagged (score < {args.threshold}): {len(flagged)}")
    print()
    for r, score in flagged:
        print(f"## ❌ {r['key']} (best score: {score:.2f})")
        print(f"  Title: {r['title']}")
        print(f"  Authors: {', '.join(r['authors'])} ({r['year']})")
        cr = r.get("crossref") or {}
        oa = r.get("openalex") or {}
        if cr.get("matched_title"):
            print(f"  Crossref best: {cr['matched_title']} ({cr.get('matched_year')}) — score {cr['score']:.2f}")
        if oa.get("matched_title"):
            print(f"  OpenAlex best: {oa['matched_title']} ({oa.get('matched_year')}) — score {oa['score']:.2f}")
        print()

    if args.output:
        lines = [f"# Bibliography online audit\n", f"- entries verified: {len(results)}\n", f"- flagged: {len(flagged)}\n\n"]
        for r, score in flagged:
            lines.append(f"## {r['key']} (score {score:.2f})\n")
            lines.append(f"- title in .bib: *{r['title']}*\n")
            lines.append(f"- authors: {', '.join(r['authors'])} ({r['year']})\n")
            cr = r.get("crossref") or {}
            oa = r.get("openalex") or {}
            if cr.get("matched_title"):
                lines.append(f"- Crossref best: *{cr['matched_title']}* ({cr.get('matched_year')}) — score {cr['score']:.2f} — DOI: {cr.get('doi')}\n")
            if oa.get("matched_title"):
                lines.append(f"- OpenAlex best: *{oa['matched_title']}* ({oa.get('matched_year')}) — score {oa['score']:.2f} — {oa.get('url')}\n")
            lines.append("\n")
        args.output.write_text("".join(lines), encoding="utf-8")
        print(f"\nMarkdown audit written to {args.output}", file=sys.stderr)

    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
