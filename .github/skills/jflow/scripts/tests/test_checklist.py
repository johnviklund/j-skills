import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "jflow.py"

ITEMS = """# Reliability

- [ ] Net code keeps timeouts
  Paths: src/net/**/*.py
  Check: every request passes timeout=
  Incident: https://example.com/inc/1
- [ ] Retries stay bounded
  Match: \\bretry\\(
  Check: retry has max attempts
  Incident: #12
- [ ] Docs links
  Paths: docs/*.md
  Check: links resolve
  Incident: #3
- [ ] Cache keys carry the tenant
  Paths: cache/*.py
  Match: cache_key
  Check: every cache_key call passes tenant=
  Incident: org/repo#7
"""


class Checklist(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.base = self.commit("base", {})

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, msg, files):
        for name, text in files.items():
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def checklist(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "checklist", *args, "--repo", str(self.repo)],
                              capture_output=True, text=True)

    def test_row_1_prints_only_items_the_diff_triggers(self):
        base = self.commit("items", {"RELIABILITY.md": ITEMS})
        self.commit("change", {"src/net/deep/a.py": "x = retry(3)\n", "README": "hi\n"})
        r = self.checklist("--base", base)
        self.assertEqual(r.returncode, 0, r.stderr)
        for want in ("Net code keeps timeouts", "every request passes timeout=", "https://example.com/inc/1",
                     "Retries stay bounded", "retry has max attempts", "#12", "2 of 4"):
            self.assertIn(want, r.stdout)
        self.assertNotIn("Docs links", r.stdout)
        self.assertNotIn("Cache keys", r.stdout)

    def test_row_1_a_removed_line_triggers_match(self):
        self.commit("old", {"lib.py": "retry(1)\n"})
        base = self.commit("items", {"RELIABILITY.md": ITEMS})
        self.commit("drop", {"lib.py": "pass\n"})
        self.assertIn("Retries stay bounded", self.checklist("--base", base).stdout)

    def test_row_2_no_file_exits_clean(self):
        self.commit("change", {"a.py": "retry(1)\n"})
        r = self.checklist("--base", self.base)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertNotIn("- [ ]", r.stdout)

    def test_row_3_paths_and_match_must_hit_the_same_file(self):
        base = self.commit("items", {"RELIABILITY.md": ITEMS})
        self.commit("apart", {"cache/a.py": "x = 1\n", "other/b.py": "cache_key()\n"})
        self.assertNotIn("Cache keys", self.checklist("--base", base).stdout)
        self.commit("together", {"cache/a.py": "cache_key(tenant=t)\n"})
        self.assertIn("Cache keys", self.checklist("--base", base).stdout)

    def test_row_4_malformed_items_fail_naming_the_item(self):
        cases = {
            "no trigger": "- [ ] Lonely\n  Check: c\n  Incident: #1\n",
            "no incident": "- [ ] Unlinked\n  Paths: *.py\n  Check: c\n",
            "bad regex": "- [ ] Broken\n  Match: (\n  Check: c\n  Incident: #1\n",
        }
        for name, text in cases.items():
            with self.subTest(name):
                (self.repo / "RELIABILITY.md").write_text(text)
                r = self.checklist("--base", self.base)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(text.split("\n")[0][6:], r.stderr)
                self.assertIn("RELIABILITY.md:1", r.stderr)

    def test_row_5_slug_reads_base_from_the_spec(self):
        base = self.commit("items", {"RELIABILITY.md": ITEMS})
        self.commit("change", {"docs/x.md": "y\n"})
        (self.repo / ".jflow/demo").mkdir(parents=True)
        (self.repo / ".jflow/demo/spec.md").write_text(f"# demo\nStatus: ready\nBase: {base}\n")
        r = self.checklist("demo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Docs links", r.stdout)
        self.assertIn("1 of 4", r.stdout)

    def test_fix_1_glob_character_class_matches(self):
        base = self.commit("items", {"RELIABILITY.md": "- [ ] C sources\n  Paths: src/*.[ch]\n  Check: c\n  Incident: #1\n"})
        self.commit("change", {"src/store.c": "int x;\n"})
        self.assertIn("1 of 1", self.checklist("--base", base).stdout)

    def test_fix_2_changed_lines_that_look_like_headers_still_match(self):
        self.commit("old", {"counter.cpp": "-- remaining;\n"})
        base = self.commit("items", {"RELIABILITY.md":
                                     "- [ ] Counter\n  Paths: counter.cpp\n  Match: remaining\n  Check: c\n  Incident: #1\n"})
        self.commit("change", {"counter.cpp": "++ remaining;\n"})
        self.assertIn("1 of 1", self.checklist("--base", base).stdout)

    def test_fix_3_plus_bullet_item_is_validated(self):
        (self.repo / "RELIABILITY.md").write_text("+ [ ] Missing check\n  Paths: *.py\n  Incident: #1\n")
        r = self.checklist("--base", self.base)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Missing check", r.stderr)


if __name__ == "__main__":
    unittest.main()
