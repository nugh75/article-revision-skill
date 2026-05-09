#!/usr/bin/env python3
"""Character/word counter with editorial-budget awareness.

Examples:
    char_count.py article.md
    char_count.py article.md --exclude bibliography,glossary,appendices
    char_count.py article.md --limit-from-env
    char_count.py article.md --section "## 1 – Introduction"
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


SECTION_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
FRONTMATTER_PATTERN = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
CODE_FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)


def load_env_limit() -> tuple[int | None, str]:
    """Return (limit, unit) from .env. unit is 'chars' or 'words'."""
    if load_dotenv is None:
        return None, "chars"
    # Walk up to find a .env in cwd or ancestors
    for parent in [Path.cwd(), *Path.cwd().parents]:
        env_path = parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            break
    chars = os.getenv("EDITORIAL_LIMIT_CHARS")
    words = os.getenv("EDITORIAL_LIMIT_WORDS")
    if chars:
        return int(chars), "chars"
    if words:
        return int(words), "words"
    return None, "chars"


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_PATTERN.sub("", text, count=1)


def strip_code_fences(text: str) -> str:
    return CODE_FENCE_PATTERN.sub("", text)


def find_section_bounds(text: str, exclude_titles: set[str]) -> list[tuple[int, int]]:
    """Find char ranges to exclude based on section titles (case-insensitive substring match)."""
    matches = list(SECTION_PATTERN.finditer(text))
    excluded_ranges: list[tuple[int, int]] = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip().lower()
        if any(ex.lower() in title for ex in exclude_titles):
            start = m.start()
            # Find next section at same or higher level (smaller `#` count)
            end = len(text)
            for nxt in matches[i + 1 :]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            excluded_ranges.append((start, end))
    return excluded_ranges


def remove_ranges(text: str, ranges: list[tuple[int, int]]) -> str:
    if not ranges:
        return text
    ranges = sorted(ranges)
    out = []
    cursor = 0
    for start, end in ranges:
        out.append(text[cursor:start])
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def count(text: str) -> tuple[int, int]:
    chars = len(text)
    words = len(text.split())
    return chars, words


def main() -> int:
    ap = argparse.ArgumentParser(description="Character/word counter for editorial budgets.")
    ap.add_argument("file", type=Path, help="Markdown file to analyze")
    ap.add_argument(
        "--exclude",
        default="",
        help="Comma-separated section title substrings to exclude (case-insensitive)",
    )
    ap.add_argument(
        "--section",
        default=None,
        help="Count only the named section (exact title or substring match on heading)",
    )
    ap.add_argument(
        "--limit-from-env",
        action="store_true",
        help="Read EDITORIAL_LIMIT_CHARS / EDITORIAL_LIMIT_WORDS from .env",
    )
    ap.add_argument("--strip-code", action="store_true", help="Also strip code fences")
    args = ap.parse_args()

    if not args.file.exists():
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 2

    text = args.file.read_text(encoding="utf-8")
    text = strip_frontmatter(text)
    if args.strip_code:
        text = strip_code_fences(text)

    if args.section:
        # Keep only the named section
        m = re.search(rf"^#{{1,6}}\s+.*{re.escape(args.section)}.*$", text, re.MULTILINE | re.IGNORECASE)
        if not m:
            print(f"ERROR: section '{args.section}' not found", file=sys.stderr)
            return 2
        start = m.start()
        # Find next sibling or higher-level heading
        level_match = re.match(r"^(#{1,6})", text[start:])
        level = len(level_match.group(1)) if level_match else 1
        rest = text[m.end() :]
        next_heading = re.search(rf"^#{{1,{level}}}\s+", rest, re.MULTILINE)
        end = m.end() + (next_heading.start() if next_heading else len(rest))
        text = text[start:end]

    excludes = {e.strip() for e in args.exclude.split(",") if e.strip()}
    if excludes:
        ranges = find_section_bounds(text, excludes)
        text = remove_ranges(text, ranges)

    chars, words = count(text)
    print(f"chars: {chars}")
    print(f"words: {words}")

    if args.limit_from_env:
        limit, unit = load_env_limit()
        if limit is None:
            print("WARN: no EDITORIAL_LIMIT_* in .env", file=sys.stderr)
        else:
            measured = chars if unit == "chars" else words
            delta = measured - limit
            pct = (measured / limit) * 100 if limit else 0
            sign = "+" if delta >= 0 else ""
            print(f"limit ({unit}): {limit}")
            print(f"delta: {sign}{delta} ({pct:.1f}% of limit)")
            return 1 if delta > 0 else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
