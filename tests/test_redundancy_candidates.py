#!/usr/bin/env python3
"""Behavioural tests for the read-only redundancy candidate pre-filter."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/redundancy_candidates.py"


def load_module():
    spec = importlib.util.spec_from_file_location("redundancy_candidates", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RedundancyCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_paragraph_map_preserves_locators_and_citation_metadata(self) -> None:
        markdown = """---
title: Test
---
# 1 Introduzione

La formazione sostiene l'autovalutazione professionale [@Rossi2020, p. 4].

| Campo | Valore |
| --- | --- |
| a | b |

## 1.1 Sviluppo

La riflessione collega esperienza e scelta professionale.

```python
print("non e prosa")
```
"""
        paragraphs = self.module.parse_markdown(markdown)

        self.assertEqual(2, len(paragraphs))
        first = paragraphs[0]
        self.assertEqual(["1 Introduzione"], first.section_path)
        self.assertEqual(6, first.line_start)
        self.assertEqual(6, first.line_end)
        self.assertEqual(["Rossi2020"], first.citations)
        self.assertNotIn("Rossi2020", first.comparison_text)
        self.assertRegex(first.paragraph_id, r"^P001-[0-9a-f]{8}$")

    def test_exact_duplicate_is_a_lexical_candidate(self) -> None:
        markdown = """# Sezione

L'autovalutazione permette di interpretare l'esperienza e orientare le scelte professionali.

L'autovalutazione permette di interpretare l'esperienza e orientare le scelte professionali.

L'autovalutazione è misurata con una scala composta da dodici item.
"""
        paragraphs = self.module.parse_markdown(markdown)
        pairs = self.module.rank_candidate_pairs(
            paragraphs,
            lexical_threshold=0.70,
            semantic_threshold=0.95,
        )

        self.assertEqual(1, len(pairs))
        self.assertEqual("lexical", pairs[0]["candidate_source"])
        self.assertEqual(1.0, pairs[0]["lexical_similarity"])
        self.assertNotIn("classification", pairs[0])
        self.assertNotIn("action", pairs[0])

    def test_scoped_map_keeps_document_level_paragraph_ids(self) -> None:
        markdown = """# Sezione

Primo paragrafo del documento con contenuto sufficiente per essere inventariato.

Secondo paragrafo del documento con contenuto sufficiente per essere inventariato.

Terzo paragrafo selezionato dal perimetro richiesto per questa analisi.
"""
        paragraphs = self.module.parse_markdown(markdown, line_start=7, line_end=7)

        self.assertEqual(1, len(paragraphs))
        self.assertRegex(paragraphs[0].paragraph_id, r"^P003-[0-9a-f]{8}$")
        self.assertEqual(7, paragraphs[0].line_start)

    def test_injected_embeddings_surface_a_distant_paraphrase_only_as_candidate(self) -> None:
        markdown = """# Sezione

La riflessione sul proprio operato consente al docente di scegliere consapevolmente come crescere.

Valutare criticamente l'esperienza orienta le successive decisioni di sviluppo professionale.

Il costrutto di sviluppo professionale viene misurato mediante dodici item Likert.
"""
        paragraphs = self.module.parse_markdown(markdown)
        embeddings = [[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]]
        pairs = self.module.rank_candidate_pairs(
            paragraphs,
            embeddings=embeddings,
            lexical_threshold=0.99,
            semantic_threshold=0.95,
        )

        self.assertEqual(1, len(pairs))
        pair = pairs[0]
        self.assertEqual("semantic", pair["candidate_source"])
        self.assertGreater(pair["semantic_similarity"], 0.99)
        self.assertNotIn("classification", pair)
        self.assertNotIn("action", pair)

    def test_pair_metadata_surfaces_negation_and_distinct_citations(self) -> None:
        markdown = """# Sezione

Il modello determina direttamente la scelta professionale [@FonteA].

Il modello non determina direttamente la scelta professionale [@FonteB].
"""
        paragraphs = self.module.parse_markdown(markdown)
        pairs = self.module.rank_candidate_pairs(
            paragraphs,
            lexical_threshold=0.20,
            semantic_threshold=0.95,
            min_words=5,
        )

        self.assertEqual(1, len(pairs))
        pair = pairs[0]
        self.assertIn("negation-mismatch", pair["review_flags"])
        self.assertEqual(["FonteA"], pair["citations_left_only"])
        self.assertEqual(["FonteB"], pair["citations_right_only"])

    def test_cli_is_read_only_and_emits_json(self) -> None:
        markdown = """# Sezione

La competenza integra conoscenze, abilità e disposizione ad agire nel contesto.

La competenza integra conoscenze, abilità e disposizione ad agire nel contesto.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "article.md"
            source.write_text(markdown, encoding="utf-8")
            before = hashlib.sha256(source.read_bytes()).hexdigest()

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(source),
                    "--backend",
                    "lexical",
                    "--lexical-threshold",
                    "0.70",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual("lexical", payload["semantic_status"])
            self.assertEqual(1, len(payload["candidate_pairs"]))
            self.assertEqual(before, hashlib.sha256(source.read_bytes()).hexdigest())

    def test_cli_defaults_to_ranked_8b_semantic_queue(self) -> None:
        args = self.module.build_parser().parse_args(["article.md"])

        self.assertEqual("qwen3-embedding:8b", args.model)
        self.assertEqual(0.0, args.semantic_threshold)

    def test_cli_discovers_windows_ollama_url_from_project_env(self) -> None:
        class EmbedHandler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802 - stdlib handler contract
                self.assert_path()
                length = int(self.headers.get("Content-Length", "0"))
                request = json.loads(self.rfile.read(length))
                inputs = request.get("input", [])
                payload = json.dumps({"embeddings": [[1.0, 0.0] for _ in inputs]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def assert_path(self) -> None:
                if self.path != "/api/embed":
                    self.send_error(404)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), EmbedHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                project = Path(temp_dir)
                source = project / "articles" / "article.md"
                source.parent.mkdir()
                source.write_text(
                    "# Sezione\n\nUn paragrafo sufficientemente lungo per richiedere un embedding.\n",
                    encoding="utf-8",
                )
                endpoint = f"http://127.0.0.1:{server.server_port}"
                (project / ".env").write_text(
                    f"ARTICLE_REVISION_OLLAMA_URL={endpoint}/v1\n",
                    encoding="utf-8",
                )
                environment = os.environ.copy()
                for key in ("ARTICLE_REVISION_OLLAMA_URL", "OLLAMA_BASE_URL", "OLLAMA_HOST"):
                    environment.pop(key, None)

                result = subprocess.run(
                    [sys.executable, str(SCRIPT), str(source), "--backend", "ollama"],
                    text=True,
                    capture_output=True,
                    check=False,
                    env=environment,
                )

                self.assertEqual(0, result.returncode, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(
                    f"ollama:qwen3-embedding:8b@{endpoint}",
                    payload["semantic_status"],
                )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
