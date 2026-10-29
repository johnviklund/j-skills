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
## Phase → seat · effort · approval
| Key | Phase / work | Seat | Effort | Context | Approval | Notes |
|---|---|---|---|---|---|---|
| plan | Plan | Strict reviewer | high | large | human | |
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
