import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name("sentence-ledger.py")


class SentenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.skill = self.root / "skills/example"
        self.skill.mkdir(parents=True)
        self.git("init", "-q")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True).strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def baseline(self, text):
        self.write("skills/example/SKILL.md", text)
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                 "commit", "-qm", "baseline")

    def run_ledger(self):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.skill), "HEAD"],
                              cwd=self.root, text=True, capture_output=True)

    def test_sentence_accounting(self):
        self.baseline("Move this sentence. Keep this rule twice. Dropped rule.\n")
        self.write("skills/example/SKILL.md", "[Reference](references/a.md)\n\nCanonical rule.\n")
        self.write("skills/example/references/a.md", "Move this\nsentence.\n")
        self.write(".workflow/lean-skill-hubs/notes/dups-example.txt",
                   "Keep this rule twice.\tskills/example/SKILL.md\tCanonical rule.\n")
        result = self.run_ledger()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("moved 1 · duplicate 1 · unaccounted 1", result.stdout)
        self.assertIn("Dropped rule.", result.stdout)
        self.write("skills/example/references/a.md", "Move this sentence. Dropped rule.\n")
        result = self.run_ledger()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("moved 2 · duplicate 1 · unaccounted 0", result.stdout)
        self.write(".workflow/lean-skill-hubs/notes/dups-example.txt",
                   "Keep this rule twice.\tskills/example/SKILL.md\tMissing phrase.\n")
        result = self.run_ledger()
        self.assertEqual(result.returncode, 1)
        self.assertIn("retained phrase missing", result.stderr)

    def test_reference_disclosure(self):
        self.baseline("Retained rule.\n")
        self.write("skills/example/SKILL.md", "Retained rule.\n[Long](references/c.md)\n")
        self.write("skills/example/references/b.md", "Short reference.\n")
        self.write("skills/example/references/c.md", "Detail\n" * 101)
        result = self.run_ledger()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("references/b.md: not linked", result.stdout)
        self.assertIn("references/c.md: missing contents", result.stdout)
        self.write("skills/example/SKILL.md", "Retained rule.\n[Long](references/c.md)\n[Short](references/b.md)\n")
        self.write("skills/example/references/c.md", "# Reference\n\nContents: details\n" + "Detail\n" * 101)
        result = self.run_ledger()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.write("skills/example/references/c.md", "Detail\n" * 100)
        result = self.run_ledger()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
