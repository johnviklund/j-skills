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

    def worklog(self, after=3, score=4, before=True, repo=None, skill="workflow"):
        entries = []
        for date, count, value in [("2026-10-31", 3 if before else 0, 4),
                                   ("2026-11-02", after, score)]:
            entries.extend(f"## {date} · run-{i}\n- Run: 2 tickets · 1 sessions · "
                           f"{value - 1} review cycles · 1 deviations · 0 findings overturned\n"
                           f"- Skills: {skill}@abc\n" for i in range(count))
        (repo or self.a).joinpath("WORKLOG.md").write_text("\n".join(reversed(entries)))

    def test_finished_trial_verdicts(self):
        for score, save, source, expected in [
            (2, False, "run", "✅ 2026-11-01 workflow · trial complete · kept · numbers better (before 4.0 → after 2.0)"),
            (4, False, "run", "⚠️ 2026-11-01 workflow · trial complete · 0 saves · numbers not better (before 4.0 → after 4.0) · removal candidate → workflow improve workflow"),
            (6, True, "run", "✅ 2026-11-01 workflow · trial complete · kept · 1 save"),
            (6, False, "insurance: release", "✅ 2026-11-01 workflow · trial complete · kept · insurance: release")]:
            with self.subTest(score=score, save=save, source=source):
                self.rows(self.row(source=source))
                self.worklog(score=score)
                self.tag(self.a, "[saved→skill] 2026-11-01 workflow — stopped it" if save else "")
                self.assertTrue(self.scan()[0].startswith(expected), self.scan())
                self.assertTrue(self.scan("--sweep")[0].startswith(
                    ("keep" if score < 4 or save else "insurance" if "insurance:" in source else "candidate") + " ·"))

    def test_trial_completion_and_missing_evidence(self):
        for count, unit, before, skill, expected in [
            (2, "runs", True, "workflow", []),
            (3, "checkups", True, "workflow", ["open · count checkups by hand"]),
            (3, "runs", False, "workflow", ["numbers unavailable (before n/a → after 4.0)"]),
            (3, "runs", True, "checkup", [])]:
            with self.subTest(count=count, unit=unit, before=before, skill=skill):
                self.rows(self.row().replace("3 runs", f"3 {unit}"))
                self.worklog(after=count, before=before, skill=skill)
                out = self.scan()
                self.assertEqual(len(out), len(expected))
                for needle in expected:
                    self.assertIn(needle, out[0])
                self.assertEqual(len(self.scan("--sweep")), 1)

    def test_worklog_evidence_across_repos(self):
        self.rows(self.row())
        self.worklog(after=2, score=2)
        self.worklog(after=1, score=2, before=False, repo=self.b)
        self.assertIn("numbers better (before 4.0 → after 2.0)", self.scan()[0])

    def test_real_forms_and_numbers_on_every_line(self):
        self.rows(self.row(), self.row(change="rollback"))
        self.impact.write_text("# SKILL-IMPACT — changes to these skills, and what the runs after them showed\n\n"
                               "Mode: autonomous\n\nOne line per change, newest first.\n" + self.impact.read_text())
        self.tag(self.a, "## Execute\n- [durable→memory] Keep evidence\n"
                 "- [saved→skill] 2026-11-01 workflow push guard — stopped it [routed → SKILL-IMPACT 2026-11-02]\n")
        self.worklog(score=6)
        out = self.scan("--sweep")
        self.assertEqual(len(out), 2)
        self.assertTrue(all("· numbers not better (before 4.0 → after 6.0)" in line for line in out))
        self.assertIn("kept · 1 save · numbers not better (before 4.0 → after 6.0)", self.scan()[0])

    def test_date_windows_and_incomplete_worklog_blocks(self):
        self.rows(self.row())
        dates = [f"2026-10-{day}" for day in range(27, 32)] + [f"2026-11-{day:02}" for day in range(1, 7)]
        blocks = [f"## {date} · run\n- Run: {score} review cycles · 0 deviations\n- Skills: workflow@abc\n"
                  for date, score in zip(dates, [20, 15, 9, 6, 3, 99, 1, 2, 3, 10, 14])]
        malformed = "## 2026-10-31 · incomplete\n- Run: 90 review cycles · 0 deviations\n- Skills: workflow@abc\n"
        incomplete = [malformed.replace(part, "") for part in
                      ["2026-10-31", "90 review cycles", "0 deviations", "- Skills: workflow@abc"]]
        for repo, subset in [(self.a, blocks[::2]), (self.b, blocks[1::2])]:
            (repo / "WORKLOG.md").write_text("# WORKLOG\nPreamble\n" + "\n".join(reversed(subset + incomplete)))
        self.assertIn("numbers better (before 6.0 → after 2.0)", self.scan()[0])

    def test_cli_defaults_deduplication_and_path_errors(self):
        self.rows(self.row())
        self.tag(self.a, "[saved→skill] 2026-11-01 workflow — stopped it\n")
        installed = self.root / "skills/checkup/scripts/skill-trials.py"
        installed.parent.mkdir(parents=True)
        installed.write_bytes(SCRIPT.read_bytes())
        impact = self.root / "skills/workflow/SKILL-IMPACT.md"
        impact.parent.mkdir()
        impact.write_bytes(self.impact.read_bytes())
        for script, args, code, needle in [
            (SCRIPT, ["--impact", str(self.impact), "--sweep"], 0, "· 1 save ·"),
            (SCRIPT, ["--impact", str(self.impact), "--sweep", str(self.a), str(self.a)], 0, "· 1 save ·"),
            (SCRIPT, ["--impact", str(self.impact), str(self.root / "absent-repo")], 2, "absent-repo"),
            (SCRIPT, ["--impact", str(self.root / "absent-impact")], 2, "absent-impact"),
            (installed, ["--sweep"], 0, "· 1 save ·")]:
            with self.subTest(script=script, args=args):
                result = subprocess.run([sys.executable, str(script), *args], cwd=self.a,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertIn(needle, result.stdout if code == 0 else result.stderr)
