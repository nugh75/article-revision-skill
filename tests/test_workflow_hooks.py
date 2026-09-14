"""Compatibility entry points delegate to the same integrated project coordinator."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


class WorkflowHookTests(unittest.TestCase):
    def project(self, folder):
        root = Path(folder)
        source = root / 'articles/versions/article-v76-2026-09-13-1034.md'
        source.parent.mkdir(parents=True)
        source.write_text('> Versione: v76\n\nTesto.\n')
        bib = root / 'bibliography/reference.bib'
        bib.parent.mkdir()
        bib.write_text('@book{test, title={Test}}')
        (root / '05_Script').mkdir()
        (root / '05_Script/tesi.py').write_text('import sys,json\nprint(json.dumps(sys.argv[1:]))\n')
        return root, source, bib

    def test_bump_uses_prepare_and_preserves_argument_quoting(self):
        with tempfile.TemporaryDirectory() as folder:
            root, source, _ = self.project(folder)
            result = subprocess.run(['bash', str(SCRIPTS / 'new_version.sh'), str(source)],
                                    cwd=root, env={**os.environ, 'PYTHON_BIN': '/usr/bin/python3',
                                                  'BUMP_MESSAGE': 'Titolo "citato"; $(non-eseguire)'},
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"bump", "--prepare", "--path-only"', result.stdout)
            self.assertIn('$(non-eseguire)', result.stdout)
            self.assertEqual(len(list(source.parent.glob('*.md'))), 1)

    def test_export_delegates_with_explicit_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root, source, bib = self.project(folder)
            result = subprocess.run(['bash', str(SCRIPTS / 'sync_current.sh'), str(source), str(bib)],
                                    cwd=root, env={**os.environ, 'PYTHON_BIN': '/usr/bin/python3'},
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"export", "--source"', result.stdout)
            self.assertFalse((root / 'articles/current.docx').exists())


if __name__ == '__main__':
    unittest.main()
