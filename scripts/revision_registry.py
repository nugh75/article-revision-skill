#!/usr/bin/env python3
"""Index revision work; archive explicit closures, retaining deferred work."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote

CLOSED = {"completed", "closed", "absorbed", "superseded", "applied",
          "completato", "applicato", "applicata", "superato"}
HISTORY = {"diffs", "final-sheets", "automations"}
GENERATED = {"TASKS.md", "ARCHIVE.md", "INDEX.md"}
PROTECTED = {"freeze-ledger.md", "backlog-promesse-non-sviluppate.md", "text_graph_report.md"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(text):
    if not text.startswith("---\n"):
        return {}
    header = text.split("---", 2)[1]
    return dict(re.findall(r"^([\w-]+):\s*(.*)$", header, re.M))


def declared_state(text):
    meta = metadata(text)
    raw = meta.get("status", meta.get("stato", "da-verificare"))
    words = re.sub(r"[*`\"']", "", raw).split()
    return words[0].lower() if words else "da-verificare"


def read_json(path, fallback):
    return json.loads(path.read_text()) if path.exists() else fallback


def write_if_changed(path, text):
    if not path.exists() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(text)
        temporary.replace(path)


def inventory(root, slug):
    base = root / "revisions" / slug
    decisions = read_json(base / "registry-decisions.json", {})
    manifest = read_json(base / "archive-manifest.json", {})
    reverse = {v["path"]: k for k, v in manifest.items()}
    records = []
    for folder in (base, root / "revisions/self"):
        for path in sorted(folder.rglob("*.md")):
            if path.is_symlink() or path.name in GENERATED:
                continue
            rel = path.relative_to(root).as_posix()
            origin = reverse.get(rel, rel)
            text = path.read_text()
            decision = decisions.get(origin, {})
            state = decision.get("status", declared_state(text))
            task = path.name.startswith("task-")
            historical = bool(set(Path(origin).parts) & HISTORY)
            archived = rel in reverse
            records.append(dict(path=rel, origin=origin, text=text, status=state,
                                task=task, archived=archived,
                                evidence=decision.get("evidence", ""),
                                eligible=(state in CLOSED or historical) and not archived
                                and path.name not in PROTECTED))
    return records, manifest


def link(path, base, label=None):
    target = quote(os.path.relpath(path, base), safe="/-._")
    return f"[{label or Path(path).name}]({target})"


def report(root, slug, records, manifest):
    base = Path("revisions") / slug
    versions = [(int(m[1]), p) for p in (root / "articles/versions").glob("article-v*.md")
                if (m := re.match(r"article-v(\d+)-", p.name))]
    active = max(versions, default=(0, None), key=lambda x: x[0])[1]
    lines = ["# Attività di revisione", "",
             "Generato da `revision_registry.py refresh`; modificare le fonti, poi rigenerare.",
             "Gli stati mancanti restano da verificare. Archiviare una sessione non chiude i suoi rinvii.", ""]
    if active:
        lines += ["Versione attiva: " + link(active.relative_to(root), base), ""]
    source_digest = hashlib.sha256()
    for r in records:
        source_digest.update((r["path"] + r["text"] + r["status"] + r["evidence"]).encode())
    if active:
        source_digest.update(active.read_bytes())
    lines += [f"<!-- sources-sha256: {source_digest.hexdigest()} -->", ""]
    groups = [
        ("Task aperti o da riconciliare", [r for r in records if r["task"] and r["status"] not in CLOSED]),
        ("Proposte e materiali da verificare", [r for r in records if not r["task"]
         and not r["archived"] and not r["eligible"]
         and Path(r["path"]).parent != base]),
    ]
    for title, rows in groups:
        lines += [f"## {title} ({len(rows)})", ""]
        for r in rows:
            lines += [f"- {link(r['path'], base)} — **{r['status']}**"]
            next_action = re.findall(r"^- \*\*Prossima azione esatta\*\*:\s*(.*)", r["text"], re.M)
            if next_action:
                lines += ["  Azione registrata (verificare sulla versione attiva): " + next_action[-1]]
        lines += [""]
    ledger = root / base / "freeze-ledger.md"
    lines += ["## Ledger e promesse", ""]
    for name in ("freeze-ledger.md", "backlog-promesse-non-sviluppate.md"):
        if (root / base / name).exists():
            lines += [f"- {link(base / name, base)} — fonte autorevole; gli stati non vengono modificati dall'archivio."]
    if ledger.exists():
        # Only current rows, not the append-only history below them.
        for line in ledger.read_text().splitlines():
            cells = [c.strip() for c in line.split("|")]
            if len(cells) == 10 and re.search(r"\b(open|wip)\b", cells[6]):
                lines += [f"- {cells[1]} — {cells[6]}: {cells[8]}"]
    lines += ["", "## Segnaposto nella versione attiva", ""]
    if active:
        markers = [(n, t) for n, t in enumerate(active.read_text().splitlines(), 1) if "DA-SVILUPPARE" in t]
        lines += [f"- Riga {n}: `{t.strip()}`" for n, t in markers] or ["Nessun marcatore `DA-SVILUPPARE`."]
    lines += ["", "## Rinvii registrati nelle sessioni (da riconciliare, anche se archiviate)", "",
              "Estratti storici, non un elenco di obblighi confermati: verificare decisioni successive e testo attivo.", ""]
    for r in records:
        if not r["task"]:
            continue
        notes = re.findall(r"^- \*\*(?:Rinviati|Da considerare|Decisioni pendenti)\*\*:\s*(.+)$", r["text"], re.M)
        notes = [n for n in notes if not re.match(r"^(?:[—–-]|0\b|nessun[ao]?\b)", n, re.I)]
        if notes:
            lines += [f"- {link(r['path'], base)}: " + " · ".join(notes)]
    lines += ["", "## Segnalazioni residue negli artefatti archiviati", "",
              "Richiami storici da confrontare con decisioni successive; non certificano un problema ancora presente.", ""]
    for r in records:
        if r["task"] or not r["archived"]:
            continue
        flags = [line.strip() for line in r["text"].splitlines()
                 if re.match(r"^\s*(?:[-*] |\d+\. )", line)
                 and re.search(r"(?i)da verificare|da confermare|non verificat|fuori scope|rinviat|rimandat|^- \[ \]", line)]
        if flags:
            lines += [f"- {link(r['path'], base)} — {len(flags)} segnalazioni storiche da riconciliare."]
    lines += ["", f"Archivio: {len(manifest)} file. Candidati ancora da archiviare: {sum(r['eligible'] for r in records)}.",
              "Vedi [catalogo dell'archivio](ARCHIVE.md).", ""]
    archive = ["# Archivio delle revisioni", "", "I percorsi precedenti restano consultabili in `archive-manifest.json`.",
               "Le tracce di esecuzione e i diff sono storici: la loro archiviazione non certifica la risoluzione dei rilievi.", ""]
    for old, entry in sorted(manifest.items()):
        archive += [f"- {link(entry['path'], base)} — origine: `{old}`; criterio: {entry['reason']}."]
    return "\n".join(lines), "\n".join(archive) + "\n"


def relocate_links(text, old_file, new_file, moves, root):
    # Repair working Markdown links before replacing repository-relative prose references.
    def replace(match):
        target = unquote(match[2])
        path, sep, anchor = target.partition("#")
        if not path or re.match(r"[a-zA-Z]+://", path):
            return match[0]
        absolute = (old_file.parent / path).resolve()
        if not absolute.is_relative_to(root) or not absolute.exists():
            return match[0]
        relative = absolute.relative_to(root).as_posix()
        destination = root / moves.get(relative, relative)
        new_target = quote(os.path.relpath(destination, new_file.parent), safe="/-._")
        return match[1] + new_target + (sep + anchor if sep else "") + ")"
    text = re.sub(r"(\]\()([^\s)]+)\)", replace, text)
    if moves:
        # One pass prevents a new archive path from being replaced twice.
        pattern = "|".join(re.escape(k) for k in sorted(moves, key=len, reverse=True))
        text = re.sub(pattern, lambda m: moves[m[0]], text)
    return text


def archive_files(root, slug, records, manifest):
    base = Path("revisions") / slug
    moves = {}
    reasons = {}
    for r in records:
        if r["eligible"]:
            relative = Path(r["path"]).relative_to("revisions")
            if relative.parts[0] == slug:
                relative = Path(*relative.parts[1:])
            new = (base / "archive" / relative).as_posix()
            if (root / new).exists():
                raise ValueError(f"Destination already exists: {new}")
            moves[r["path"]] = new
            reasons[r["path"]] = r["evidence"] or ("stato esplicito: " + r["status"] if r["status"] in CLOSED else "traccia storica")
    # Prepare all content before mutation; preserve other edits and source versions.
    contents = {}
    before = {old: digest(root / old) for old in moves}
    for p in (root / "revisions").rglob("*.md"):
        if p.is_symlink() or p.name in GENERATED:
            continue
        old = p.relative_to(root).as_posix()
        new = moves.get(old, old)
        original = p.read_text()
        updated = relocate_links(original, p, root / new, moves, root)
        if old in moves or updated != original:
            contents[old] = (new, updated)
    for old, (new, text) in contents.items():
        target = root / new
        target.parent.mkdir(parents=True, exist_ok=True)
        if new != old:
            (root / old).rename(target)
        write_if_changed(target, text)
    for old, new in moves.items():
        manifest[old] = dict(path=new, reason=reasons[old], sha256_before=before[old], sha256=digest(root / new))
    # Later moves may repair links in already archived records.
    for entry in manifest.values():
        entry["sha256"] = digest(root / entry["path"])
    write_if_changed(root / base / "archive-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return len(moves)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["status", "refresh", "check", "archive"])
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--slug")
    parser.add_argument("--apply", action="store_true", help="Apply archive moves; otherwise preview only")
    args = parser.parse_args()
    root = args.project.resolve()
    slug = args.slug or root.name
    if Path(slug).name != slug or slug in {".", ".."}:
        parser.error("slug must be a directory name")
    base = root / "revisions" / slug
    if not base.is_dir():
        parser.error(f"Missing revision directory: {base}")
    records, manifest = inventory(root, slug)
    for old, entry in manifest.items():
        if not (root / entry["path"]).is_file():
            parser.error(f"Archived file missing: {old} -> {entry['path']}")
    if args.command == "archive":
        candidates = [r["path"] for r in records if r["eligible"]]
        if not args.apply:
            print(json.dumps({"candidates": candidates, "count": len(candidates)}, ensure_ascii=False, indent=2))
            return 0
        # Integrity check precedes all writes; archived sources are immutable.
        for entry in manifest.values():
            if digest(root / entry["path"]) != entry["sha256"]:
                parser.error(f"Archived file changed: {entry['path']}")
        print(f"Archived: {archive_files(root, slug, records, manifest)}")
        records, manifest = inventory(root, slug)
    tasks, archive = report(root, slug, records, manifest)
    if args.command == "status":
        print(tasks)
        return 0
    if args.command == "check":
        stale = [name for name, content in (("TASKS.md", tasks), ("ARCHIVE.md", archive))
                 if not (base / name).exists() or (base / name).read_text() != content]
        corrupt = [e["path"] for e in manifest.values() if digest(root / e["path"]) != e["sha256"]]
        print(json.dumps({"stale": stale, "changed_archive": corrupt}))
        return int(bool(stale or corrupt))
    write_if_changed(base / "TASKS.md", tasks)
    write_if_changed(base / "ARCHIVE.md", archive)
    print(f"Updated: {base / 'TASKS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
