#!/usr/bin/env python3
"""Verify that every frozen passage of the ledger survives verbatim in the article."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path
from typing import Sequence

SECTION = "## Passaggi congelati"
ROW = re.compile(r"^\|\s*(F\d+)\s*\|(.*)$")
BLOCK = re.compile(r"^###\s+(F\d+)\s*(?:—|-)\s*(.*)$")
FENCE = re.compile(r"^```\s*text\s*$")
DIGEST_LENGTH = 12


def normalise(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def digest(text: str) -> str:
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()[:DIGEST_LENGTH]


def flatten(text: str) -> tuple[str, list[int]]:
    """Return the normalised article and the source line of each of its characters."""
    pieces: list[str] = []
    lines: list[int] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for token in unicodedata.normalize("NFC", line).split():
            if pieces:
                pieces.append(" ")
                lines.append(number)
            pieces.append(token)
            lines.extend([number] * len(token))
    return "".join(pieces), lines


def locate(needle: str, flat: str, lines: Sequence[int]) -> list[int]:
    """Return the source line of every occurrence of the normalised needle.

    The search is a plain substring match, so a passage may start or end inside a
    token: freezing «percepite dell'innovazione» finds it even when the article
    writes «dell'innovazione:» with the colon attached.
    """
    if not needle:
        return []
    found: list[int] = []
    start = flat.find(needle)
    while start != -1:
        found.append(lines[start])
        start = flat.find(needle, start + 1)
    return found


def section_of(ledger: str) -> list[str]:
    body = ledger.splitlines()
    try:
        start = next(index for index, line in enumerate(body) if line.strip() == SECTION)
    except StopIteration:
        return []
    for index in range(start + 1, len(body)):
        if body[index].startswith("## "):
            return body[start + 1:index]
    return body[start + 1:]


def parse_rows(lines: Sequence[str]) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in lines:
        match = ROW.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in match.group(2).split("|")]
        rows[match.group(1)] = {
            "section": cells[0] if cells else "",
            "range": cells[1] if len(cells) > 1 else "",
            "digest": cells[3] if len(cells) > 3 else "",
            "state": cells[4] if len(cells) > 4 else "",
        }
    return rows


def parse_blocks(lines: Sequence[str]) -> dict[str, str]:
    blocks: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] | None = None
    for line in lines:
        heading = BLOCK.match(line)
        if heading:
            current, buffer = heading.group(1), None
            continue
        if current is None:
            continue
        if buffer is None:
            if FENCE.match(line.strip()):
                buffer = []
            continue
        if line.strip() == "```":
            blocks[current] = "\n".join(buffer)
            current, buffer = None, None
            continue
        buffer.append(line)
    return blocks


def default_ledger(article: Path) -> Path:
    candidates = sorted(Path.cwd().glob("revisions/*/freeze-ledger.md"))
    if len(candidates) == 1:
        return candidates[0]
    raise SystemExit(
        f"cannot infer the ledger for {article}: pass --ledger explicitly "
        f"({len(candidates)} candidates under revisions/)"
    )


def report(article_text: str, ledger_text: str) -> tuple[list[str], int]:
    lines = section_of(ledger_text)
    rows = parse_rows(lines)
    blocks = parse_blocks(lines)
    flat, flat_lines = flatten(article_text)

    output: list[str] = []
    verified = problems = 0
    for identifier in sorted(set(rows) | set(blocks), key=lambda name: int(name[1:])):
        row = rows.get(identifier)
        text = blocks.get(identifier)
        if row is None:
            output.append(f"{identifier} — ⚠ riga di tabella mancante")
            problems += 1
            continue
        label = f"{identifier} {row['section']}".rstrip()
        if text is None:
            output.append(f"{label} — ⚠ blocco mancante")
            problems += 1
            continue
        if "frozen" not in row["state"]:
            output.append(f"{label} — non verificato (stato {row['state']})")
            continue
        found = digest(text)
        if row["digest"] != found:
            output.append(
                f"{label} — ⚠ hash incoerente (tabella {row['digest'] or '—'}, testo {found})"
            )
            problems += 1
            continue
        hits = locate(normalise(text), flat, flat_lines)
        if not hits:
            output.append(f"{label} — ⚠ stale (testo non trovato)")
            problems += 1
        elif len(hits) > 1:
            output.append(
                f"{label} — ⚠ ambiguo ({len(hits)} occorrenze: righe "
                f"{', '.join(str(hit) for hit in hits)})"
            )
            problems += 1
        else:
            verified += 1
            output.append(f"{label} riga {hits[0]} — ok")

    output.append(f"{verified} passaggi 🔒 verificati · {problems} da sanare")
    return output, (1 if problems else 0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article", type=Path)
    parser.add_argument("--ledger", type=Path, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    ledger = arguments.ledger or default_ledger(arguments.article)
    lines, status = report(
        arguments.article.read_text(encoding="utf-8"),
        ledger.read_text(encoding="utf-8"),
    )
    print("\n".join(lines))
    return status


if __name__ == "__main__":
    sys.exit(main())
