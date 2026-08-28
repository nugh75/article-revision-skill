#!/usr/bin/env python3
"""Validate lifecycle scenarios, internal pointers, compatibility docs, and mirrors."""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EFFECTS = {
    "chat-only": dict(writes_target=False, bump=False, task=False, ledger=False, sync=False),
    "direct-apply": dict(writes_target=True, bump=False, task=False, ledger=False, sync=False),
    "tracked-round": dict(writes_target=True, bump=True, task=True, ledger=True, sync=True),
    "auto": dict(writes_target=True, bump=True, task=True, ledger=True, sync=True),
}
GIT_EVENTS = {"dedicated-yes", "explicit-commit-push", "handoff-git", "auto-git"}
POINTER = re.compile(r"(?:workflow|templates|references|scripts)/[A-Za-z0-9._/-]+")
STALE_PHRASES = (
    "Mandatory bump at session start",
    "commit and push the handoff state",
    "requested handoff, or confirmed closure authorizes",
    "/r-auto uses it automatically",
    "/r-auto remains automatic",
)


def route(case: dict[str, object]) -> dict[str, object]:
    kind = case["kind"]
    if kind in {"audit", "draft", "organize", "structure-audit", "redundancy-audit"}:
        mode = "chat-only"
    elif kind == "auto":
        mode = "auto"
    elif case["tracking_requested"] or kind in {"reviewer", "iterative", "structural-edit"}:
        mode = "tracked-round"
    elif kind == "direct-edit" and case["target_named"]:
        mode = "direct-apply"
    else:
        raise ValueError(f"ambiguous route: {case['name']}")

    return {"mode": mode, **EFFECTS[mode], "git": bool(case["git_authorized"])}


def check_cases(errors: list[str]) -> None:
    data = json.loads((ROOT / "tests/lifecycle-cases.json").read_text(encoding="utf-8"))
    for case in data["routes"]:
        actual = route(case)
        if actual != case["expected"]:
            errors.append(f"route {case['name']}: {actual} != {case['expected']}")
    for case in data["git_authorization"]:
        actual = case["event"] in GIT_EVENTS
        if actual != case["expected"]:
            errors.append(f"git event {case['event']}: {actual} != {case['expected']}")


def check_pointers(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for pointer in POINTER.findall(path.read_text(encoding="utf-8")):
            candidate = ROOT / pointer.rstrip(".,:;)")
            if not candidate.exists():
                errors.append(f"missing pointer in {path.relative_to(ROOT)}: {pointer}")


def check_stale_phrases(errors: list[str]) -> None:
    paths = [*ROOT.rglob("*.md"), ROOT / ".env.example"]
    for path in paths:
        if not path.exists() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in STALE_PHRASES:
            if phrase.casefold() in text.casefold():
                errors.append(f"stale phrase in {path.relative_to(ROOT)}: {phrase}")


def check_compat(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_compat_docs.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append(result.stdout.strip() or result.stderr.strip())


def check_redundancy_audit(errors: list[str]) -> None:
    expected_names = {
        "near-identical paragraphs",
        "distant paraphrase",
        "technical term with different claims",
        "introduction and conclusion reprise",
        "semantic safeguard mismatch",
        "same claim with new evidence",
        "local qwen preliminary review",
        "read-only audit",
        "cut preservation packet",
    }
    cases_path = ROOT / "tests/redundancy-cases.json"
    try:
        cases = json.loads(cases_path.read_text(encoding="utf-8"))["cases"]
    except (OSError, KeyError, json.JSONDecodeError) as error:
        errors.append(f"invalid redundancy cases: {error}")
        return
    names = {case.get("name") for case in cases}
    if names != expected_names or any("input" not in case for case in cases):
        errors.append("redundancy cases must define the nine named behavioural scenarios")

    result = subprocess.run(
        [sys.executable, str(ROOT / "tests/test_redundancy_candidates.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append(result.stdout.strip() or result.stderr.strip())


def check_mirror(mirror: Path, errors: list[str]) -> None:
    def files_under(root: Path) -> dict[Path, Path]:
        files: dict[Path, Path] = {}
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            if (
                path.is_dir()
                or ".git" in relative.parts
                or "__pycache__" in relative.parts
                or path.suffix == ".pyc"
            ):
                continue
            files[relative] = path
        return files

    source_files = files_under(ROOT)
    mirror_files = files_under(mirror)
    for relative, source in source_files.items():
        target = mirror / relative
        if not target.is_file():
            errors.append(f"mirror missing: {relative}")
        elif not filecmp.cmp(source, target, shallow=False):
            errors.append(f"mirror differs: {relative}")
    for relative in sorted(mirror_files.keys() - source_files.keys()):
        errors.append(f"mirror has extra file: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mirror", type=Path)
    args = parser.parse_args()
    errors: list[str] = []

    check_cases(errors)
    check_pointers(errors)
    check_stale_phrases(errors)
    check_compat(errors)
    check_redundancy_audit(errors)
    if args.mirror:
        check_mirror(args.mirror.resolve(), errors)

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("contract=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
