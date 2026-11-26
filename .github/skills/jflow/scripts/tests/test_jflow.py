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
A run with `Status: done` stops.

## Problem
A fixture run.

## Goals
1. Prove the run.

## Non-goals
- none

## Constraints
- Gate: none.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | a | cli | x | y | new | red |
| 2 | b | cli | x | y | keep | green |

## Human checks
- none
"""

def ask_line(n):
    return n["blocker"].splitlines()[0][3:]


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

    def receipt(self, n, v1, defects, sha=None):
        sha = sha or self.git("rev-parse", "HEAD")
        (self.run_dir / "receipts" / f"check-{n}.md").write_text(RECEIPT.format(n=n, v1=v1, defects=defects, sha=sha))

    def test_full_run_counts_sessions_rounds_checks_and_lines(self):
        self.jflow("record", "demo", "spec", "--model", "opus", "--effort", "high")
        (self.repo / "app.py").write_text("a = 1\nb = 2\nc = 3\n")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_app.py").write_text("assert True\n")
        (self.repo / "README.md").write_text("# demo\n")
        self.commit("build")
        self.jflow("record", "demo", "build", "--model", "opus", "--effort", "high")
        self.receipt(1, "BROKEN", "- 1. app.py: input -> crash -> ok. Evidence: run, boom")
        check = json.loads(self.jflow("record", "demo", "check", "--model", "sol", "--effort", "high"))
        self.assertEqual((check["n"], check["rows"], check["defects"], check["maybes"]),
                         (1, {"BROKEN": 1, "PROVED": 1}, 1, 0))
        fix = json.loads(self.jflow("record", "demo", "fix", "--model", "opus", "--effort", "high"))
        self.assertEqual((fix["n"], fix["session"]), (1, "builder"))
        self.commit("check-1")
        (self.run_dir / "notes.md").write_text("Fix: the finding was wrong.\n")
        self.commit("fix")
        self.receipt(2, "PROVED", "- 1. app.py, carried from check-1: input -> crash -> ok. Evidence: run, boom")
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
        self.receipt(1, "BROKEN", "- 1. app.py: input -> crash -> ok. Evidence: run, boom", self.git("rev-parse", "HEAD"))
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
        slugs = ("task-list", "sk-ui", "sk-onboarding-checklist", "sk-onboarding-checklist-v2")
        for slug in slugs:
            task = self.run_dir.with_name(slug)
            task.mkdir()
            (task / "spec.md").write_text((self.run_dir / "spec.md").read_text())
        for slug, path in [(s, self.repo) for s in slugs] + [("demo", self.repo / ("projects/" * 8))]:
            with self.subTest(slug=slug):
                path.mkdir(parents=True, exist_ok=True)
                self.repo = path
                self.jflow("record", slug, "spec", "--model", "opus", "--effort", "high")
                self.assertIn("jflow:", self.jflow("summary", slug))
                self.assertEqual(json.loads(self.jflow("seat", "build"))["role"], "builder")

    def next(self, *args):
        return json.loads(self.jflow("next", "demo", "--json", *args))

    def state(self, v1, defects="- none", code=False):
        if code:
            (self.repo / "app.py").write_text(self.git("rev-parse", "HEAD") + "\n")
            self.commit("code")
        self.receipt(1, v1, defects, self.git("rev-parse", "HEAD"))
        self.commit("receipt")

    def test_next_follows_every_state(self):
        spec = self.run_dir / "spec.md"
        flow = json.loads((SCRIPT.parents[1] / "flow.json").read_text())["steps"]
        notes = self.run_dir / "notes.md"
        steps = [
            (lambda: None, "build"),
            (lambda: spec.write_text(spec.read_text().replace("ready", "drafting")), "spec"),
            (lambda: spec.write_text(spec.read_text().replace("drafting", "ready")), "build"),
            (lambda: self.state("PROVED", code=True) or (self.run_dir / "receipts/check-1.md").unlink(), "check"),
            (lambda: self.state("BROKEN"), "fix"),
            (lambda: self.state("PROVED", "- 1. app.py: x -> crash -> ok"), "fix"),
            (lambda: self.state("BLOCKED"), "human"),
            (lambda: self.state("UNREACHABLE"), "human"),
            (lambda: self.state("WAITING"), "live"),
            (lambda: notes.write_text("Live done: 2026-11-09\n"), "check"),
            (lambda: self.state("PROVED"), "done"),
            (lambda: notes.write_text("only .jflow changed\n"), "done"),
            (lambda: (self.repo / "app.py").write_text("a = 9\n"), "check"),
            (lambda: spec.write_text(spec.read_text().replace("ready", "done")), None),
        ]
        for change, expected in steps:
            change()
            self.git("add", "-A")
            self.git("commit", "-qm", "state", "--allow-empty")
            with self.subTest(expected=expected):
                n = self.next()
                self.assertEqual(set(n), {"schema_version", "slug", "step", "n", "role", "model", "command",
                                          "session", "blocker", "why"})
                self.assertEqual(n["step"], expected)
                if expected in flow:
                    seat = json.loads(self.jflow("seat", expected))
                    self.assertEqual(n["model"], {k: seat[k] for k in ("model", "vendor", "effort")})
                    self.assertEqual((n["role"], n["session"]), (flow[expected]["role"], flow[expected]["session"]))
                self.assertEqual(n["n"], {"check": len(list(self.run_dir.glob("receipts/*"))) + 1, "fix": 1}.get(expected))
                self.assertEqual(bool(n["blocker"]), expected == "human")
                if expected == "fix":
                    self.assertEqual(n["command"], "Fix .jflow/demo/receipts/check-1.md, then print the card.")
                    card = self.jflow("next", "demo").splitlines()
                    self.assertEqual(card, ["Next: send this in the builder session (claude-opus-5-5 · medium):", "",
                                            "```text", n["command"], "```"])
        self.assertIsNone(self.next()["command"])
        self.assertEqual(json.loads(self.jflow("next", "nothing-yet", "--json"))["step"], "spec")

    def test_next_routes_edge_defects_to_the_human(self):
        for tag, v1, expected in [("[edge] ", "PROVED", "human"), ("[use] ", "PROVED", "fix"),
                                  ("[edge] ", "BROKEN", "fix"), ("", "PROVED", "fix")]:
            self.state(v1, f"- 1. {tag}app.py: x -> crash -> ok", code=True)
            n = self.next()
            self.assertEqual(n["step"], expected, (tag, v1))
            if expected == "human":
                self.assertIn("defect 1", n["blocker"].splitlines()[0])
                self.assertIn("➡️ A. Accept them", n["blocker"])
        (self.run_dir / "notes.md").write_text("Checks allowed: 0\n")  # a cap set below the checks used
        self.state("PROVED", "- 1. [edge]\tapp.py: x -> crash -> ok", code=True)
        self.assertIn("**B. Fix them**: I fix them and raise the check limit.", self.next()["blocker"])

    def test_next_sends_rows_broken_only_by_edge_defects_to_the_human(self):
        edge, use = "- 1. [edge] app.py: x -> crash -> ok", "\n- 2. [use] app.py: y -> crash -> ok"
        for cited, defects, expected in [("defect 1", edge, "human"), ("defect 1, defect 2", edge + use, "fix"),
                                         ("`cmd` -> fails", edge, "fix")]:
            self.state("BROKEN", defects, code=True)
            path = self.run_dir / "receipts/check-1.md"
            path.write_text(path.read_text().replace("| 1 | BROKEN | `cmd` -> ok |", f"| 1 | BROKEN | {cited} |"))
            self.commit("receipt")
            self.assertEqual(self.next()["step"], expected, cited)
        self.state("BROKEN", edge, code=True)
        path.write_text(path.read_text().replace("| 1 | BROKEN | `cmd` -> ok |", "| 1 | BROKEN | defect 1 |"))
        self.commit("receipt")
        with (self.run_dir / "spec.md").open("a") as f:  # accepting the defect clears the row it broke
            f.write(f'\n## Accepted\n- Defect 1 · odd input · "accept" · 2026-11-25 · {self.git("rev-parse", "HEAD~2")}\n')
        self.commit("accept")
        self.assertEqual(self.next()["step"], "done")

    def test_next_asks_about_unproved_rows_before_edge_defects(self):
        self.state("BLOCKED", "- 1. [edge] app.py: x -> crash -> ok", code=True)
        n = self.next()
        self.assertEqual(n["step"], "human")
        # The row's own reason from the receipt, so the human sees what is missing.
        self.assertIn("- Row 1, BLOCKED: `cmd` -> ok", n["blocker"])
        self.assertIn("I add them and the [edge] defects under ## Accepted.", n["blocker"])
        self.assertTrue(ask_line(n).startswith("Check-1 could not prove 1 row,"), ask_line(n))

    def test_next_stops_at_the_check_cap(self):
        for k in range(1, 4):
            (self.repo / "app.py").write_text(f"a = {k + 1}\n")
            self.commit("code")
            self.receipt(k, "BROKEN", "- none", self.git("rev-parse", "HEAD"))
            self.commit("receipt")
        self.receipt(4, "BROKEN", "- none", self.git("rev-parse", "HEAD"))
        self.commit("rerun only")
        self.assertIn("3 checks used of 3", self.next()["blocker"])
        ask = self.jflow("next", "demo", "--ask").splitlines()
        self.assertIn("went from 1 to 1", ask[0])
        self.assertEqual(ask[ask.index("Checker view (.jflow/demo/receipts/check-4.md): 1 | BROKEN | `cmd` -> ok") + 2],
                         "**➡️ A. Stop here** (recommended): I accept what is open and move on.", ask)
        self.assertIn("**B. One more check**: I raise the limit and fix; if that check finds a new problem, stop.", ask)
        self.assertEqual(ask[-1], "Reply A or B.")
        (self.run_dir / "receipts/check-3.md").write_text(
            (self.run_dir / "receipts/check-3.md").read_text().replace("- none", "- 1. app.py: x -> crash -> ok"))
        self.commit("closing")
        self.assertIn("➡️ A. One more check", self.next()["blocker"])
        (self.run_dir / "notes.md").write_text("Checks allowed: 2\n")
        self.commit("allow")
        self.assertIn("3 checks used of 2", self.next()["blocker"])
        self.assertIn("I raise the limit", self.next()["blocker"])
        with (self.run_dir / "notes.md").open("a") as notes:
            notes.write("Checks allowed: 5\n")
        self.commit("allow more")
        self.assertEqual(self.next()["step"], "fix")

    def test_next_closes_on_acceptance_after_live_changes_at_the_cap(self):
        (self.repo / "app.py").write_text("a = 2\n")
        self.commit("build")
        (self.run_dir / "notes.md").write_text("Checks allowed: 1\n")
        self.receipt(1, "WAITING", "- none")
        self.commit("check-1")
        (self.repo / "report.md").write_text("live verdict\n")
        self.commit("live")
        self.assertIn("1 checks used of 1 and check is next", self.next()["blocker"])
        sha = self.git("rev-parse", "HEAD~2")  # the receipt's header sha
        with (self.run_dir / "spec.md").open("a") as spec:
            spec.write(f"\n## Accepted\n- Row 2 · not the open row · {sha}\n")
        self.commit("accept another row")
        self.assertIn("1 checks used of 1", self.next()["blocker"])
        with (self.run_dir / "spec.md").open("a") as spec:
            spec.write(f"- Row 1 · waiting after the live steps · {sha}\n")
        self.commit("accept what is open")
        self.assertEqual(self.next()["step"], "done")
        (self.run_dir / "notes.md").write_text("Checks allowed: 2\n")
        self.commit("allow")
        self.assertEqual(self.next()["step"], "check")

    def test_next_vendor_override_and_bad_slug(self):
        (self.repo / "app.py").write_text("a = 2\n")
        self.commit("build")
        self.assertEqual(self.next("--builder-vendor", "openai")["model"]["vendor"], "anthropic")
        out = subprocess.run([sys.executable, str(SCRIPT), "next", "../x", "--repo", str(self.repo)],
                             capture_output=True, text=True)
        self.assertEqual((out.returncode, "bad slug" in out.stderr), (1, True))
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_next_accepts_only_the_named_item_at_its_check(self):
        self.state("BROKEN", "- 1. app.py: x -> crash -> ok", code=True)
        sha, spec = self.git("rev-parse", "HEAD~1"), (self.run_dir / "spec.md").read_text()
        both = f"Row 1 · 254 of 300 · {sha}\n- Defect 1 · crash · {sha}"
        for lines, check2, expected in [(both, "", "done"), (both.replace(sha, "abcdef1"), "", "fix"),
                                        (f'Defect 1 · "Accept Row 1; Row 2 must be fixed" · {sha}', "", "fix"),
                                        (both, "carried from check-1", "done"), (both, "0 of 300", "fix")]:
            (self.run_dir / "receipts/check-2.md").unlink(missing_ok=True)
            (self.run_dir / "spec.md").write_text(f"{spec}\n## Accepted\n- {lines}\n")
            self.commit("accept")
            with open(self.run_dir / "receipts/check-1.md", "a") as receipt:
                receipt.write("\nedited after the acceptance\n")
            self.commit("edit receipt")
            if check2:  # a later check at the same code, after the acceptance
                self.receipt(2, "BROKEN", f"- 1. app.py: x -> crash -> ok, {check2}", sha)
                text = (self.run_dir / "receipts/check-2.md").read_text()
                (self.run_dir / "receipts/check-2.md").write_text(text.replace("`cmd` -> ok", check2, 1))
                self.commit("check-2")
            self.assertEqual(self.next()["step"], expected, (lines, check2))

    def test_next_stops_at_each_wait_point_until_its_yes(self):
        spec, notes, path, start = self.run_dir / "spec.md", self.run_dir / "notes.md", self.run_dir / "receipts/check-1.md", self.git("rev-parse", "HEAD")
        gate, ask, checks = "- Gate: publish the release to npm.", "- Ask first: the config.json shape", ["## Human checks", "- try it on the laptop"]
        cases = [  # spec lines, receipt row 1 and maybe, notes: expected step and session, text the blocker names
            ([ask], None, "", ("build", "fresh"), None),
            ([ask], None, "## Approach\nYes: gate\nYes: done\n- the human said Yes: approach\n", ("human", None), ask[14:]),
            ([ask], None, "## Approach\nYes: approach · \"go\" · 2026-11-09\n", ("build", "builder"), None),
            ([gate], ("WAITING", "none"), "", ("human", None), gate[8:-1]),
            ([gate], ("WAITING", "none"), "Yes: gate · \"go\" · 2026-11-09\n", ("live", "builder"), None),
            (checks, ("PROVED", "none"), "", ("human", None), "Human check: try it on the laptop"),
            ([], ("PROVED", "None of the Windows flows ran."), "", ("human", None), "Maybe: None of the Windows"),
            (checks, ("PROVED", "slow on big repos"), "Yes: done · \"ok\" · 2026-11-09\n", ("done", "builder"), None)]
        for lines, receipt, text, expected, named in cases:
            self.git("reset", "-q", "--hard", start)
            (self.run_dir / "receipts").mkdir(exist_ok=True)
            spec.write_text(spec.read_text().replace("## Human checks\n- none", "").replace("- Gate: none.\n", "") + "\n".join(lines) + "\n")
            notes.write_text(text)
            if receipt:
                self.state(receipt[0], code=True)
                path.write_text(path.read_text().replace("- <none>", f"- {receipt[1]}"))
            self.commit("state")
            self.assertEqual(((n := self.next())["step"], n["session"]), expected, (lines, receipt, text))
            if named:
                self.assertIn(named, n["blocker"])
                self.assertEqual((n["role"], n["model"], n["command"]), ("human", None, None))
                # Any session's card sends the human to the builder session with one message, no options.
                card = self.jflow("next", "demo")
                self.assertTrue(card.startswith(f"Next: you decide. {ask_line(n)} Send this in the builder session"), card)
                self.assertTrue(card.endswith("```text\njflow demo\n```"), card)
                self.assertNotIn("A.", card)
                # The builder session asks the question itself; the human replies there.
                ask = self.jflow("next", "demo", "--ask")
                self.assertEqual(ask, n["blocker"])
                self.assertIn("\n\n**➡️ A. ", ask)
                self.assertTrue(ask.endswith("\n\nReply A or B."), ask)
                self.assertNotIn("```", ask)

    def test_next_types_wait_points_and_edits_waits_for_its_own_yes(self):
        spec, notes, start = self.run_dir / "spec.md", self.run_dir / "notes.md", self.git("rev-parse", "HEAD")
        edits = "## Proposed edits\n- PRODUCT.md: mark Prove the run reached\n- TODO.md: drop the demo line\n"
        ydone, yedits = 'Yes: done · "ok" · 2026-11-24\n', 'Yes: edits · "yes" · 2026-11-24\n'
        human = ("## Human checks\n- none", "## Human checks\n- try it on the laptop")
        edge = "- 1. [edge] app.py: odd -> y -> z. Evidence: run"
        cases = [  # spec edit, receipt (row 1, defects) or None, notes: expected step and wait_point
            (("- Gate: none.", "- Gate: none.\n- Ask first: schema."), None, "## Approach\n- v1\n", "human", "approach"),
            (("- Gate: none.", "- Gate: publish."), ("WAITING", "- none"), "", "human", "gate"),
            (human, ("PROVED", "- none"), edits, "human", "done"),
            (human, ("PROVED", "- none"), edits + ydone, "human", "edits"),
            (human, ("PROVED", "- none"), edits + yedits, "human", "done"),
            (human, ("PROVED", "- none"), edits + ydone + yedits, "done", None),
            (None, ("PROVED", "- none"), edits, "human", "edits"),
            (None, ("PROVED", "- none"), edits + yedits, "done", None),
            (None, ("BROKEN", "- none"), "Checks allowed: 1\n", "human", None),
            (None, ("BLOCKED", "- none"), "", "human", None),
            (None, ("PROVED", edge), "", "human", None),
            (None, None, "", "build", None)]
        for edit, receipt, text, step, wp in cases:
            self.git("reset", "-q", "--hard", start)
            (self.run_dir / "receipts").mkdir(exist_ok=True)
            if edit:
                spec.write_text(spec.read_text().replace(*edit))
            notes.write_text(text)
            self.commit("state")
            if receipt:
                self.state(*receipt, code=True)
            n = self.next()
            self.assertEqual((n["step"], n.get("wait_point")), (step, wp), (edit, receipt, text))
            self.assertEqual("wait_point" in n, bool(wp))
            if wp == "edits":
                self.assertIn("- PRODUCT.md: mark Prove the run reached\n- TODO.md: drop the demo line", n["blocker"])
                self.assertEqual((n["role"], n["session"]), ("human", None))
            if step == "done":
                self.assertEqual(n["session"], "builder")
        # A mid-run re-spec voids earlier Proposed edits and Yes: edits: they neither stop nor clear.
        self.git("reset", "-q", "--hard", start)
        notes.write_text(edits + yedits)
        self.commit("edits approved")
        self.state("PROVED", code=True)
        self.assertEqual(self.next()["step"], "done")
        spec.write_text(spec.read_text().replace("1. Prove the run.", "1. Prove the revised run."))
        self.commit("respec")
        (self.repo / "app.py").write_text("a = 30\n")
        self.commit("build v2")
        self.receipt(2, "PROVED", "- none")
        self.commit("check-2")
        self.assertNotIn("wait_point", n := self.next())
        self.assertEqual(n["step"], "done")
        # Another yes appended under the old proposal leaves it old.
        with notes.open("a") as f:
            f.write(ydone)
        self.commit("yes done after respec")
        self.assertEqual(self.next()["step"], "done")
        # The same edits posted again in a fresh section need a fresh yes.
        with notes.open("a") as f:
            f.write("\n" + edits)
        self.commit("repost")
        self.assertEqual(self.next().get("wait_point"), "edits")
        self.git("reset", "-q", "--hard", "HEAD^")
        # An old proposal line copied into another section is no new proposal.
        with notes.open("a") as f:
            f.write("\n## Deferred\n- PRODUCT.md: mark Prove the run reached\n")
        self.commit("deferred note")
        self.assertEqual(((n := self.next())["step"], n.get("wait_point")), ("done", None))
        # A proposal revised under its old heading and old yes waits, and shows every edit, kept ones too.
        notes.write_text(edits.replace("drop", "keep") + yedits)
        self.commit("new edits")
        self.assertEqual((n := self.next()).get("wait_point"), "edits")
        self.assertIn("- PRODUCT.md: mark Prove the run reached\n- TODO.md: keep the demo line", n["blocker"])
        # Only a committed yes counts.
        with notes.open("a") as f:
            f.write('Yes: edits · "go" · 2026-11-25\n')
        self.assertEqual(self.next().get("wait_point"), "edits")
        self.commit("fresh yes")
        self.assertEqual((n := self.next())["step"], "done")
        self.assertNotIn("wait_point", n)

    def test_next_mid_run_respec_resets_routing_cap_trend_and_approvals(self):
        spec, notes = self.run_dir / "spec.md", self.run_dir / "notes.md"
        spec.write_text(spec.read_text().replace("- Gate: none.", "- Gate: publish.\n- Ask first: schema."))
        notes.write_text('## Approach\n- v1\nYes: approach · "ok" · 2026-11-22\nYes: gate · "ok" · 2026-11-22\n')
        self.commit("spec with gate")
        self.state("WAITING", code=True)
        self.assertEqual(self.next()["step"], "live")
        # Mid-run re-spec (non-Accepted edit): routes to build (not live), invalidates Yes: approach & Yes: gate.
        spec.write_text(spec.read_text().replace("1. Prove the run.", "1. Prove the revised run."))
        self.commit("mid-run respec")
        n = self.next()
        self.assertEqual(n["step"], "human")
        self.assertIn("Approve the approach", n["blocker"])
        with notes.open("a") as f:
            f.write('Yes: approach · "ok v2" · 2026-11-23\n')
        self.commit("fresh approach yes")
        self.assertEqual(self.next()["step"], "build")
        (self.repo / "app.py").write_text("a = 10\n")
        self.commit("build v2")
        self.assertEqual((self.next()["step"], self.next()["n"]), ("check", 2))
        self.receipt(2, "WAITING", "- none")
        self.commit("check-2")
        n = self.next()
        self.assertEqual(n["step"], "human")
        self.assertIn("the live gate", n["blocker"])
        with notes.open("a") as f:
            f.write('Yes: gate · "go v2" · 2026-11-23\n')
        self.commit("fresh gate yes")
        self.assertEqual(self.next()["step"], "live")

    def test_next_mid_run_respec_resets_check_cap_and_defect_trend(self):
        spec, notes = self.run_dir / "spec.md", self.run_dir / "notes.md"
        for k in range(1, 4):
            (self.repo / "app.py").write_text(f"a = {k + 1}\n")
            self.commit(f"code {k}")
            self.receipt(k, "BROKEN", "- 1. [use] app.py: x -> y -> z. Evidence: run\n- 2. [use] app.py: p -> q -> r. Evidence: run")
            self.commit(f"check-{k}")
        notes.write_text("Checks allowed: 2\n")
        self.commit("prior cap")
        self.assertIn("3 checks used of 2", self.next()["blocker"])
        # Mid-run re-spec resets budget to 3 and clears trend against check-3.
        spec.write_text(spec.read_text().replace("1. Prove the run.", "1. Prove the new scope."))
        self.commit("respec")
        self.assertEqual(self.next()["step"], "build")
        (self.repo / "app.py").write_text("a = 20\n")
        self.commit("build after respec")
        self.receipt(4, "BROKEN", "- none")
        self.commit("check-4")
        self.assertEqual((self.next()["step"], self.next()["n"]), ("fix", 4))
        with notes.open("a") as f:
            f.write("Checks allowed: 1\n")
        self.commit("lower cap after respec")
        blocker = self.next()["blocker"]
        self.assertIn("1 checks used of 1", blocker)
        self.assertNotIn("went from", blocker)
        self.assertIn("➡️ A. Stop here", blocker)

    def test_next_carried_newest_sha_accepted_row_on_late_and_twice_carried_escalation(self):
        spec, notes = self.run_dir / "spec.md", self.run_dir / "notes.md"
        # 1) Newest-sha acceptance of a carried defect closes it.
        (self.repo / "app.py").write_text("a = 2\n")
        self.commit("code 1")
        sha1 = self.git("rev-parse", "HEAD")
        self.receipt(1, "PROVED", "- 1. [use] app.py: x -> bad -> ok. Evidence: run", sha1)
        self.commit("check-1")
        (self.repo / "app.py").write_text("a = 3\n")
        self.commit("code 2")
        sha2 = self.git("rev-parse", "HEAD")
        self.receipt(2, "PROVED", "- 1. [use] app.py (carried from check-1): x -> bad -> ok. Evidence: run", sha2)
        self.commit("check-2")
        self.assertEqual(self.next()["step"], "fix")
        # 2) Twice-carried [use] defect escalates to human instead of looping fix.
        notes.write_text("Dispute: intentional behavior.\n")
        self.commit("rebuttal")
        self.receipt(3, "PROVED", "- 1. [use] app.py (carried from check-1): x -> bad -> ok. Evidence: run", sha2)
        self.commit("check-3")
        n = self.next()
        self.assertEqual(n["step"], "human")
        self.assertIn("defect 1 carried unchanged across two checks", n["blocker"])
        self.assertIn("➡️ A. Accept", n["blocker"])
        # Non-carried defect or BROKEN row still routes to fix.
        self.receipt(3, "BROKEN", "- 1. [use] app.py (carried from check-1): x -> bad -> ok. Evidence: run", sha2)
        self.commit("check-3 broken")
        self.assertEqual(self.next()["step"], "fix")
        self.receipt(3, "PROVED", "- 1. [use] app.py (carried from check-2): x -> bad -> ok. Evidence: run", sha2)
        self.commit("check-3 carried from check-2")
        self.assertEqual(self.next()["step"], "human")
        # Accepting with newest sha closes the carried defect.
        with spec.open("a") as f:
            f.write(f'\n## Accepted\n- Defect 1 · disputed · "accept it" · 2026-11-23 · {sha2}\n')
        self.commit("accept newest sha")
        self.assertEqual(self.next()["step"], "done")

    def test_next_treats_accepted_rows_as_closed_in_late_checks(self):
        spec, notes = self.run_dir / "spec.md", self.run_dir / "notes.md"
        (self.repo / "app.py").write_text("a = 2\n")
        self.commit("code 1")
        sha1 = self.git("rev-parse", "HEAD")
        self.receipt(1, "WAITING", "- none", sha1)
        self.commit("check-1")
        with spec.open("a") as f:
            f.write(f'\n## Accepted\n- Row 1 · ok · "fine" · 2026-11-23 · {sha1}\n')
        self.commit("accept row 1")
        (self.repo / "app.py").write_text("a = 3\n")
        self.commit("code 2")
        sha2 = self.git("rev-parse", "HEAD")
        notes.write_text("Checks allowed: 2\n")
        (self.run_dir / "receipts/check-2.md").write_text(
            f"# check-2 @ {sha2} · GPT-6.1 Sol · high\n| # | Verdict | Evidence |\n|---|---|\n"
            f"| 1 | ACCEPTED | accepted in check-1 |\n| 2 | WAITING | `cmd` -> wait |\n\n## Defects\n- none\n\n## Maybes\n- <none>\n")
        self.commit("check-2")
        (self.repo / "app.py").write_text("a = 4\n")
        self.commit("late code")
        self.assertIn("2 checks used of 2 and check is next", self.next()["blocker"])
        with spec.open("a") as f:
            f.write(f'- Row 2 · wait · "fine" · 2026-11-23 · {sha2}\n')
        self.commit("accept row 2")
        self.assertEqual(self.next()["step"], "done")

if __name__ == "__main__":
    unittest.main()
