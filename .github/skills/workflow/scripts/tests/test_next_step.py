"""Next-step's CLI contract on small, independent run and routing fixtures."""
import importlib.util
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

    def test_key_prints_model_lines_without_a_run(self):
        for key, expected_code in (("review", 0), ("nope", 1)):
            with self.subTest(key=key):
                result = subprocess.run([sys.executable, str(SCRIPT), "--key", key,
                                         "--routing", str(self.routing)], cwd=self.temp.name,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, expected_code, result.stderr)
                if key == "review":
                    self.assertEqual(result.stdout, "- **Model:** Opus 5.5 · xhigh · large\n"
                                     "- **Fallback:** Sonnet 5.5 · xhigh\n")
                else:
                    self.assertEqual(result.stdout, "")
                    self.assertIn("nope", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def plan(self, tickets, name="plan.md"):
        (self.run / name).write_text(
            f"Command: workflow plan x\nCreated: now\nBase: {self.base}\nInputs: none\nStatus: complete\n"
            + "## Tickets\n" + tickets)

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
        for severity, lane, seat, effort in [("P0", "logic", "Heavy executor", "high"),
                                           ("P1", "logic", "Default executor", "medium"),
                                           ("P3", "mechanical", "Mechanical lane", "medium")]:
            with self.subTest(severity=severity, lane=lane):
                self.plan(f"### C1-T1 — Fix\nFixes: C1-1 ({severity})\nLane: {lane}\nStatus: todo\n", "patch_plan.md")
                result = self.result()
                for key, value in {"phase": "execute", "ticket": "C1-T1", "seat": seat,
                                   "why": "Patch cycle 1 · fix C1-1",
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
        self.assertEqual((result.returncode, result.stdout), (1, ""))
        self.assertIn("missing key fix:operator", result.stderr)

    def test_blocker_selects_awaiting_ticket_after_blocked_todo(self):
        self.plan("### T1 — Blocked\nBlocked by: T2 · Lane: logic\nStatus: todo\n"
                  "### T2 — Awaiting\nLane: operator\nStatus: awaiting-human\n")
        self.assertEqual(self.result()["blocker"]["ticket"], "T2")

    def test_fully_blocked_plan_has_diagnostic(self):
        self.plan("### T1 — Blocked\nBlocked by: T9 · Lane: logic\nStatus: todo\n")
        result = self.cli("--json")
        self.assertEqual((result.returncode, result.stdout), (1, ""))
        self.assertIn("no ready ticket", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_patch_cycle_comes_from_ticket_id(self):
        self.plan("### C2-T1 — Fix\nFixes: C1-1 (P1)\nLane: logic\nStatus: todo\n", "patch_plan.md")
        self.assertEqual(self.result()["why"], "Patch cycle 2 · fix C1-1")

    def test_invalid_slug_and_repository_have_diagnostics(self):
        with tempfile.TemporaryDirectory() as outside:
            for slug, args, diagnostic in [("../x", (), "slug must contain"),
                                           ("x", ("--repo", outside), "not inside a git repo")]:
                with self.subTest(slug=slug, args=args):
                    result = self.cli("--json", *args, slug=slug)
                    self.assertEqual((result.returncode, result.stdout), (1, ""))
                    self.assertIn(diagnostic, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_patch_ticket_without_fixes_fails_without_json(self):
        for fixes in ("", "C1-1 (P9)", "T1 (P1)", "C1-1 (P1) junk"):
            with self.subTest(fixes=fixes):
                self.plan(f"### C1-T1 — Fix\nFixes: {fixes}\nLane: logic\nStatus: todo\n", "patch_plan.md")
                result = self.cli("--json")
                self.assertEqual((result.returncode, result.stdout), (1, ""))
                self.assertIn("C1-T1", result.stderr)
                self.assertIn("Fixes: C<n>-<m> (P#)", result.stderr)

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

    def test_prior_cycle_finding_blocks_wrap_until_resolved(self):
        for resolved, phase in [("—", "review"), (f"@ {self.base}", "wrap")]:
            with self.subTest(resolved=resolved):
                self.review("### P1 — Old\n- Disposition: fix now\n"
                            f"- Resolved: {resolved}\n## Cycle 2 findings\n## Cycle 2 verdict\nship\n")
                result = self.result()
                self.assertEqual((result["phase"], result["command"]), (phase, f"workflow {phase} x"))
                self.assertEqual(result["blocker"]["findings"] if result["blocker"] else [],
                                 ["C1-1"] if phase == "review" else [])

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
        self.assertEqual((result.returncode, result.stdout), (1, ""))
        self.assertIn("review.md: unknown Base deadbeef", result.stderr)

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
        self.assertEqual(self.cli("--json").returncode, 1)

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
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn(diagnostic, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

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
