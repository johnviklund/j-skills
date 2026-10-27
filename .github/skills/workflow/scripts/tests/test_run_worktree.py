"""Run-worktree commands exercised against real repositories and a bare origin."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "run-worktree.py"


class RepoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.write("src.py", "base\n")
        self.commit("base")
        self.remote = self.root / "origin.git"
        self.git("clone", "-q", "--bare", str(self.repo), str(self.remote))
        self.git("remote", "add", "origin", str(self.remote))
        self.git("fetch", "-q", "origin")
        self.git("remote", "set-head", "origin", "main")

    def git(self, *args, repo=None, check=True):
        return subprocess.run(["git", "-C", str(repo or self.repo), *args],
                              capture_output=True, text=True, check=check)

    def write(self, path, text, repo=None):
        target = (repo or self.repo) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, message, repo=None):
        self.git("add", "-A", repo=repo)
        self.git("commit", "-qm", message, repo=repo)
        return self.git("rev-parse", "HEAD", repo=repo).stdout.strip()

    def run_command(self, command, slug="B", repo=None):
        return subprocess.run([sys.executable, str(SCRIPT), command, slug,
                               "--repo", str(repo or self.repo)], capture_output=True, text=True)

    def started(self, slug="A", status="complete"):
        self.write(Path(".workflow") / slug / "brainstorm.md", f"Command: brainstorm\nCreated: now\nBase: x\nInputs: none\nStatus:  {status}\n")
        self.write(Path(".workflow") / slug / "plan.md", "### T1 — ticket\nStatus: done @ abc1234\n")
        return self.commit("started run")


class OpenTests(RepoTests):
    def test_Open_isolates_a_second_run(self):
        base = self.started()
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".worktrees/B")
        tree = self.repo / ".worktrees/B"
        self.assertEqual(self.git("branch", "--show-current", repo=tree).stdout.strip(), "run/B")
        self.assertEqual(self.git("rev-parse", "HEAD", repo=tree).stdout.strip(), base)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")
        self.assertIn("no ## Worktree setup in AGENTS.md", result.stderr)

    def test_Open_keeps_a_free_primary_checkout(self):
        for state in ("clean", "isolated", "done"):
            with self.subTest(state=state):
                if state == "isolated":
                    self.started()
                    self.git("worktree", "add", "-qb", "run/A", ".worktrees/A")
                    self.write(".git/info/exclude", ".worktrees/\n")
                elif state == "done":
                    self.started(status="done")
                    self.git("worktree", "remove", ".worktrees/A")
                before = self.git("worktree", "list").stdout
                result = self.run_command("open")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), ".")
                self.assertEqual(self.git("worktree", "list").stdout, before)

    def test_Open_preserves_dirty_files_and_excludes_once(self):
        self.write("src.py", "uncommitted\n")
        before = self.git("status", "--porcelain").stdout
        for _ in range(2):
            result = self.run_command("open")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), ".worktrees/B")
        self.assertEqual((self.repo / "src.py").read_text(), "uncommitted\n")
        self.assertEqual(self.git("status", "--porcelain").stdout, before)
        self.assertEqual((self.repo / ".git/info/exclude").read_text().splitlines().count(".worktrees/"), 1)

    def test_Open_runs_only_committed_primary_setup(self):
        self.write("AGENTS.md", "## Worktree setup\n```sh\ntouch ready\n```\n## Other\nfalse\n")
        self.commit("setup")
        self.write("AGENTS.md", "## Worktree setup\ntouch untrusted\n")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("touch ready", result.stderr)
        self.assertTrue((self.repo / ".worktrees/B/ready").exists())
        self.assertFalse((self.repo / ".worktrees/B/untrusted").exists())


class WhereTests(RepoTests):
    def test_Where_finds_an_existing_worktree(self):
        self.assertEqual(self.run_command("where").stdout.strip(), ".")
        self.started()
        self.assertEqual(self.run_command("open").returncode, 0)
        result = self.run_command("where")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".worktrees/B")

    def test_Where_recovers_and_fast_forwards_another_clone(self):
        self.started()
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        tree = self.repo / ".worktrees/B"
        self.write("ticket.py", "ticket\n", repo=tree)
        first = self.commit("ticket", repo=tree)
        self.git("push", "-qu", "origin", "run/B", repo=tree)
        clone = self.root / "clone"
        self.git("clone", "-q", str(self.remote), str(clone))
        for expected in (first, "advanced"):
            if expected == "advanced":
                self.write("ticket.py", "advanced\n", repo=tree)
                expected = self.commit("advance", repo=tree)
                self.git("push", "-q", "origin", "run/B", repo=tree)
            result = self.run_command("where", repo=clone)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), ".worktrees/B")
            self.assertEqual(self.git("rev-parse", "HEAD", repo=clone / ".worktrees/B").stdout.strip(), expected)
        self.assertEqual(self.git("status", "--porcelain", repo=clone).stdout, "")
