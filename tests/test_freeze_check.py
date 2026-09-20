#!/usr/bin/env python3
"""Behavioural tests for the frozen-passage verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/freeze_check.py"

PASSAGE = "La teoria della diffusione delle innovazioni colloca l'adozione su cinque categorie."


def load_module():
    spec = importlib.util.spec_from_file_location("freeze_check", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def short_digest(text: str) -> str:
    normalised = " ".join(unicodedata.normalize("NFC", text).split())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:12]


def ledger(rows: str, blocks: str) -> str:
    return f"""---
article: articles/versions/article-v96.md
---

# Freeze Ledger — test

## Mappa stato

| Unità | Capitolo | Sezione | Righe | Incipit (ancora) | Stato | Ultima modifica | Commenti / intenzioni |
|---|---|---|---|---|---|---|---|
| §2.2 | Capitolo 2 | §2.2 Adozione | article-v96.md:168-168 | «I concetti…» | 🟡 open | 2026-09-19 | — |

---

## Passaggi congelati

| ID | Sezione | Righe | Incipit | sha256 | Stato | Data |
|---|---|---|---|---|---|---|
{rows}

{blocks}

---

## Storico freeze / thaw

| Data | Azione | Unità | Da → A | Origine |
|---|---|---|---|---|
"""


def block(identifier: str, section: str, state: str, text: str, reason: str = "dato verificato") -> str:
    return (
        f"### {identifier} — {section} — {state} — 2026-09-20\n"
        f"- **Motivo:** {reason}\n\n"
        "```text\n"
        f"{text}\n"
        "```\n"
    )


def row(identifier: str, section: str, digest: str, state: str = "🔒 frozen") -> str:
    return f"| {identifier} | {section} | article-v96.md:224-224 | «La teoria…» | {digest} | {state} | 2026-09-20 |"


class FreezeCheckTests(unittest.TestCase):
    def run_check(self, article_text: str, ledger_text: str):
        with tempfile.TemporaryDirectory() as folder:
            article = Path(folder) / "article-v96.md"
            article.write_text(article_text, encoding="utf-8")
            ledger_path = Path(folder) / "freeze-ledger.md"
            ledger_path.write_text(ledger_text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(article), "--ledger", str(ledger_path)],
                text=True,
                capture_output=True,
            )

    def test_passage_present_once_passes(self):
        article = f"# Tesi\n\n## 2.2.4 Diffusione\n\n{PASSAGE}\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE)),
                                               block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("F7", result.stdout)
        self.assertIn("ok", result.stdout)

    def test_reports_current_line_of_the_passage(self):
        article = f"# Tesi\n\nPrima riga.\n\nSeconda riga.\n\n{PASSAGE}\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE)),
                                                block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("riga 7", result.stdout)

    def test_reworded_passage_is_stale(self):
        article = "# Tesi\n\nLa teoria della diffusione colloca l'adozione su sei categorie.\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE)),
                                                block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale", result.stdout)

    def test_deleted_passage_is_stale(self):
        result = self.run_check("# Tesi\n\nAltro testo.\n",
                                ledger(row("F7", "§2.2.4", short_digest(PASSAGE)),
                                       block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale", result.stdout)

    def test_duplicated_passage_is_ambiguous(self):
        article = f"# Tesi\n\n{PASSAGE}\n\nAltro.\n\n{PASSAGE}\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE)),
                                                block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ambiguo", result.stdout)
        self.assertIn("2", result.stdout)

    def test_passage_rewrapped_across_lines_still_matches(self):
        wrapped = "La teoria della diffusione\ndelle innovazioni colloca\nl'adozione su cinque categorie."
        article = f"# Tesi\n\n{wrapped}\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE)),
                                                block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok", result.stdout)

    def test_decomposed_accents_match_composed_ledger(self):
        composed = "L'università è il contesto dell'indagine."
        decomposed = unicodedata.normalize("NFD", composed)
        article = f"# Tesi\n\n{decomposed}\n"
        result = self.run_check(article, ledger(row("F3", "§1.1", short_digest(composed)),
                                                block("F3", "§1.1", "🔒 frozen", composed)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok", result.stdout)

    def test_span_ending_before_punctuation_still_matches(self):
        """A passage may end mid-token: the article has «dell'innovazione:» with a colon."""
        span = "da cinque caratteristiche percepite dell'innovazione"
        article = (
            "# Tesi\n\nNel modello di Rogers, il tasso di adozione è spiegato "
            "principalmente " + span + ": il vantaggio relativo e altri.\n"
        )
        result = self.run_check(article, ledger(row("F1", "§2.2.4", short_digest(span)),
                                                block("F1", "§2.2.4", "🔒 frozen", span)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok", result.stdout)

    def test_span_starting_mid_sentence_still_matches(self):
        span = "l'adozione su cinque"
        article = f"# Tesi\n\nLa teoria colloca {span} categorie distinte.\n"
        result = self.run_check(article, ledger(row("F2", "§2.2.4", short_digest(span)),
                                                block("F2", "§2.2.4", "🔒 frozen", span)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok", result.stdout)

    def test_ledger_without_frozen_passages_passes(self):
        result = self.run_check("# Tesi\n\nTesto.\n", ledger("", ""))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 passaggi", result.stdout)

    def test_digest_mismatch_between_table_and_block_fails(self):
        article = f"# Tesi\n\n{PASSAGE}\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", "000000000000"),
                                                block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("hash incoerente", result.stdout)

    def test_table_row_without_verbatim_block_fails(self):
        article = f"# Tesi\n\n{PASSAGE}\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE)), ""))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("blocco mancante", result.stdout)

    def test_verbatim_block_without_table_row_fails(self):
        article = f"# Tesi\n\n{PASSAGE}\n"
        result = self.run_check(article, ledger("", block("F7", "§2.2.4", "🔒 frozen", PASSAGE)))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("riga di tabella mancante", result.stdout)

    def test_thawed_passage_is_not_enforced(self):
        article = "# Tesi\n\nTesto completamente diverso.\n"
        result = self.run_check(article, ledger(row("F7", "§2.2.4", short_digest(PASSAGE), "🟡 open"),
                                                block("F7", "§2.2.4", "🟡 open", PASSAGE)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("non verificato", result.stdout)

    def test_missing_passages_section_passes(self):
        ledger_text = "---\narticle: x.md\n---\n\n# Freeze Ledger\n\n## Mappa stato\n\nniente.\n"
        result = self.run_check("# Tesi\n\nTesto.\n", ledger_text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 passaggi", result.stdout)

    def test_normalisation_is_reusable_as_a_function(self):
        module = load_module()
        self.assertEqual(module.normalise("  La  teoria\ndella   diffusione "), "La teoria della diffusione")


if __name__ == "__main__":
    unittest.main()
