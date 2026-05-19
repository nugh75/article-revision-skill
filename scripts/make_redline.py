#!/usr/bin/env python3
"""make_redline.py — colored old-vs-new redline for the journal reviewer.

Word-level diff between two article versions (markdown or .docx). Emits an
HTML redline (insertions green + underline, deletions red + strikethrough)
and, if pandoc is available, a .docx with the same colors.

The clean revised manuscript stays the submission file; this redline is the
SEPARATE marked-up copy reviewers ask for. ECPS forbids revision marks in
the final Word file, so never submit this as the manuscript.

Usage:
    python make_redline.py OLD NEW [--out-prefix PATH] [--title TITLE]

OLD/NEW may be .md or .docx. .docx is converted via pandoc first.
Outputs: <out-prefix>.html  and  <out-prefix>.docx (if pandoc present).
Default out-prefix: revisions/redline-<oldstem>-to-<newstem>
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

INS_STYLE = "color:#1a7f1a;text-decoration:underline"
DEL_STYLE = "color:#c01818;text-decoration:line-through"
INS_HEX, DEL_HEX = "1A7F1A", "C01818"

TOKEN_RE = re.compile(r"\s+|\w+|[^\w\s]", re.UNICODE)


def xml_esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def ooxml_run(text: str, kind: str) -> str:
    """Raw OOXML run with real Word color/underline/strike.

    Pandoc passes inline raw `...`{=openxml} straight into document.xml,
    so colors survive (HTML CSS colors do not — pandoc drops them)."""
    if not text:
        return ""
    rpr = ""
    if kind == "ins":
        rpr = f'<w:color w:val="{INS_HEX}"/><w:u w:val="single"/>'
    elif kind == "del":
        rpr = f'<w:color w:val="{DEL_HEX}"/><w:strike/>'
    run = (
        f"<w:r><w:rPr>{rpr}</w:rPr>"
        f'<w:t xml:space="preserve">{xml_esc(text)}</w:t></w:r>'
    )
    return f"`{run}`{{=openxml}}"


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        if not shutil.which("pandoc"):
            sys.exit("pandoc required to read .docx input")
        out = subprocess.run(
            ["pandoc", str(path), "-f", "docx", "-t", "markdown", "--wrap=none"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout
    return path.read_text(encoding="utf-8")


def paragraphs(text: str) -> list[str]:
    # split on blank lines; keep non-empty blocks
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def tokens(s: str) -> list[str]:
    return TOKEN_RE.findall(s)


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def diff_paragraph(old: str, new: str) -> str:
    a, b = tokens(old), tokens(new)
    sm = SequenceMatcher(None, a, b, autojunk=False)
    parts: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            parts.append(esc("".join(a[i1:i2])))
        elif op == "delete":
            parts.append(f'<span style="{DEL_STYLE}">{esc("".join(a[i1:i2]))}</span>')
        elif op == "insert":
            parts.append(f'<span style="{INS_STYLE}">{esc("".join(b[j1:j2]))}</span>')
        elif op == "replace":
            parts.append(f'<span style="{DEL_STYLE}">{esc("".join(a[i1:i2]))}</span>')
            parts.append(f'<span style="{INS_STYLE}">{esc("".join(b[j1:j2]))}</span>')
    return "".join(parts)


def build_html(old: str, new: str, title: str) -> tuple[str, int, int]:
    pa, pb = paragraphs(old), paragraphs(new)
    sm = SequenceMatcher(None, pa, pb, autojunk=False)
    body: list[str] = []
    ins_n = del_n = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for p in pa[i1:i2]:
                body.append(f"<p>{esc(p)}</p>")
        elif op == "delete":
            for p in pa[i1:i2]:
                del_n += 1
                body.append(f'<p><span style="{DEL_STYLE}">{esc(p)}</span></p>')
        elif op == "insert":
            for p in pb[j1:j2]:
                ins_n += 1
                body.append(f'<p><span style="{INS_STYLE}">{esc(p)}</span></p>')
        elif op == "replace":
            # pair paragraphs positionally; diff at word level
            for k in range(max(i2 - i1, j2 - j1)):
                o = pa[i1 + k] if i1 + k < i2 else ""
                n = pb[j1 + k] if j1 + k < j2 else ""
                ins_n += 1
                del_n += 1
                body.append(f"<p>{diff_paragraph(o, n)}</p>")
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{esc(title)}</title>
<style>
 body{{font-family:Georgia,serif;line-height:1.5;max-width:46em;margin:2em auto;padding:0 1em}}
 h1{{font-size:1.3em}} .legend{{font-size:.85em;color:#555;border:1px solid #ddd;padding:.5em 1em;margin-bottom:1.5em}}
 ins,span[style*="underline"]{{}}
</style></head><body>
<h1>{esc(title)}</h1>
<p class="legend">Marked-up version for the reviewer — NOT for submission.
<span style="{INS_STYLE}">inserted text</span> ·
<span style="{DEL_STYLE}">deleted text</span>.
Insertions: {ins_n} · deletions/edits: {del_n}.</p>
{chr(10).join(body)}
</body></html>"""
    return doc, ins_n, del_n


def diff_paragraph_ooxml(old: str, new: str) -> str:
    a, b = tokens(old), tokens(new)
    sm = SequenceMatcher(None, a, b, autojunk=False)
    parts: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            parts.append(ooxml_run("".join(a[i1:i2]), "eq"))
        elif op == "delete":
            parts.append(ooxml_run("".join(a[i1:i2]), "del"))
        elif op == "insert":
            parts.append(ooxml_run("".join(b[j1:j2]), "ins"))
        elif op == "replace":
            parts.append(ooxml_run("".join(a[i1:i2]), "del"))
            parts.append(ooxml_run("".join(b[j1:j2]), "ins"))
    return "".join(parts)


def build_md(old: str, new: str, title: str, ins_n: int, del_n: int) -> str:
    """Markdown whose changed text is raw OOXML → colors survive in .docx."""
    pa, pb = paragraphs(old), paragraphs(new)
    sm = SequenceMatcher(None, pa, pb, autojunk=False)
    out: list[str] = [
        f"# {title}",
        "",
        "_Marked-up version for the reviewer — NOT for submission. "
        f"Green underlined = inserted, red struck-through = deleted. "
        f"Insertions: {ins_n} · deletions/edits: {del_n}._",
        "",
    ]
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for p in pa[i1:i2]:
                out.append(ooxml_run(p, "eq")); out.append("")
        elif op == "delete":
            for p in pa[i1:i2]:
                out.append(ooxml_run(p, "del")); out.append("")
        elif op == "insert":
            for p in pb[j1:j2]:
                out.append(ooxml_run(p, "ins")); out.append("")
        elif op == "replace":
            for k in range(max(i2 - i1, j2 - j1)):
                o = pa[i1 + k] if i1 + k < i2 else ""
                n = pb[j1 + k] if j1 + k < j2 else ""
                out.append(diff_paragraph_ooxml(o, n)); out.append("")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Colored old-vs-new redline for reviewers.")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--out-prefix", default=None)
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    old_p, new_p = Path(args.old), Path(args.new)
    if not old_p.is_file() or not new_p.is_file():
        sys.exit("OLD and NEW must be existing files")

    prefix = Path(
        args.out_prefix
        or f"revisions/redline-{old_p.stem}-to-{new_p.stem}"
    )
    prefix.parent.mkdir(parents=True, exist_ok=True)
    title = args.title or f"Redline: {old_p.stem} → {new_p.stem}"

    doc, ins_n, del_n = build_html(read_text(old_p), read_text(new_p), title)
    html_path = prefix.with_suffix(".html")
    html_path.write_text(doc, encoding="utf-8")
    print(f"html : {html_path}  (+{ins_n} ins / {del_n} del-or-edit)")

    if shutil.which("pandoc"):
        md = build_md(read_text(old_p), read_text(new_p), title, ins_n, del_n)
        md_path = prefix.with_suffix(".redline.md")
        md_path.write_text(md, encoding="utf-8")
        docx_path = prefix.with_suffix(".docx")
        subprocess.run(
            ["pandoc", str(md_path), "-f", "markdown", "-t", "docx", "-o", str(docx_path)],
            check=True,
        )
        print(f"docx : {docx_path}  (real OOXML color runs)")
    else:
        print("docx : skipped (pandoc not found)")


if __name__ == "__main__":
    main()
