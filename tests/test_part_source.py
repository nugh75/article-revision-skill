import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/part_source.py"


class PartSourceTests(unittest.TestCase):
    def test_changed_interior_and_duplicate_parts_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            article = Path(folder) / "article.md"
            part = b"# Part\nSample A.\nFinal line.\n"
            article.write_bytes(part)

            def run(*args):
                return subprocess.run([sys.executable, str(SCRIPT), *args], text=True,
                                      capture_output=True)

            fingerprint = run("capture", article, "1:3")
            self.assertEqual(fingerprint.returncode, 0, fingerprint.stderr)
            locate = ("locate", article, "1:3", fingerprint.stdout.strip())

            article.write_bytes(part.replace(b"Sample A.", b"Sample B."))
            self.assertNotEqual(run(*locate).returncode, 0)

            article.write_bytes(b"New preceding text.\n" + part)
            result = run(*locate)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "2:4")

            article.write_bytes(part.replace(b"\n", b"\r\n"))
            self.assertEqual(run(*locate).stdout.strip(), "1:3")

            article.write_bytes(part + part)
            self.assertNotEqual(run(*locate).returncode, 0)


if __name__ == "__main__":
    unittest.main()
