import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/revision_registry.py"


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "revisions/demo"
        self.base.mkdir(parents=True)
        self.put("revisions/demo/tasks/task-done.md", "---\nstatus: completed\n---\n- **Rinviati**: verificare le fonti\n")
        self.put("revisions/demo/tasks/task-open.md", "---\nstatus: paused\n---\n[chiuso](task-done.md)\n")
        self.put("revisions/demo/plans/proposal.md", "# Proposta\nDecision: accepted\n")
        self.put("revisions/demo/parti/applied.md", "---\nstato: applicato <!-- proposto | applicato -->\n---\n[fonte](../../../articles/versions/article-v9-a.md)\n")
        self.put("articles/versions/article-v9-a.md", "versione storica")
        self.put("articles/versions/article-v10-a.md", "<!-- DA-SVILUPPARE: teoria -->")

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def run_command(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPT), *args, "--project", str(self.root), "--slug", "demo"], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return result.stdout

    def test_preview_and_status_are_read_only(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(json.loads(self.run_command("archive"))["count"], 2)
        self.run_command("status")
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_archive_preserves_pending_work_links_and_active_version(self):
        self.run_command("archive", "--apply")
        self.assertTrue((self.base / "tasks/task-open.md").exists())
        self.assertTrue((self.base / "plans/proposal.md").exists())
        self.assertFalse((self.base / "tasks/task-done.md").exists())
        self.assertIn("../archive/tasks/task-done.md", (self.base / "tasks/task-open.md").read_text())
        self.assertIn("../../../../articles/versions/article-v9-a.md", (self.base / "archive/parti/applied.md").read_text())
        report = (self.base / "TASKS.md").read_text()
        self.assertIn("verificare le fonti", report)
        self.assertIn("article-v10-a.md", report)
        self.assertIn("DA-SVILUPPARE: teoria", report)
        self.run_command("check")
        self.assertIn("Archived: 0", self.run_command("archive", "--apply"))
        self.run_command("check")

    def test_detects_new_work_and_archive_tampering(self):
        self.run_command("archive", "--apply")
        self.put("revisions/demo/tasks/task-new.md", "---\nstatus: in-progress\n---\n")
        self.run_command("check", expected=1)
        self.run_command("refresh")
        self.run_command("check")
        self.put("revisions/demo/archive/tasks/task-done.md", "changed")
        self.assertIn("changed_archive", self.run_command("check", expected=1))
        self.run_command("archive", "--apply", expected=2)

    def test_collision_fails_before_moving_any_file(self):
        self.put("revisions/demo/archive/tasks/task-done.md", "existing")
        result = subprocess.run([sys.executable, str(SCRIPT), "archive", "--apply", "--project", str(self.root), "--slug", "demo"], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.base / "tasks/task-done.md").exists())
        self.assertTrue((self.base / "parti/applied.md").exists())


if __name__ == "__main__":
    unittest.main()
