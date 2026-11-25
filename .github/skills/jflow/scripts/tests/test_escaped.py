import json
import re
import subprocess
import sys
import unittest

import test_jflow as fixture

SCRIPT = fixture.SCRIPT
SECRET = "ghp_" + "a1" * 20


class Escaped(unittest.TestCase):
    setUp = fixture.RunRecord.setUp
    tearDown = fixture.RunRecord.tearDown
    git = fixture.RunRecord.git
    commit = fixture.RunRecord.commit
    jflow = fixture.RunRecord.jflow

    def done_run(self):
        """A done run with one record and one accepted defect, all committed."""
        (self.repo / "app.py").write_text("a = 2\n")
        self.commit("build")
        self.jflow("record", "demo", "spec", "--model", "opus", "--effort", "high")
        spec = self.run_dir / "spec.md"
        sha = self.git("rev-parse", "--short", "HEAD")
        spec.write_text(spec.read_text().replace("Status: ready", "Status: done")
                        + f'\n## Accepted\n- Defect 1 · a miss · "ok" · 2026-11-25 · {sha}\n')
        self.commit("done")
        return (self.run_dir / "run.jsonl").read_text()

    def escaped(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "escaped", *args, "--repo", str(self.repo)],
                              capture_output=True, text=True)

    def test_rows_1_2_appends_each_bug_and_summary_counts_them(self):
        before = self.done_run()
        summary = json.loads(self.jflow("summary", "demo", "--json"))
        self.assertNotIn("escaped", summary)
        self.assertEqual(self.escaped("demo", " count shows wrong data ").returncode, 0)
        self.assertEqual(self.escaped("demo", "second bug", "--ref", "#12").returncode, 0)
        text = (self.run_dir / "run.jsonl").read_text()
        self.assertTrue(text.startswith(before))
        first, second = map(json.loads, text[len(before):].splitlines())
        head = self.git("rev-parse", "HEAD")
        self.assertEqual({k: first[k] for k in ("v", "step", "sha", "text")},
                         {"v": 1, "step": "escaped", "sha": head, "text": "count shows wrong data"})
        self.assertNotIn("ref", first)
        self.assertEqual((second["text"], second["ref"]), ("second bug", "#12"))
        self.assertRegex(first["at"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00$")
        after = json.loads(self.jflow("summary", "demo", "--json"))
        self.assertEqual(after, dict(summary, escaped=2))
        self.assertEqual(after["accepted"], 1)

    def test_row_3_refuses_bad_input_without_writing(self):
        before = self.done_run()
        cases = [(["nope", "x"], "no .jflow/nope/spec.md"), (["demo", "  "], "one-line"),
                 (["demo", "two\nlines"], "one-line"), (["demo", "leak " + SECRET], "secret-like"),
                 (["demo", "x", "--ref", SECRET], "secret-like"), (["#42", "x"], ".jflow/ slug"),
                 (["demo", "x"], ".jflow/ slug")]  # last: a plain slug with git config jflow.mode github
        for args, error in cases:
            with self.subTest(args=args):
                if args == ["demo", "x"]:
                    self.git("config", "jflow.mode", "github")
                out = self.escaped(*args)
                self.assertNotEqual(out.returncode, 0)
                self.assertEqual(out.stdout, "")
                self.assertRegex(out.stderr, r"^[^\n]+\n$")
                self.assertIn(error, out.stderr)
                self.assertNotIn(SECRET, out.stderr)
                self.assertEqual((self.run_dir / "run.jsonl").read_text(), before)

    def test_row_4_done_run_stays_done_and_valid(self):
        self.done_run()
        self.assertEqual(self.escaped("demo", "a bug").returncode, 0)
        n = json.loads(self.jflow("next", "demo", "--json"))
        self.assertEqual((n["step"], n["why"]), (None, "spec.md says Status: done"))
        self.assertEqual(self.jflow("validate", "demo", "spec"), "")

    def test_row_5_skill_documents_the_command(self):
        skill = (SCRIPT.parents[1] / "SKILL.md").read_text()
        line = next(l for l in skill.split("\n\n") if "jflow.py escaped" in l)
        self.assertTrue(re.search(r"run\.jsonl", line) and "## Accepted" in line, line)

    def test_commit_sha_ref_allowed_and_non_commit_hex_refused(self):
        before = self.done_run()
        head = self.git("rev-parse", "HEAD")
        ok = self.escaped("demo", "commit ref bug", "--ref", head)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["ref"], head)
        fake = "f" * 40
        bad = self.escaped("demo", "fake hex", "--ref", fake)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("secret-like", bad.stderr)
        self.assertNotIn(fake, bad.stderr)
        self.assertEqual(len((self.run_dir / "run.jsonl").read_text().splitlines()), len(before.splitlines()) + 1)

    def test_missing_final_newline_in_run_jsonl(self):
        before = self.done_run()
        log = self.run_dir / "run.jsonl"
        log.write_text(before.rstrip("\n"), encoding="utf-8")
        out = self.escaped("demo", "after manual edit")
        self.assertEqual(out.returncode, 0, out.stderr)
        after = json.loads(self.jflow("summary", "demo", "--json"))
        self.assertEqual(after["escaped"], 1)

    def test_misspelled_and_repeated_ref_refused_without_echo(self):
        before = self.done_run()
        for args, expected in (
            (["demo", "x", "--reff", SECRET], "secret-like"),
            (["demo", "x", "--ref", SECRET, "--ref", "#12"], "secret-like"),
            (["demo", "x", "--ref", "#11", "--ref", "#12"], "only once"),
        ):
            with self.subTest(args=args):
                out = self.escaped(*args)
                self.assertNotEqual(out.returncode, 0)
                self.assertIn(expected, out.stderr)
                self.assertNotIn(SECRET, out.stderr)
                self.assertEqual((self.run_dir / "run.jsonl").read_text(), before)

    def test_repo_path_with_newline(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo\nwith-newline"
            repo.mkdir()
            for cmd in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t"]):
                subprocess.run(["git", "-C", str(repo), *cmd], check=True)
            (repo / ".jflow/demo").mkdir(parents=True)
            (repo / ".jflow/demo/spec.md").write_text("# demo\nStatus: done\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
            out = subprocess.run([sys.executable, str(SCRIPT), "escaped", "demo", "nl path", "--repo", str(repo)],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(json.loads(out.stdout)["text"], "nl path")


if __name__ == "__main__":
    unittest.main()
