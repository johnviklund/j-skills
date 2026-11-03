"""Next-step's CLI contract on small, independent run and routing fixtures."""
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "next-step.py"
ROUTING = """## Seat mapping
| Seat | Vendor | Model | Trial | Fallback chain | Notes |
|---|---|---|---|---|---|
| Strict reviewer | Anthropic | Opus 5.5 | — | Anthropic · Sonnet 5.5 · xhigh; OpenAI · GPT-6 Sol · xhigh | |
| Heavy executor | OpenAI | GPT-6.1 Sol | — | OpenAI · GPT-6 Sol | |
| Default executor | OpenAI | GPT-6.1 Sol | — | OpenAI · GPT-6 Sol | |
| Mechanical lane | OpenAI | GPT-6.1 Sol | — | OpenAI · GPT-6 Sol | |
| Brainstorm partner | Anthropic | Sonnet 5.5 | — | OpenAI · GPT-6 Sol | |
## Phase → seat · effort · approval
| Key | Phase / work | Seat | Effort | Context | Approval | Notes |
|---|---|---|---|---|---|---|
| plan | Plan | Strict reviewer | high | large | human | |
| execute:contract | Execute contract | Heavy executor | xhigh | standard | auto | |
| execute:logic | Execute logic | Default executor | high | standard | auto | |
| execute:operator | Execute operator | Default executor | high | standard | human | |
| fix:P0 | Fix P0 | Heavy executor | high | standard | auto | |
| fix:logic | Fix logic | Default executor | medium | standard | auto | |
| fix:operator | Fix operator | Default executor | high | standard | human | |
| fix:mechanical | Fix mechanical | Mechanical lane | medium | standard | auto | |
| review | Review | Strict reviewer | xhigh | large | auto | |
| wrap | Wrap | Brainstorm partner | medium | standard | auto | |
| brainstorm | Brainstorm | Brainstorm partner | high | standard | human | |
| patch-plan | Patch plan | Strict reviewer | high | standard | auto | |
"""


class NextStepTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.run = self.repo / ".workflow" / "x"
        self.run.mkdir(parents=True)
        (self.run / "brainstorm.md").write_text(
            f"Command: workflow brainstorm x\nCreated: now\nBase: {self.base}\nInputs: none\nStatus: complete\n")
        self.routing = self.repo / "ROUTING.md"
        self.routing.write_text(ROUTING)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True)

    def cli(self, *args, slug="x"):
        return subprocess.run([sys.executable, str(SCRIPT), slug, "--repo", str(self.repo),
                               "--routing", str(self.routing), *args], capture_output=True, text=True)

    def result(self, *args):
        result = self.cli("--json", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def fails(self, result, *diagnostics):
        self.assertEqual((result.returncode, result.stdout), (1, ""))
        for diagnostic in diagnostics:
            self.assertIn(diagnostic, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def override(self, rows):
        (self.run / "routing.md").write_text("| Key | Vendor · Model | Effort |\n|---|---|---|\n" + rows)

    def test_override_model_keeps_route_policy(self):
        self.plan("### T1 — First\nLane: logic\nStatus: todo\n")
        for trial in (False, True):
            with self.subTest(trial=trial):
                self.routing.write_text(ROUTING.replace("| — |", "| OpenAI · Trial |") if trial else ROUTING)
                (self.run / "routing.md").unlink(missing_ok=True)
                baseline = self.result()
                self.override("| execute:logic | OpenAI · GPT-6 Sol | xhigh |\n")
                result = self.result()
                self.assertEqual(result["model"], {"vendor": "OpenAI", "name": "GPT-6 Sol", "effort": "xhigh"})
                for key in ("fallback", "context", "approval"):
                    self.assertEqual(result[key], baseline[key])
                self.assertTrue(result["override"])
                self.assertFalse(result["trial"])
                self.assertIn("- **Model:** GPT-6 Sol · xhigh · standard (override)", result["card"])
                if not trial:
                    self.assertNotIn("Warning", result["card"])
        (self.run / "decisions.md").write_text(
            "| ID | Phase | Question | Default | Status | Answer |\n| D1 | execute | Wait? | yes | waiting | |\n")
        self.assertNotIn("override", self.result())

    def test_override_unrelated_row_preserves_plan_output(self):
        baseline = self.result()
        expected = ("---\n**▶ Next: plan** · x\n\n- **Why:** The brief is complete; the run needs a plan.\n"
                    "- **Reset:** yes\n- **Model:** Opus 5.5 · high · large\n- **Fallback:** Sonnet 5.5 · xhigh\n"
                    "- **Reads:** .workflow/x/brainstorm.md\n\n**Run:**\n\n```text\nworkflow plan x\n```\n---\n")
        self.assertEqual(self.cli().stdout, expected)
        self.override("| review | Anthropic · Other | high |\n")
        self.assertEqual(self.result(), baseline)
        self.assertEqual(self.cli().stdout, expected)

    def test_override_same_vendor_warning(self):
        for key, cell in (("review", "OpenAI · GPT-6 Sol"), ("plan", "OpenAI · Other"),
                          ("fix:logic", "Anthropic · Other"), ("execute:logic", "Anthropic · Other")):
            with self.subTest(key=key):
                self.override(f"| {key} | {cell} | xhigh |\n")
                result = self.result()
                self.assertIn("- **Warning:** same vendor writes and reviews: " + cell.split(" · ")[0], result["card"])

    def test_override_bad_rows_name_key_without_json(self):
        for row, key in (("execute:nope | OpenAI · Sol | high", "execute:nope"),
                         ("review | OpenAI | high", "review"), ("review | OpenAI · Sol | max", "review"),
                         ("review | OpenAI · Sol | ", "review"), ("review | OpenAI · Sol · high | high", "review")):
            with self.subTest(row=row):
                self.override(f"| {row} |\n")
                result = self.cli("--json")
                self.fails(result, key)

    def test_key_prints_model_lines_without_a_run(self):
        for key in ("review", "nope"):
            with self.subTest(key=key):
                result = subprocess.run([sys.executable, str(SCRIPT), "--key", key,
                                         "--routing", str(self.routing)], cwd=self.temp.name,
                                        capture_output=True, text=True)
                if key == "review":
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "- **Model:** Opus 5.5 · xhigh · large\n"
                                     "- **Fallback:** Sonnet 5.5 · xhigh\n")
                else:
                    self.fails(result, "nope")

    def plan(self, tickets, name="plan.md"):
        (self.run / name).write_text(
            f"Command: workflow plan x\nCreated: now\nBase: {self.base}\nInputs: none\nStatus: complete\n"
            + "## Tickets\n" + tickets)

    def test_unattended_decision_states(self):
        path = self.run / "decisions.md"
        table = "| ID | Phase | Question | Default | Status | Answer |\n|---|---|---|---|---|---|\n"
        for blocked in (False, True):
            with self.subTest(blocked=blocked):
                self.plan("### T1 — Run\nLane: operator\nStatus: "
                          + ("awaiting-human" if blocked else "todo") + "\n")
                baseline = self.result()
                for status in ("assumed", "waiting", "answered"):
                    rows = f"| D2 | execute | Which port? | 8000 | {status} | |\n"
                    if status == "waiting":
                        rows = ("| D1 | plan | First choice? | yes | assumed | |\n" + rows
                                + "| D3 | execute | Later choice? | yes | waiting | |\n")
                    path.write_text(table + rows)
                    result = self.result()
                    if status == "waiting":
                        self.assertEqual(result["blocker"], {"decision": "D2", "action": "Which port?"})
                        self.assertIsNone(result["model"])
                        self.assertIn("**Model:** human · Which port?", result["card"])
                        self.assertIn(".workflow/x/decisions.md", result["reads"])
                    else:
                        self.assertEqual(result, baseline)
                path.unlink()

    def test_plan_ready_contract_ticket(self):
        self.plan(f"""### T1 — First
Delivers: B1 · Blocked by: none · Lane: logic
Status: done @ {self.base}
### T2 — Second
Delivers: B2 · Blocked by: T1 · Lane: contract
Status: todo
""")
        result = self.result()
        self.assertEqual(result["why"], "T2 is ready.")
        for key, value in {"phase": "execute", "ticket": "T2", "seat": "Heavy executor", "approval": "auto",
                           "model": {"vendor": "OpenAI", "name": "GPT-6.1 Sol", "effort": "xhigh"}}.items():
            self.assertEqual(result[key], value, key)

    def test_operator_handoff_waits_until_receipt_exists(self):
        self.plan("""### T3 — Run the probe
Delivers: B3 · Blocked by: none · Lane: operator
Verify: receipt: receipts/t3.txt — ok
Status: awaiting-human
""")
        receipts = self.run / "receipts"
        receipts.mkdir()
        handoff = receipts / "t3-operator-handoff.md"
        handoff.write_text("Run the probe and save receipts/t3.txt.\n")
        (receipts / "t4-operator-handoff.md").write_text("A different ticket's handoff.\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "handoff")
        result = self.result()
        self.assertEqual(result["blocker"]["ticket"], "T3")
        self.assertEqual(result["why"], "T3 is awaiting human action.")
        self.assertNotIn("t4-operator-handoff.md", str(result["reads"]) + result["blocker"]["action"])
        self.assertIn("receipts/t3-operator-handoff.md", result["blocker"]["action"])
        self.assertIn("Run the probe", result["blocker"]["action"])
        self.assertIn(".workflow/x/receipts/t3-operator-handoff.md", result["reads"])
        self.assertIsNone(result["model"])
        self.assertEqual(result["command"], "workflow execute x")
        self.assertIn("- **Model:** human · ", result["card"])
        (receipts / "t3.txt").write_text("ok\n")
        result = self.result()
        self.assertEqual((result["phase"], result["ticket"], result["blocker"]), ("execute", "T3", None))

    def test_backticked_receipt_resumes_operator(self):
        self.plan("### T3 — Run\nLane: operator\nVerify: receipt: `receipts/t3.txt` — ok\nStatus: awaiting-human\n")
        self.assertEqual(self.result()["blocker"]["ticket"], "T3")
        (self.run / "receipts").mkdir()
        (self.run / "receipts/t3.txt").write_text("ok\n")
        result = self.result()
        self.assertEqual((result["phase"], result["ticket"], result["blocker"]), ("execute", "T3", None))

    def test_plan_skips_ticket_with_unfinished_dependency(self):
        self.plan("""### T2 — Blocked
Delivers: B2 · Blocked by: T1 · Lane: contract
Status: todo
### T1 — Ready
Delivers: B1 · Blocked by: none · Lane: logic
Status: todo
""")
        self.assertEqual(self.result()["ticket"], "T1")

    def test_patch_ticket_routes_by_severity_and_lane(self):
        self.plan("### T1 — Plan work\nLane: contract\nStatus: todo\n")
        for cycle, severity, lane, seat, effort in [(1, "P0", "logic", "Heavy executor", "high"),
                                                  (1, "P1", "logic", "Default executor", "medium"),
                                                  (1, "P3", "mechanical", "Mechanical lane", "medium"),
                                                  (2, "P1", "logic", "Default executor", "medium")]:
            with self.subTest(cycle=cycle, severity=severity, lane=lane):
                self.plan(f"### C{cycle}-T1 — Fix\nFixes: C1-1 ({severity})\nLane: {lane}\nStatus: todo\n", "patch_plan.md")
                result = self.result()
                for key, value in {"phase": "execute", "ticket": f"C{cycle}-T1", "seat": seat,
                                   "why": f"Patch cycle {cycle} · fix C1-1",
                                   "model": {"vendor": "OpenAI", "name": "GPT-6.1 Sol", "effort": effort}}.items():
                    self.assertEqual(result[key], value, key)
        patch = self.run / "patch_plan.md"
        patch.write_text(patch.read_text().replace("Status: todo", f"Status: done @ {self.base}"))
        self.assertEqual(self.result()["ticket"], "T1")

    def test_p0_fix_keeps_lane_approval(self):
        for lane, approval in [("operator", "human"), ("logic", "auto")]:
            with self.subTest(lane=lane):
                self.plan(f"### C1-T1 — Fix\nFixes: C1-1 (P0)\nLane: {lane}\nStatus: todo\n", "patch_plan.md")
                result = self.result()
                self.assertEqual([result[k] for k in ("key", "seat", "model", "fallback", "approval")],
                                 ["fix:P0", "Heavy executor", {"vendor": "OpenAI", "name": "GPT-6.1 Sol", "effort": "high"},
                                  [{"vendor": "OpenAI", "name": "GPT-6 Sol", "effort": "high"}], approval])
        self.routing.write_text(ROUTING.replace("| fix:operator | Fix operator | Default executor | high | standard | human | |\n", ""))
        self.plan("### C1-T1 — Fix\nFixes: C1-1 (P0)\nLane: operator\nStatus: todo\n", "patch_plan.md")
        result = self.cli("--json")
        self.fails(result, "missing key fix:operator")

    def test_blocker_selects_awaiting_ticket_after_blocked_todo(self):
        self.plan("### T1 — Blocked\nBlocked by: T2 · Lane: logic\nStatus: todo\n"
                  "### T2 — Awaiting\nLane: operator\nStatus: awaiting-human\n")
        self.assertEqual(self.result()["blocker"]["ticket"], "T2")

    def test_fully_blocked_plan_has_diagnostic(self):
        self.plan("### T1 — Blocked\nBlocked by: T9 · Lane: logic\nStatus: todo\n")
        result = self.cli("--json")
        self.fails(result, "no ready ticket")

    def test_invalid_slug_and_repository_have_diagnostics(self):
        with tempfile.TemporaryDirectory() as outside:
            for slug, args, diagnostic in [("../x", (), "slug must contain"),
                                           ("x", ("--repo", outside), "not inside a git repo")]:
                with self.subTest(slug=slug, args=args):
                    result = self.cli("--json", *args, slug=slug)
                    self.fails(result, diagnostic)

    def test_patch_ticket_without_fixes_fails_without_json(self):
        for fixes in ("", "C1-1 (P9)", "T1 (P1)", "C1-1 (P1) junk"):
            with self.subTest(fixes=fixes):
                self.plan(f"### C1-T1 — Fix\nFixes: {fixes}\nLane: logic\nStatus: todo\n", "patch_plan.md")
                result = self.cli("--json")
                self.fails(result, "C1-T1", "Fixes: C<n>-<m> (P#)")

    def review(self, findings=""):
        self.plan(f"### T1 — Finished\nLane: logic\nStatus: done @ {self.base}\n")
        (self.run / "review.md").write_text(
            f"Command: workflow review x\nCreated: now\nBase: {self.base}\nInputs: none\nStatus: complete\n"
            + f"## Cycle 1 findings\n{findings}\n## Cycle 1 verdict\nship\n")

    def test_finished_plan_needs_review_then_wrap(self):
        self.plan(f"### T1 — Finished\nLane: logic\nStatus: done @ {self.base}\n")
        result = self.result()
        for key, value in {"phase": "review", "seat": "Strict reviewer", "context": "large",
                           "model": {"vendor": "Anthropic", "name": "Opus 5.5", "effort": "xhigh"}}.items():
            self.assertEqual(result[key], value, key)
        self.review()
        result = self.result()
        self.assertIn("- **Reset:** no", result["card"])
        for key, value in {"phase": "wrap", "seat": "Brainstorm partner", "reset": False,
                           "model": {"vendor": "Anthropic", "name": "Sonnet 5.5", "effort": "medium"}}.items():
            self.assertEqual(result[key], value, key)

    def test_review_receipt_rule_diff(self):
        self.review()
        for path, expected in [("tool.py", "review"), ("notes.md", "wrap")]:
            with self.subTest(path=path):
                (self.repo / path).write_text("changed\n")
                self.git("add", path)
                self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "change")
                self.assertEqual(self.result()["phase"], expected)
                self.git("reset", "--hard", self.base)

    def test_open_finding_needs_patch_or_recheck(self):
        self.review("### P1 — Defect\n- Disposition: fix now\n")
        result = self.result()
        self.assertIn("C1-1", str(result["blocker"]))
        self.assertEqual(result["command"], "workflow review x")
        self.plan(f"### C1-T1 — Fix\nFixes: C1-1 (P1)\nLane: logic\nStatus: done @ {self.base}\n", "patch_plan.md")
        result = self.result()
        self.assertEqual((result["phase"], result["blocker"]), ("review", None))
        patch = self.run / "patch_plan.md"
        patch.write_text(patch.read_text().replace("C1-", "C2-"))
        self.assertIn("C1-1", str(self.result()["blocker"]))
        patch.unlink()
        for finding in ["### P2 — Later\n- Disposition: defer\n",
                        f"### P1 — Fixed\n- Disposition: fix now\n- Resolved: @ {self.base}\n"]:
            with self.subTest(finding=finding):
                self.review(finding)
                self.assertEqual(self.result()["phase"], "wrap")

    def test_objected_fix_counts_finished_and_returns_to_review(self):
        self.review("### P1 — Defect\n- Disposition: fix now\n### P2 — Other\n- Disposition: fix now\n")
        objected = "### C1-T1 — Fix\nFixes: C1-1 (P1)\nLane: logic\nStatus: objected\nObjection: passes\n"
        later = "### C1-T2 — Next\nFixes: C1-2 (P2)\nLane: logic\nBlocked by: C1-T1\nStatus: {}\n"
        self.plan(objected + later.format("todo"), "patch_plan.md")
        self.assertEqual(self.result()["ticket"], "C1-T2")
        self.plan(objected + later.format(f"done @ {self.base}"), "patch_plan.md")
        result = self.result()
        self.assertEqual((result["phase"], result["blocker"]), ("review", None))
        self.assertEqual(result["why"], "C1-T1 objected; judge each objection, then re-review")

    def test_prior_cycle_finding_blocks_wrap_until_resolved(self):
        for resolved, phase in [("—", "review"), (f"@ {self.base}", "wrap")]:
            with self.subTest(resolved=resolved):
                self.review("### P1 — Old\n- Disposition: fix now\n"
                            f"- Resolved: {resolved}\n## Cycle 2 findings\n## Cycle 2 verdict\nship\n")
                result = self.result()
                self.assertEqual((result["phase"], result["command"]), (phase, f"workflow {phase} x"))
                self.assertEqual(result["blocker"]["findings"] if result["blocker"] else [],
                                 ["C1-1"] if phase == "review" else [])

    def test_folded_resolved_findings_keep_open_ids(self):
        for resolved, cycles, expected, why in [
                (("C1-1", "C2-1"), ((2, 1), (3, 1)), ["C2-2", "C3-1"], "Patch cycle 3 · fix C2-2, C3-1"),
                (("C2-2",), ((2, 2),), ["C2-1", "C2-3"], "Patch cycle 2 · fix C2-1, C2-3")]:
            with self.subTest(resolved=resolved):
                self.review("## Resolved\n| Finding | Title | Resolved |\n"
                            + "".join(f"| {id} | C2-2 | @ {self.base} |\n" for id in resolved)
                            + "\n"
                            + "".join(f"## Cycle {cycle} findings\n"
                                      + "### P1 — Open\n- Disposition: fix now\n- Resolved: —\n" * count
                                      for cycle, count in cycles))
                result = self.result()
                self.assertEqual(result["blocker"]["findings"], expected)
                self.assertEqual(result["why"], why)

    def test_other_artifacts_drafting(self):
        for name, phase, key in [("plan.md", "plan", "plan"), ("review.md", "review", "review"),
                                  ("patch_plan.md", "review", "patch-plan")]:
            with self.subTest(name=name):
                self.review()
                if name == "patch_plan.md":
                    self.plan("### C1-T1 — Fix\nLane: logic\nStatus: todo\n", name)
                doc = self.run / name
                doc.write_text(doc.read_text().replace("Status: complete", "Status: drafting"))
                result = self.result()
                self.assertEqual((result["phase"], result["key"], result["ticket"]), (phase, key, None))

    def test_review_rejects_unknown_base(self):
        self.review()
        doc = self.run / "review.md"
        doc.write_text(doc.read_text().replace(self.base, "deadbeef"))
        result = self.cli("--json")
        self.fails(result, "review.md: unknown Base deadbeef")

    def test_brief_drafting_parked_and_done(self):
        brief = self.run / "brainstorm.md"
        original = brief.read_text()
        for status, phase, command in [("drafting", "brainstorm", "workflow brainstorm x"),
                                        ("parked", "parked", "workflow plan x"), ("done", "done", None)]:
            with self.subTest(status=status):
                brief.write_text(original.replace("Status: complete", f"Status: {status}"))
                result = self.result()
                self.assertEqual((result["phase"], result["command"]), (phase, command))
        brief.write_text(original.replace("Status: complete", "Status: bogus"))
        self.fails(self.cli("--json"), "unknown brief status bogus")

        brief.write_text(original.replace("Status: complete", "Status: done"))
        self.override("| execute:mechanical | OpenAI · GPT-6 Sol | high |\n")
        self.assertEqual(self.result()["phase"], "done")

    def test_parked_run_resumes_after_planning(self):
        brief = self.run / "brainstorm.md"
        brief.write_text(brief.read_text().replace("Status: complete", "Status: parked"))
        for status, phase in [("todo", "execute"), (f"done @ {self.base}", "review")]:
            with self.subTest(status=status):
                self.plan(f"### T1 — First\nLane: logic\nStatus: done @ {self.base}\n"
                          f"### T2 — Second\nLane: logic\nStatus: {status}\n")
                result = self.result()
                self.assertEqual((result["phase"], result["command"]), ("parked", f"workflow {phase} x"))

    def test_brief_plan_card_and_json(self):
        result = self.result()
        expected = {"schema_version": 1, "slug": "x", "phase": "plan", "command": "workflow plan x",
                    "seat": "Strict reviewer", "context": "large", "reset": True, "blocker": None,
                    "model": {"vendor": "Anthropic", "name": "Opus 5.5", "effort": "high"}}
        for key, value in expected.items():
            self.assertEqual(result[key], value, key)
        self.assertEqual(result["fallback"], [{"vendor": v, "name": n, "effort": "xhigh"}
                         for v, n in [("Anthropic", "Sonnet 5.5"), ("OpenAI", "GPT-6 Sol")]])
        self.assertEqual(self.cli().stdout, result["card"])
        for prefix in ("", "/"):
            with self.subTest(prefix=prefix):
                card = self.result("--prefix", prefix)["card"]
                for line in ("- **Model:** Opus 5.5 · high · large", "- **Fallback:** Sonnet 5.5 · xhigh",
                             f"```text\n{prefix}workflow plan x\n```"):
                    self.assertIn(line, card)

    def test_trial_and_phase_effort_fallback(self):
        self.routing.write_text(ROUTING.replace("| — |", "| OpenAI · GPT-6.1 Sol |").replace(" · xhigh", ""))
        result = self.result()
        self.assertTrue(result["trial"])
        self.assertEqual(result["model"], {"vendor": "OpenAI", "name": "GPT-6.1 Sol", "effort": "high"})
        self.assertEqual(result["fallback"][0], {"vendor": "Anthropic", "name": "Opus 5.5", "effort": "high"})
        self.assertEqual(result["fallback"][1]["effort"], "high")
        self.assertIn("- **Model:** GPT-6.1 Sol · high · large (trial)\n", result["card"])

    def test_bad_routing_names_the_row_and_emits_no_json(self):
        row = "| plan | Plan | Strict reviewer | high | large | human | |\n"
        cases = [(ROUTING.replace(" | human | |", " | human |"), "plan"),
                 (ROUTING.replace("| high |", "| max |"), "plan"),
                 (ROUTING[:ROUTING.index("| plan |")], "plan"),
                 (ROUTING.replace("| Seat | Vendor", "| Seat | Provider"), "Seat"),
                 (ROUTING.replace("| Opus 5.5 |", "| |"), "Strict reviewer"),
                 (ROUTING.replace("| Plan |", "| |"), "plan"),
                 (ROUTING + row, "plan"), (ROUTING.replace("Seat mapping", "Other"), "Seat mapping"),
                 (ROUTING.replace("| large |", "| huge |"), "plan"),
                 (ROUTING.replace("| human |", "| sometimes |"), "plan"),
                 (ROUTING.replace(row, row.replace("Strict reviewer", "Unknown")), "plan")]
        for trial in ("OpenAI", "OpenAI · ", "OpenAI · Sol · max", "OpenAI · Sol · high · extra"):
            cases.append((ROUTING.replace("| — |", f"| {trial} |"), "Strict reviewer"))
        unused = "| Unused | OpenAI | Sol | OpenAI · Sol · max | OpenAI · Sol | |\n"
        cases.append((ROUTING.replace("## Phase", unused + "## Phase"), "Unused"))
        for bad, diagnostic in cases:
            with self.subTest(routing=bad):
                self.routing.write_text(bad)
                result = self.cli("--json")
                self.fails(result, diagnostic)

    def test_real_routing_resolves_all_thirteen_run_keys(self):
        spec = importlib.util.spec_from_file_location("next_step", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        path = SCRIPT.parents[1] / "ROUTING.md"
        routes = module.routing(path)
        keys = ["brainstorm", "plan", "review", "wrap", "fix:P0"]
        keys += [f"{phase}:{lane}" for phase in ("execute", "fix") for lane in ("logic", "contract", "mechanical", "operator")]
        for key in keys:
            with self.subTest(key=key):
                self.assertIn(routes[key]["model"]["effort"], ("medium", "high", "xhigh"))
        self.assertLessEqual(path.stat().st_size, 5500)


class StateSpaceTests(unittest.TestCase):
    """Every combination of run artifact states, checked against SKILL.md's state table."""

    def test_state_space_routes_only_finished_work_to_wrap(self):
        spec = importlib.util.spec_from_file_location("next_step", SCRIPT)
        ns = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ns)
        with tempfile.TemporaryDirectory() as tmp:
            repo, run = Path(tmp), Path(tmp) / ".workflow" / "x"
            git = lambda *a: subprocess.run(["git", "-C", tmp, *a], check=True, capture_output=True, text=True).stdout.strip()
            git("init", "-q", "-b", "main")
            shas = []
            for name in ("base", "code"):
                (repo / "tool.py").write_text(name)
                git("add", "-A")
                git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", name)
                shas.append(git("rev-parse", "HEAD"))
            run.mkdir(parents=True)
            (repo / "ROUTING.md").write_text(ROUTING)
            routes = ns.routing(repo / "ROUTING.md")
            head = lambda cmd, status, base=shas[0]: (f"Command: workflow {cmd} x\nCreated: now\nBase: {base}\n"
                                                      f"Inputs: none\nStatus: {status}\n")
            ticket = lambda tid, status: (f"### {tid} — T\nFixes: C1-1 (P1)\nLane: logic\nStatus: {status}\n"
                                          + ("Objection: passes\n" if status == "objected" else ""))
            done = f"done @ {shas[0]}"
            plans = {"none": None, "drafting": head("plan", "drafting") + ticket("T1", "todo"),
                     **{name: head("plan", "complete") + ticket("T1", status) for name, status in
                        (("todo", "todo"), ("awaiting", "awaiting-human"), ("done", done))}}
            patches = {"none": None, "drafting": head("review", "drafting") + ticket("C1-T1", "todo"),
                       **{name: head("review", "complete") + ticket("C1-T1", status) for name, status in
                          (("todo", "todo"), ("done", done), ("objected", "objected"))}}
            findings = {"none": None, "drafting": "", "open": "### P1 — D\n- Disposition: fix now\n",
                        "resolved": f"### P1 — D\n- Disposition: fix now\n- Resolved: @ {shas[1]}\n",
                        "deferred": "### P2 — D\n- Disposition: defer\n"}
            for brief, plan, patch, review, moved in itertools.product(
                    ("complete", "parked"), plans, patches, findings, (False, True)):
                status = "drafting" if review == "drafting" else "complete"
                files = {"brainstorm.md": head("brainstorm", brief), "plan.md": plans[plan], "patch_plan.md": patches[patch],
                         "review.md": None if review == "none" else head("review", status, shas[0 if moved else 1])
                         + f"## Cycle 1 findings\n{findings[review]}\n## Cycle 1 verdict\nship\n"}
                for name, text in files.items():
                    (run / name).unlink(missing_ok=True) if text is None else (run / name).write_text(text)
                with self.subTest(brief=brief, plan=plan, patch=patch, review=review, moved=moved):
                    step = ns.next_step(repo, "x", routes)
                    ready = (plan == "done" and patch in ("none", "done", "objected")
                             and review in ("resolved", "deferred") and not moved)
                    if brief == "parked":
                        self.assertEqual(step["phase"], "parked")
                    else:
                        self.assertEqual(step["phase"] == "wrap", ready)
                    if plan == patch == "none":  # a patch plan only exists after a plan and a review
                        self.assertEqual(step["key"], "plan")
                    if step["key"].startswith(("execute", "fix")):
                        doc = (run / ("patch_plan.md" if step["ticket"].startswith("C") else "plan.md")).read_text()
                        self.assertIn("Status: complete", doc)
                        self.assertRegex(doc, rf"### {step['ticket']} — T\nFixes: \S+ \(P1\)\nLane: logic\n"
                                              r"Status: (todo|awaiting-human)\n")
                    for finding in (step["blocker"] or {}).get("findings", []):
                        self.assertEqual((finding, review), ("C1-1", "open"))
