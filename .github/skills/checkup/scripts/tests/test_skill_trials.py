"""Trial reports through the CLI, with isolated fixture repositories."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "skill-trials.py"


class SkillTrialsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.impact = self.root / "impact.md"
        self.a, self.b = self.root / "a", self.root / "b"
        self.a.mkdir()
        self.b.mkdir()

    def rows(self, *rows):
        self.impact.write_text("| Date | Skill | Change | From | Trial until | Outcome |\n"
                               "|---|---|---|---|---|---|\n" + "\n".join(rows))

    def row(self, change="push guard", source="run", outcome="trialing", skill="workflow"):
        return f"| 2026-11-01 | {skill} | {change} | {source} | 3 runs | {outcome} |"

    def tag(self, repo, text):
        path = repo / ".workflow/run/learnings.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def scan(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), "--impact", str(self.impact),
                                 *args, str(self.a), str(self.b)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.splitlines()

    def test_saves_across_repos_and_sweep_is_read_only(self):
        self.rows(self.row(), self.row(source="insurance: lost a release"),
                  self.row(outcome="kept"))
        # Distinguish the insurance row so only the first row receives these saves.
        self.rows(self.row(), self.row(change="rollback", source="insurance: lost a release"),
                  self.row(outcome="kept"))
        for repo in (self.a, self.b):
            self.tag(repo, "- [saved→skill] 2026-11-01 workflow push guard — stopped a bad push\n")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.scan("--sweep"), [
            "keep · 2026-11-01 · workflow · 2 saves · push guard",
            "insurance · 2026-11-01 · workflow · 0 saves · rollback"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_tag_disambiguation(self):
        self.rows(self.row("other"), self.row("Run Routing"))
        for words, counts, warning in [
            ("run routing", [0, 1], None), ("", [0, 0], "matches 2 rows; add words of the change"),
            ("missing", [0, 0], "matches 0 rows; add words of the change")]:
            with self.subTest(words=words):
                self.tag(self.a, f"[saved→skill] 2026-11-01 workflow {words} — stopped it\n")
                out = self.scan("--sweep")
                labels = [line for line in out if not line.startswith("⚠️")]
                for line, count in zip(labels, counts):
                    self.assertIn(f"· {count} save", line)
                if warning:
                    self.assertIn(f"⚠️ tag .workflow/run/learnings.md:1 {warning}", out)

    def test_unique_skill_match_and_wrong_keys(self):
        self.rows(self.row(skill="design (new) · workflow"))
        for date, skill, saves in [("2026-11-01", "workflow", 1),
                                   ("2026-11-01", "design", 1),
                                   ("2026-10-31", "workflow", 0),
                                   ("2026-11-01", "checkup", 0)]:
            with self.subTest(date=date, skill=skill):
                self.tag(self.a, f"- [saved→skill] {date} {skill} — stopped it\n")
                self.assertIn(f"· {saves} save", self.scan("--sweep")[-1])
