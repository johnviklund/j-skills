import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "jflow.py"

SPEC = """# demo
Status: ready
Base: {base}

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | a | cli | x | y | new | red |
| 2 | b | cli | x | y | keep | green |

## Human checks
- none
"""

RECEIPT = """# check-{n} @ {sha} · GPT-6.1 Sol · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | {v1} | `cmd` -> ok |
| 2 | PROVED | `cmd` -> ok |

## Defects
{defects}

## Maybes
- <none>
"""


class RunRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        (self.repo / "app.py").write_text("a = 1\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        base = self.git("rev-parse", "HEAD")
        self.run_dir = self.repo / ".jflow" / "demo"
        (self.run_dir / "receipts").mkdir(parents=True)
        (self.run_dir / "spec.md").write_text(SPEC.format(base=base))
        self.commit("spec")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-qm", msg)

    def jflow(self, *args):
        out = subprocess.run([sys.executable, str(SCRIPT), *args, "--repo", str(self.repo)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout.strip()

    def receipt(self, n, v1, defects, sha="abc"):
        (self.run_dir / "receipts" / f"check-{n}.md").write_text(RECEIPT.format(n=n, v1=v1, defects=defects, sha=sha))

    def test_full_run_counts_sessions_rounds_checks_and_lines(self):
        self.jflow("record", "demo", "spec", "--model", "opus", "--effort", "high")
        (self.repo / "app.py").write_text("a = 1\nb = 2\nc = 3\n")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_app.py").write_text("assert True\n")
        (self.repo / "README.md").write_text("# demo\n")
        self.commit("build")
        self.jflow("record", "demo", "build", "--model", "opus", "--effort", "high")
        self.receipt(1, "BROKEN", "- app.py: input -> crash -> ok. Evidence: run, boom")
        check = json.loads(self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high"))
        self.assertEqual((check["n"], check["rows"], check["defects"], check["maybes"]),
                         (1, {"BROKEN": 1, "PROVED": 1}, 1, 0))
        fix = json.loads(self.jflow("record", "demo", "fix", "--model", "opus", "--effort", "high"))
        self.assertEqual((fix["n"], fix["session"]), (1, "builder"))
        self.receipt(2, "PROVED", "- app.py, carried from check-1: input -> crash -> ok. Evidence: run, boom")
        self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high")
        done = self.jflow("record", "demo", "done", "--model", "opus", "--effort", "high")
        self.assertEqual(done, "jflow: 4 sessions · 1 fix rounds · 2 rows · 0 accepted · check 1 defects"
                               " · net code +2 · tests +1 · docs +1")
        summary = json.loads(self.jflow("summary", "demo", "--json"))
        self.assertIs(summary["first_check_clean"], False)
        self.assertEqual(summary["checks"], 2)

    def test_summary_without_records_and_with_foreign_lines(self):
        (self.run_dir / "run.jsonl").write_text(json.dumps({"v": 1, "step": "decision", "by": "jev"}) + "\n")
        self.assertEqual(self.jflow("summary", "demo"), "jflow: ? sessions · 0 fix rounds · 2 rows · 0 accepted"
                                                        " · check clean · net code +0 · tests +0 · docs +0")

    def test_finished_run_ends_at_the_done_commit(self):
        spec = self.run_dir / "spec.md"
        (self.repo / "app.py").write_text("a = 1\nb = 2\n")
        self.commit("build")
        spec.write_text(spec.read_text().replace("Status: ready", "Status: done"))
        self.commit("done")
        (self.repo / "later.py").write_text("x = 1\ny = 2\n")
        self.commit("later work")
        self.assertEqual(json.loads(self.jflow("summary", "demo", "--json"))["net_code"], 1)

    def test_unrecorded_steps_and_fixes_come_from_git(self):
        (self.repo / "app.py").write_text("a = 2\n")
        self.commit("build, not recorded")
        self.receipt(1, "BROKEN", "- app.py: input -> crash -> ok. Evidence: run, boom", self.git("rev-parse", "HEAD"))
        self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high")
        self.commit("check-1")
        (self.repo / "app.py").write_text("a = 3\n")
        self.commit("fix, not recorded")
        self.receipt(2, "PROVED", "- none", self.git("rev-parse", "HEAD"))
        self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high")
        self.commit("check-2")
        s = json.loads(self.jflow("summary", "demo", "--json"))
        self.assertEqual((s["sessions"], s["fix_rounds"], s["checks"]), (4, 1, 2))

    def test_build_is_a_fresh_session_whatever_the_flag_says(self):
        build = json.loads(self.jflow("record", "demo", "build", "--model", "sol", "--effort", "high",
                                      "--session", "builder"))
        self.assertEqual(build["session"], "fresh")
        restart = json.loads(self.jflow("record", "demo", "fix", "--model", "sol", "--effort", "high",
                                        "--session", "fresh"))
        self.assertEqual(restart["session"], "fresh")

    def test_line_printed_at_done_matches_the_summary_after_the_done_commit(self):
        self.jflow("record", "demo", "spec", "--model", "opus", "--effort", "high")
        (self.repo / "app.py").write_text("a = 1\nb = 2\n")
        self.commit("build")
        spec = self.run_dir / "spec.md"
        spec.write_text(spec.read_text().replace("Status: ready", "Status: done"))
        printed = self.jflow("record", "demo", "done", "--model", "opus", "--effort", "high")
        (self.repo / "WORKLOG.md").write_text("# log\n- " + printed + "\n")
        self.commit("done")
        self.assertEqual(self.jflow("summary", "demo"), printed)

    def test_recording_a_check_again_replaces_its_line(self):
        self.receipt(1, "BLOCKED", "- none")
        self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high")
        self.receipt(1, "PROVED", "- none")
        self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high")
        checks = [r for r in map(json.loads, (self.run_dir / "run.jsonl").read_text().splitlines())
                  if r["step"] == "check"]
        self.assertEqual([c["rows"] for c in checks], [{"PROVED": 2}])

    def test_check_without_receipt_fails(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "record", "demo", "check", "--model", "m",
                              "--effort", "high", "--repo", str(self.repo)], capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertFalse((self.run_dir / "run.jsonl").exists())

    def test_task_slug_and_long_repo_paths_are_not_secrets(self):
        for slug in ("task-list", "sk-ui"):
            task = self.run_dir.with_name(slug)
            task.mkdir()
            (task / "spec.md").write_text((self.run_dir / "spec.md").read_text())
        for slug, path in (("task-list", self.repo), ("sk-ui", self.repo), ("demo", self.repo / ("projects/" * 8))):
            with self.subTest(slug=slug):
                path.mkdir(parents=True, exist_ok=True)
                self.repo = path
                self.jflow("record", slug, "spec", "--model", "opus", "--effort", "high")
                self.assertIn("jflow:", self.jflow("summary", slug))
                self.assertEqual(json.loads(self.jflow("seat", "build"))["role"], "builder")


if __name__ == "__main__":
    unittest.main()
