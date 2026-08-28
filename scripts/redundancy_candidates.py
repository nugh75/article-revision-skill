#!/usr/bin/env python3
"""Rank paragraph pairs for a human redundancy audit without editing the source."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


CITATION_RE = re.compile(r"@([A-Za-z0-9_:.+/-]+)")
CITATION_GROUP_RE = re.compile(r"\[[^\]]*@[^\]]*\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
FENCE_RE = re.compile(r"^\s*(```|~~~)")

STOPWORDS = {
    "a", "ad", "al", "alla", "alle", "anche", "che", "con", "da", "dal",
    "dalla", "delle", "di", "e", "è", "gli", "i", "il", "in", "la", "le",
    "lo", "ma", "nel", "nella", "o", "per", "più", "quale", "questa",
    "questo", "si", "sono", "su", "tra", "un", "una", "the", "a", "an",
    "and", "as", "at", "by", "for", "from", "in", "is", "it", "of", "on",
    "or", "that", "this", "to", "with",
}
MARKERS = {
    "negation": {
        "non", "nessun", "nessuna", "nessuno", "senza", "mai", "not", "no",
        "never", "without", "cannot", "neither",
    },
    "modality": {
        "può", "possono", "potrebbe", "potrebbero", "dovrebbe", "dovrebbero",
        "deve", "devono", "possibile", "probabile", "may", "might", "could",
        "should", "must", "possible", "probable",
    },
    "causality": {
        "causa", "causano", "determina", "determinano", "produce", "producono",
        "conduce", "conducono", "comporta", "comportano", "causes", "caused",
        "determines", "produces", "leads", "results",
    },
    "qualification": {
        "solo", "soltanto", "parzialmente", "limite", "limiti", "tuttavia",
        "se", "quando", "only", "partly", "partially", "limit", "limits",
        "however", "if", "when",
    },
}
OLLAMA_URL_KEYS = (
    "ARTICLE_REVISION_OLLAMA_URL",
    "OLLAMA_BASE_URL",
    "OLLAMA_HOST",
)


@dataclass(frozen=True)
class Paragraph:
    paragraph_id: str
    order: int
    section_path: list[str]
    line_start: int
    line_end: int
    text: str
    comparison_text: str
    citations: list[str]
    word_count: int

    @property
    def locator(self) -> str:
        return f"lines {self.line_start}-{self.line_end}"

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["locator"] = self.locator
        return result


def strip_markdown(text: str) -> str:
    text = CITATION_GROUP_RE.sub(" ", text)
    text = CITATION_RE.sub(" ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[`*_~>#]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", strip_markdown(text)).casefold()


def content_tokens(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_RE.findall(normalize_text(text))
        if len(token) > 1 and token not in STOPWORDS
    ]


def parse_markdown(
    text: str,
    line_start: int = 1,
    line_end: int | None = None,
) -> list[Paragraph]:
    """Extract prose paragraphs while retaining heading and source-line context."""
    lines = text.splitlines()
    scope_end = len(lines) if line_end is None else min(line_end, len(lines))
    headings: list[str] = []
    paragraphs: list[Paragraph] = []
    buffer: list[str] = []
    buffer_start = 0
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    in_fence = False

    def flush(end_line: int) -> None:
        nonlocal buffer, buffer_start
        if not buffer:
            return
        source_text = "\n".join(buffer).strip()
        buffer = []
        if not source_text:
            return
        comparison_text = strip_markdown(source_text)
        citations = list(dict.fromkeys(CITATION_RE.findall(source_text)))
        order = len(paragraphs) + 1
        digest = hashlib.sha256(normalize_text(source_text).encode("utf-8")).hexdigest()[:8]
        paragraphs.append(
            Paragraph(
                paragraph_id=f"P{order:03d}-{digest}",
                order=order,
                section_path=headings.copy(),
                line_start=buffer_start,
                line_end=end_line,
                text=source_text,
                comparison_text=comparison_text,
                citations=citations,
                word_count=len(TOKEN_RE.findall(comparison_text)),
            )
        )

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if in_frontmatter:
            if number > 1 and stripped == "---":
                in_frontmatter = False
            continue

        fence = FENCE_RE.match(line)
        if fence:
            flush(number - 1)
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = HEADING_RE.match(line)
        if heading:
            flush(number - 1)
            level = len(heading.group(1))
            headings = headings[: level - 1]
            headings.append(strip_markdown(heading.group(2)))
            continue

        structural_line = (
            not stripped
            or stripped.startswith("|")
            or bool(re.match(r"^\s*\[\^[^\]]+\]:", line))
        )
        if structural_line:
            flush(number - 1)
            continue

        if not buffer:
            buffer_start = number
        buffer.append(line)

    flush(len(lines))
    return [
        paragraph
        for paragraph in paragraphs
        if paragraph.line_end >= line_start and paragraph.line_start <= scope_end
    ]


def cosine_counts(left: Sequence[str], right: Sequence[str]) -> float:
    left_counts = Counter(left)
    right_counts = Counter(right)
    dot = sum(value * right_counts[token] for token, value in left_counts.items())
    left_norm = math.sqrt(sum(value * value for value in left_counts.values()))
    right_norm = math.sqrt(sum(value * value for value in right_counts.values()))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def jaccard(left: set[object], right: set[object]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def lexical_similarity(left: Paragraph, right: Paragraph) -> float:
    left_tokens = content_tokens(left.comparison_text)
    right_tokens = content_tokens(right.comparison_text)
    token_score = jaccard(set(left_tokens), set(right_tokens))
    count_score = cosine_counts(left_tokens, right_tokens)
    left_bigrams = set(zip(left_tokens, left_tokens[1:]))
    right_bigrams = set(zip(right_tokens, right_tokens[1:]))
    bigram_score = jaccard(left_bigrams, right_bigrams)
    return 0.35 * token_score + 0.45 * count_score + 0.20 * bigram_score


def cosine_vectors(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions differ")
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def marker_flags(left: Paragraph, right: Paragraph) -> list[str]:
    left_tokens = set(TOKEN_RE.findall(normalize_text(left.comparison_text)))
    right_tokens = set(TOKEN_RE.findall(normalize_text(right.comparison_text)))
    flags: list[str] = []
    for name, markers in MARKERS.items():
        if bool(left_tokens & markers) != bool(right_tokens & markers):
            flags.append(f"{name}-mismatch")
    return flags


def rank_candidate_pairs(
    paragraphs: Sequence[Paragraph],
    embeddings: Sequence[Sequence[float]] | None = None,
    lexical_threshold: float = 0.34,
    semantic_threshold: float = 0.82,
    min_words: int = 8,
    max_pairs: int = 100,
) -> list[dict[str, object]]:
    """Return ranked candidates; classification and editorial action stay human-led."""
    if embeddings is not None and len(embeddings) != len(paragraphs):
        raise ValueError("one embedding is required for each paragraph")

    candidates: list[dict[str, object]] = []
    for left_index, left in enumerate(paragraphs):
        if left.word_count < min_words:
            continue
        for right_index in range(left_index + 1, len(paragraphs)):
            right = paragraphs[right_index]
            if right.word_count < min_words:
                continue
            lexical = lexical_similarity(left, right)
            semantic = (
                cosine_vectors(embeddings[left_index], embeddings[right_index])
                if embeddings is not None
                else None
            )
            lexical_match = lexical >= lexical_threshold
            semantic_match = semantic is not None and semantic >= semantic_threshold
            if not lexical_match and not semantic_match:
                continue

            left_terms = set(content_tokens(left.comparison_text))
            right_terms = set(content_tokens(right.comparison_text))
            if lexical_match and semantic_match:
                source = "lexical+semantic"
            elif semantic_match:
                source = "semantic"
            else:
                source = "lexical"
            left_citations = set(left.citations)
            right_citations = set(right.citations)
            candidates.append(
                {
                    "left_id": left.paragraph_id,
                    "right_id": right.paragraph_id,
                    "left_locator": left.locator,
                    "right_locator": right.locator,
                    "left_section": left.section_path,
                    "right_section": right.section_path,
                    "lexical_similarity": round(lexical, 6),
                    "semantic_similarity": round(semantic, 6) if semantic is not None else None,
                    "candidate_source": source,
                    "review_flags": marker_flags(left, right),
                    "citations_left_only": sorted(left_citations - right_citations),
                    "citations_right_only": sorted(right_citations - left_citations),
                    "unique_terms_left": sorted(left_terms - right_terms)[:20],
                    "unique_terms_right": sorted(right_terms - left_terms)[:20],
                }
            )

    candidates.sort(
        key=lambda pair: max(
            float(pair["lexical_similarity"]),
            float(pair["semantic_similarity"] or 0.0),
        ),
        reverse=True,
    )
    return candidates[:max_pairs]


def ollama_embeddings(
    texts: Sequence[str],
    model: str,
    base_url: str,
    timeout: float,
) -> list[list[float]]:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/embed",
        data=json.dumps({"model": model, "input": list(texts)}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        raise ValueError("Ollama response does not contain one embedding per paragraph")
    return embeddings


def normalize_ollama_url(value: str) -> str:
    normalized = value.strip().strip("'\"").rstrip("/")
    if not re.match(r"^https?://", normalized, flags=re.IGNORECASE):
        normalized = f"http://{normalized}"
    return re.sub(r"/v1$", "", normalized, flags=re.IGNORECASE)


def project_env_values(source: Path) -> dict[str, str]:
    """Read only Ollama URL keys from the closest project .env."""
    resolved = source.resolve()
    for directory in (resolved.parent, *resolved.parents):
        env_path = directory / ".env"
        if not env_path.is_file():
            continue
        values: dict[str, str] = {}
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            key, separator, value = line.partition("=")
            if separator and key.strip() in OLLAMA_URL_KEYS:
                values[key.strip()] = value.strip()
        if values:
            return values
    return {}


def ollama_url_candidates(source: Path, explicit: str | None) -> list[str]:
    if explicit:
        return [normalize_ollama_url(explicit)]

    project_values = project_env_values(source)
    values: list[str] = []
    for key in OLLAMA_URL_KEYS:
        if project_values.get(key):
            values.append(project_values[key])
        if os.environ.get(key):
            values.append(os.environ[key])
    values.append("http://127.0.0.1:11434")
    return list(dict.fromkeys(normalize_ollama_url(value) for value in values))


def line_range(value: str) -> tuple[int, int | None]:
    match = re.fullmatch(r"([1-9][0-9]*):([1-9][0-9]*)?", value)
    if not match:
        raise argparse.ArgumentTypeError("expected START:END, for example 40:180")
    start = int(match.group(1))
    end = int(match.group(2)) if match.group(2) else None
    if end is not None and end < start:
        raise argparse.ArgumentTypeError("END must be greater than or equal to START")
    return start, end


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank possible redundant paragraph pairs without editing the Markdown source."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--lines", type=line_range, default=(1, None), metavar="START:END")
    parser.add_argument("--backend", choices=("auto", "lexical", "ollama"), default="auto")
    parser.add_argument("--model", default="qwen3-embedding:8b")
    parser.add_argument(
        "--ollama-url",
        help=(
            "Ollama base URL. Otherwise discover ARTICLE_REVISION_OLLAMA_URL, "
            "OLLAMA_BASE_URL, or OLLAMA_HOST from the closest project .env and environment."
        ),
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--lexical-threshold", type=float, default=0.34)
    parser.add_argument(
        "--semantic-threshold",
        type=float,
        default=0.0,
        help=(
            "Minimum cosine similarity for semantic candidates. The uncalibrated "
            "default keeps a max-pairs-capped ranked queue instead of treating a "
            "model-specific score as an editorial cutoff."
        ),
    )
    parser.add_argument("--min-words", type=int, default=8)
    parser.add_argument("--max-pairs", type=int, default=100)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.lexical_threshold <= 1 or not 0 <= args.semantic_threshold <= 1:
        raise SystemExit("similarity thresholds must be between 0 and 1")
    if args.min_words < 1 or args.max_pairs < 1:
        raise SystemExit("--min-words and --max-pairs must be positive")
    try:
        source_text = args.source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"error: cannot read {args.source}: {error}", file=sys.stderr)
        return 2

    start, end = args.lines
    paragraphs = parse_markdown(source_text, start, end)
    embeddings: list[list[float]] | None = None
    semantic_status = "lexical"
    if args.backend in {"auto", "ollama"} and paragraphs:
        failures: list[tuple[str, Exception]] = []
        for ollama_url in ollama_url_candidates(args.source, args.ollama_url):
            try:
                embeddings = ollama_embeddings(
                    [paragraph.comparison_text for paragraph in paragraphs],
                    args.model,
                    ollama_url,
                    args.timeout,
                )
                semantic_status = f"ollama:{args.model}@{ollama_url}"
                break
            except (OSError, ValueError, TimeoutError, urllib.error.URLError) as error:
                failures.append((ollama_url, error))
        if embeddings is None:
            if args.backend == "ollama":
                attempted = ", ".join(url for url, _ in failures)
                last_error = failures[-1][1] if failures else RuntimeError("no endpoint found")
                print(
                    f"error: Ollama embedding failed ({attempted}): {last_error}",
                    file=sys.stderr,
                )
                return 2
            error_name = type(failures[-1][1]).__name__ if failures else "NoEndpoint"
            semantic_status = f"fallback-lexical:{error_name}"

    pairs = rank_candidate_pairs(
        paragraphs,
        embeddings=embeddings,
        lexical_threshold=args.lexical_threshold,
        semantic_threshold=args.semantic_threshold,
        min_words=args.min_words,
        max_pairs=args.max_pairs,
    )
    payload = {
        "source": str(args.source),
        "scope_lines": [start, end],
        "semantic_status": semantic_status,
        "thresholds": {
            "lexical": args.lexical_threshold,
            "semantic": args.semantic_threshold,
        },
        "paragraphs": [paragraph.to_dict() for paragraph in paragraphs],
        "candidate_pairs": pairs,
        "notice": "Similarity ranks candidates only; it does not classify redundancy or authorize edits.",
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
