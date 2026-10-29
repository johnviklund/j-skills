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
## Phase → seat · effort · approval
| Key | Phase / work | Seat | Effort | Context | Approval | Notes |
|---|---|---|---|---|---|---|
| plan | Plan | Strict reviewer | high | large | human | |
| execute:contract | Execute contract | Heavy executor | xhigh | standard | auto | |
| execute:logic | Execute logic | Default executor | high | standard | auto | |
| execute:operator | Execute operator | Default executor | high | standard | human | |
| fix:P0 | Fix P0 | Heavy executor | high | standard | auto | |
| fix:logic | Fix logic | Default executor | medium | standard | auto | |
| fix:mechanical | Fix mechanical | Mechanical lane | medium | standard | auto | |
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
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "handoff")
        result = self.result()
        self.assertEqual(result["blocker"]["ticket"], "T3")
        self.assertIn("receipts/t3-operator-handoff.md", result["blocker"]["action"])
        self.assertIn("Run the probe", result["blocker"]["action"])
        self.assertIn(".workflow/x/receipts/t3-operator-handoff.md", result["reads"])
        self.assertIsNone(result["model"])
        self.assertEqual(result["command"], "workflow execute x")
        self.assertIn("- **Model:** human · ", result["card"])
        (receipts / "t3.txt").write_text("ok\n")
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

    def test_patch_ticket_without_fixes_fails_without_json(self):
        for fixes in ("", "C1-1 (P9)", "T1 (P1)", "C1-1 (P1) junk"):
            with self.subTest(fixes=fixes):
                self.plan(f"### C1-T1 — Fix\nFixes: {fixes}\nLane: logic\nStatus: todo\n", "patch_plan.md")
                result = self.cli("--json")
                self.assertEqual((result.returncode, result.stdout), (1, ""))
                self.assertIn("C1-T1", result.stderr)
                self.assertIn("Fixes: C<n>-<m> (P#)", result.stderr)

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
