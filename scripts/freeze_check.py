#!/usr/bin/env python3
"""Verify that every frozen passage of the ledger survives verbatim in the article."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path
from typing import NamedTuple, Sequence

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


class Finding(NamedTuple):
    state: str
    message: str
    occurrences: int = 0


def inspect_passages(article_text: str, ledger_text: str) -> dict[str, Finding]:
    lines = section_of(ledger_text)
    rows = parse_rows(lines)
    blocks = parse_blocks(lines)
    flat, flat_lines = flatten(article_text)

    findings: dict[str, Finding] = {}
    for identifier in sorted(set(rows) | set(blocks), key=lambda name: int(name[1:])):
        row = rows.get(identifier)
        text = blocks.get(identifier)
        if row is None:
            findings[identifier] = Finding("invalid", f"{identifier} — ⚠ riga di tabella mancante")
            continue
        label = f"{identifier} {row['section']}".rstrip()
        if text is None:
            findings[identifier] = Finding("invalid", f"{label} — ⚠ blocco mancante")
            continue
        if "frozen" not in row["state"]:
            findings[identifier] = Finding("inactive", f"{label} — non verificato (stato {row['state']})")
            continue
        found = digest(text)
        if row["digest"] != found:
            findings[identifier] = Finding(
                "invalid", f"{label} — ⚠ hash incoerente (tabella {row['digest'] or '—'}, testo {found})"
            )
            continue
        hits = locate(normalise(text), flat, flat_lines)
        if not hits:
            findings[identifier] = Finding("stale", f"{label} — ⚠ stale (testo non trovato)")
        elif len(hits) > 1:
            findings[identifier] = Finding(
                "ambiguous",
                f"{label} — ⚠ ambiguo ({len(hits)} occorrenze: righe "
                f"{', '.join(str(hit) for hit in hits)})",
                len(hits),
            )
        else:
            findings[identifier] = Finding("ok", f"{label} riga {hits[0]} — ok", 1)
    return findings


def report(article_text: str, ledger_text: str) -> tuple[list[str], int]:
    findings = inspect_passages(article_text, ledger_text).values()
    output = [finding.message for finding in findings]
    verified = sum(finding.state == "ok" for finding in findings)
    problems = sum(finding.state not in {"ok", "inactive"} for finding in findings)
    output.append(f"{verified} passaggi 🔒 verificati · {problems} da sanare")
    return output, int(problems > 0)


def report_edit(before: str, candidate: str, ledger: str) -> tuple[list[str], int]:
    original = inspect_passages(before, ledger)
    proposed = inspect_passages(candidate, ledger)
    output = []
    blocked = False
    for identifier, finding in proposed.items():
        prior = original[identifier]
        if finding.state in {"ok", "inactive"} and prior.state != "ambiguous":
            continue
        if finding.state == "invalid":
            output.append(f"Ledger non valido già prima della modifica — {finding.message}")
            blocked = True
        elif (finding.state, finding.occurrences) == (prior.state, prior.occurrences):
            output.append(f"Problema preesistente — {finding.message}")
        else:
            output.append(f"Problema introdotto dalla modifica — {finding.message}")
            blocked = True
    output.append("Verifica della modifica fallita." if blocked else "Verifica della modifica riuscita.")
    return output, int(blocked)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article", type=Path)
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument("--before", type=Path, help="Compare with an exact pre-edit snapshot")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    ledger = arguments.ledger or default_ledger(arguments.article)
    candidate = arguments.article.read_text(encoding="utf-8")
    ledger_text = ledger.read_text(encoding="utf-8")
    if arguments.before:
        lines, status = report_edit(arguments.before.read_text(encoding="utf-8"), candidate, ledger_text)
    else:
        lines, status = report(candidate, ledger_text)
    print("\n".join(lines))
    return status


if __name__ == "__main__":
    sys.exit(main())
