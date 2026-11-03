"""mutate.py's CLI contract on a scratch repo with one module and its test."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "mutate.py"
MODULE = "def big(x):\n    return x > 3\nsmall = lambda x: x < 2\n"
STRONG = ("import unittest\nfrom calc import big\n\n\nclass T(unittest.TestCase):\n"
          "    def test_big(self):\n        self.assertEqual((big(3), big(4)), (False, True))\n\n\nunittest.main()\n")
WEAK = STRONG.replace("(big(3), big(4)), (False, True)", "big(9), True")
# Untracked, two folders deep: the worktree must copy it in.
TEST = "PYTHONPATH=. python3 checks/unit/test_calc.py"


class MutateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")
        self.write("calc.py", "def big(x):\n    return x\nsmall = lambda x: x < 2\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.write("calc.py", MODULE)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, text=True)

    def write(self, name, text):
        (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
        (self.repo / name).write_text(text)

    def mutate(self, *args, base=None):
        return subprocess.run([sys.executable, str(SCRIPT), "--base", base or self.base, "--repo", str(self.repo),
                               *args], capture_output=True, text=True)

    def test_mutate_lists_changed_python_lines_only(self):
        self.write("tests/test_more.py", "assert 1 == 1\n")
        self.write("notes.md", "x > 3\n")
        self.write("query.sql", "select 1\n")
        self.write("new.py", "flag = all([len(''), True])\n")
        self.write("lib/deep.py", "on = True\n")
        self.write("lib2.py", "on = True\n")
        only = self.mutate("--list", "--path", "lib/", "--path", "calc.py")
        self.assertEqual(only.stdout.splitlines(), [
            "calc.py:2 Gt->GtE: (x >= 3)", "calc.py:2 3->4: (4)", "lib/deep.py:1 True->False: (False)"])
        (self.repo / "lib/deep.py").unlink()
        (self.repo / "lib2.py").unlink()
        result = self.mutate("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "not mutated: query.sql (not Python): invert one condition by hand (tests.md)",
            "calc.py:2 Gt->GtE: (x >= 3)", "calc.py:2 3->4: (4)", "new.py:1 all->any: (any([len(''), True]))",
            "new.py:1 True->False: (False)"])

    def test_mutate_reports_survivors_and_exit(self):
        for test, code, survivors in ((STRONG, 0, []), (WEAK, 1, ["survived calc.py:2 Gt->GtE: (x >= 3)",
                                                                  "survived calc.py:2 3->4: (4)"])):
            with self.subTest(code=code):
                self.write("checks/unit/test_calc.py", test)
                result = self.mutate("--jobs", "2", "--", TEST)
                self.assertEqual(result.returncode, code, result.stderr)
                lines = result.stdout.splitlines()
                self.assertEqual(lines[:-1], survivors)
                self.assertTrue(lines[-1].startswith(f"mutants 2 · killed {2 - len(survivors)} · "))
                self.assertEqual((self.repo / "calc.py").read_text(), MODULE)
                self.assertEqual(len(self.git("worktree", "list").stdout.splitlines()), 1)

    def test_mutate_counts_timeout_as_killed(self):
        self.write("calc.py", MODULE.replace("return x > 3", "while x:\n        pass\n    return x == 0"))
        self.write("checks/unit/test_calc.py", STRONG.replace("(big(3), big(4)), (False, True)", "big(0), True"))
        result = self.mutate("--timeout", "3", "--", TEST)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "mutants 3 · killed 3 · survived 0 · timed out 1 (counted killed)\n")

    def test_mutate_stopped_removes_worktrees(self):
        proc = subprocess.Popen([sys.executable, str(SCRIPT), "--base", self.base, "--repo", str(self.repo), "--jobs", "2",
                                 "--", "sleep 1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 20
        while len(self.git("worktree", "list").stdout.splitlines()) < 3 and time.monotonic() < deadline:
            time.sleep(0.05)
        proc.terminate()
        proc.communicate(timeout=30)
        self.assertEqual(proc.returncode, 143)
        self.assertEqual(len(self.git("worktree", "list").stdout.splitlines()), 1)

    def test_mutate_setup_errors_exit_2(self):
        cases = (("bad base", ["--", TEST], "nope", MODULE, "nope"),
                 ("no command", [], None, MODULE, "give the test command after --"),
                 ("red baseline", ["--", "false"], None, MODULE, "fails before any mutation"),
                 ("syntax error", ["--", TEST], None, "def big(x):\n    return x >\n", "calc.py:2: invalid syntax"))
        for name, args, base, module, message in cases:
            with self.subTest(name):
                self.write("calc.py", module)
                result = self.mutate(*args, base=base)
                self.assertEqual((result.returncode, result.stdout), (2, ""))
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
