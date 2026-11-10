import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]


class Seats(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / ".jflow").mkdir()
        self.env = dict(os.environ, JFLOW_CONFIG="")

    def run_cli(self, *args, ok=True):
        out = subprocess.run([sys.executable, str(SKILL / "scripts/jflow.py"), *args,
                              "--repo", str(self.repo)], env=self.env, capture_output=True, text=True)
        self.assertEqual(out.returncode == 0, ok, out.stderr)
        if not ok:
            self.assertEqual(out.stdout, "")
            self.assertEqual(len(out.stderr.splitlines()), 1)
        return out

    def config(self, name, **data):
        path = self.repo / name
        path.write_text(json.dumps(dict(schema_version=1, **data)))
        return str(path)

    def test_defaults_and_flow(self):
        flow = json.loads((SKILL / "flow.json").read_text())["steps"]
        for step, meta in flow.items():
            with self.subTest(step=step):
                seat = json.loads(self.run_cli("seat", step).stdout)
                expected = ("gpt-6.1-sol", "high") if step == "check" else ("claude-opus-5-5", "medium")
                self.assertEqual((seat["model"], seat["effort"]), expected)
                self.assertEqual(seat["fallback"]["model"] if seat["fallback"] else None,
                                 "gpt-6-astra" if step == "check" else None)
                self.assertEqual({k: seat[k] for k in meta}, meta)
        self.run_cli("seat", "bogus", ok=False)

    def test_layers_and_vendor_rule(self):
        defaults = json.loads((SKILL / "config.json").read_text())
        sol = defaults["seats"]["check"]
        self.config(".jflow/config.json", seats={"build": sol})
        self.assertEqual(json.loads(self.run_cli("seat", "check").stdout)["model"], "claude-opus-5-5")
        self.config(".jflow/config.json", seats={"build": sol}, different_vendors=False)
        self.assertEqual(json.loads(self.run_cli("seat", "check").stdout)["model"], sol["model"])
        self.assertEqual(json.loads(self.run_cli("seat", "build").stdout)["model"], sol["model"])
        astra = sol["fallback"]
        self.env["JFLOW_CONFIG"] = self.config("env.json", seats={"check": astra})
        self.assertEqual(json.loads(self.run_cli("seat", "check").stdout)["model"], astra["model"])
        flag = self.config("flag.json", seats={"check": sol})
        self.assertEqual(json.loads(self.run_cli("seat", "check", "--config", flag).stdout)["model"], sol["model"])
        self.assertEqual(json.loads(self.run_cli("seat", "spec").stdout)["model"], "claude-opus-5-5")

    def test_bad_config_and_locked_rules(self):
        path = self.repo / ".jflow/config.json"
        for value in ("{", '{"schema_version":1,"seats":{"build":{"model":"m","vendor":"v","effort":5,"fallback":null}}}'):
            path.write_text(value)
            self.assertIn(str(path), self.run_cli("seat", "build", ok=False).stderr)
        path.unlink()
        rules = json.loads(self.run_cli("seat", "build").stdout)["rules"]
        self.assertEqual(set(rules), {"public_paid_needs_human", "checker_read_only", "no_secrets"})
        for rule in rules:
            self.config(".jflow/config.json", rules={rule: False})
            self.assertIn(rule, self.run_cli("seat", "build", ok=False).stderr)

    def test_secret_values_never_reach_output_or_record(self):
        run = self.repo / ".jflow/demo"
        run.mkdir()
        (run / "spec.md").write_text("Status: ready\n")
        log = run / "run.jsonl"
        log.write_text("unchanged\n")
        for value in ("sk-ant-" + "a" * 20, "sk-" + "a" * 20, "sk-" + "a" * 10 + "-" + "1" * 10,
                      "ghp_" + "b" * 20, "AKIA" + "C" * 16,
                      "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7cF0iL3oR6uX9z"):
            self.config(".jflow/config.json", seats={"build": dict(model=value, vendor="v", effort="high", fallback=None)})
            for args in (("seat", "build"), ("record", "demo", "spec", "--model", value, "--effort", "high"),
                         ("record", "demo", "spec", "--model", "m", "--effort", value)):
                self.assertNotIn(value, self.run_cli(*args, ok=False).stderr)
            self.assertEqual(log.read_text(), "unchanged\n")
