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
        return subprocess.run([sys.executable, str(SCRIPT), command,
                               *([slug] if slug else []), "--repo", str(repo or self.repo)], capture_output=True, text=True)

    def started(self, slug="A", status="complete"):
        self.write(Path(".workflow") / slug / "brainstorm.md", f"Command: brainstorm\nCreated: now\nBase: x\nInputs: none\nStatus:  {status}\n")
        self.write(Path(".workflow") / slug / "plan.md", "### T1 — ticket\nStatus: done @ abc1234\n")
        return self.commit("started run")


class OpenTests(RepoTests):
    def test_Open_keeps_primary_free_for_an_unstarted_run(self):
        self.started("A")
        self.write(".workflow/A/plan.md", "### T1 — ticket\nStatus: todo\n")
        self.commit("planned only")
        before = self.git("worktree", "list").stdout
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".")
        self.assertEqual(self.git("worktree", "list").stdout, before)

    def test_Open_excludes_multiple_isolated_runs_once(self):
        self.started()
        for slug in ("B", "C"):
            result = self.run_command("open", slug)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), f".worktrees/{slug}")
        self.assertEqual((self.repo / ".git/info/exclude").read_text().splitlines().count(".worktrees/"), 1)

    def test_Open_keeps_started_run_with_its_uncommitted_work(self):
        for name in ("plan.md", "patch_plan.md"):
            for started in (False, True):
                with self.subTest(name=name, started=started):
                    self.setUp()
                    self.write(f".workflow/B/{name}", "### T1 — ticket\nStatus: " + ("done @ abc1234" if started else "todo") + "\n### T2 — ticket\nStatus: todo\n")
                    self.commit("own run")
                    dirty = "t2.py" if started else "src.py"
                    self.write(dirty, "unfinished\n")
                    before = self.git("worktree", "list").stdout
                    result = self.run_command("open")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), "." if started else ".worktrees/B")
                    if started:
                        self.assertEqual(self.git("worktree", "list").stdout, before)
                    self.assertEqual((self.repo / dirty).read_text(), "unfinished\n")

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

    def test_Open_setup_keeps_shell_comments_inside_fences(self):
        self.write("AGENTS.md", "## Worktree setup\n```sh\n# install deps\ntouch ready\n```\n## Other\nfalse\n")
        self.commit("commented setup")
        self.write("src.py", "uncommitted\n")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("touch ready", result.stderr)
        self.assertTrue((self.repo / ".worktrees/B/ready").exists())


class WhereTests(RepoTests):
    def test_Where_uses_local_refs_when_origin_is_unreachable(self):
        for isolated in (False, True):
            with self.subTest(isolated=isolated):
                self.setUp()
                if isolated:
                    self.started()
                    self.assertEqual(self.run_command("open").returncode, 0)
                self.git("remote", "set-url", "origin", str(self.root / "missing.git"))
                result = self.run_command("where")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), ".worktrees/B" if isolated else ".")
                self.assertIn("could not fetch origin:", result.stderr)
                self.assertIn("using local refs", result.stderr)

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


class LandTests(RepoTests):
    def test_Land_routes_mixed_and_text_only_conflicts(self):
        for paths, expected in ((("src.py", "WORKLOG.md"), 3), (("notes.txt",), 4)):
            with self.subTest(paths=paths):
                self.setUp()
                tree, _, _ = self.run_branch(paths[0])
                for path in paths[1:]:
                    self.write(path, "run change\n", repo=tree)
                if len(paths) > 1:
                    self.commit("extra conflict", repo=tree)
                for path in paths:
                    self.write(path, "primary change\n")
                primary = self.commit("primary conflicts")
                result = self.run_command("land")
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertEqual(self.git("rev-parse", "main").stdout.strip(), primary)
                self.assertEqual(set(self.git("diff", "--name-only", "--diff-filter=U", repo=tree).stdout.splitlines()), set(paths))

    def test_Land_refuses_dirty_or_wrong_branch_checkouts(self):
        for state in ("dirty run", "primary branch", "run branch"):
            with self.subTest(state=state):
                self.setUp()
                tree, _, _ = self.run_branch()
                primary = self.git("rev-parse", "main").stdout
                if state == "dirty run":
                    self.write("unfinished.py", "unfinished\n", repo=tree)
                elif state == "primary branch":
                    self.git("checkout", "-qb", "feature")
                else:
                    self.git("checkout", "-qb", "feature", repo=tree)
                result = self.run_command("land")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(self.git("rev-parse", "main").stdout, primary)

    def run_branch(self, path="src.py"):
        self.started()
        self.git("push", "-q", "origin", "main")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        tree = self.repo / ".worktrees/B"
        self.write(path, "run change\n", repo=tree)
        ticket = self.commit("run ticket", repo=tree)
        self.write(Path(".workflow") / "B/plan.md", f"### T1 — ticket\nStatus: done @ {ticket}\n", repo=tree)
        tip = self.commit("run state", repo=tree)
        self.git("push", "-qu", "origin", "run/B", repo=tree)
        return tree, ticket, tip

    def test_Land_preserves_history_and_cleans_up(self):
        for shape in ("fast-forward", "merge"):
            with self.subTest(shape=shape):
                if shape == "merge":
                    self.setUp()
                tree, ticket, tip = self.run_branch()
                if shape == "merge":
                    self.write("other.py", "primary change\n")
                    self.commit("primary advance")
                    self.git("push", "-q", "origin", "main")
                result = self.run_command("land")
                self.assertEqual(result.returncode, 0, result.stderr)
                head = self.git("rev-parse", "HEAD").stdout.strip()
                if shape == "fast-forward":
                    self.assertEqual(head, tip)
                else:
                    self.assertEqual(len(self.git("rev-list", "--parents", "-n1", "HEAD").stdout.split()), 3)
                self.assertEqual(self.git("merge-base", "--is-ancestor", ticket, "HEAD", check=False).returncode, 0)
                self.assertEqual(self.git("rev-parse", "refs/heads/main", repo=self.remote).stdout.strip(), head)
                self.assertFalse(tree.exists())
                self.assertEqual(self.git("branch", "--list", "run/B").stdout, "")
                self.assertEqual(self.git("ls-remote", "--heads", "origin", "run/B").stdout, "")

    def test_Land_leaves_conflicts_only_in_the_run_worktree(self):
        for path, expected in (("src.py", 3), ("WORKLOG.md", 4)):
            with self.subTest(path=path):
                if path == "WORKLOG.md":
                    self.setUp()
                    self.write(path, "base log\n")
                    self.commit("base log")
                tree, _, _ = self.run_branch(path)
                self.write(path, "primary change\n")
                primary = self.commit("primary conflict")
                self.write("unrelated.py", "uncommitted\n")
                dirty = self.git("status", "--porcelain").stdout
                result = self.run_command("land")
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), primary)
                self.assertEqual(self.git("status", "--porcelain").stdout, dirty)
                self.assertEqual(self.git("rev-parse", "MERGE_HEAD", repo=tree).stdout.strip(), primary)
                self.assertEqual(self.git("diff", "--name-only", "--diff-filter=U", repo=tree).stdout.strip(), path)
                self.assertNotEqual(self.git("rev-parse", "--verify", "MERGE_HEAD", check=False).returncode, 0)
                if expected == 3:
                    self.assertIn("workflow review B", result.stderr)
                else:
                    self.assertIn("keeping both sides", result.stderr)
                    self.assertIn("commit", result.stderr)
                    self.assertIn("land again", result.stderr)
                (self.repo / "unrelated.py").unlink()

    def test_Land_preserves_overlapping_uncommitted_work(self):
        self.run_branch()
        primary = self.git("rev-parse", "HEAD").stdout.strip()
        self.write("src.py", "uncommitted\n")
        result = self.run_command("land")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("src.py", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), primary)
        self.assertEqual((self.repo / "src.py").read_text(), "uncommitted\n")

    def test_Land_refuses_unpushed_primary_commits(self):
        tree, _, _ = self.run_branch()
        self.write("other.py", "unscanned primary change\n")
        primary = self.commit("unscanned primary")
        remote = self.git("rev-parse", "refs/heads/main", repo=self.remote).stdout
        run = self.git("rev-parse", "HEAD", repo=tree).stdout
        result = self.run_command("land")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(primary[:7], result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), primary)
        self.assertEqual(self.git("rev-parse", "refs/heads/main", repo=self.remote).stdout, remote)
        self.assertTrue(tree.exists())
        self.assertEqual(self.git("rev-parse", "HEAD", repo=tree).stdout, run)


class CheckoutTests(RepoTests):
    def test_Checkout_warnings_exempt_only_the_matching_run_checkout(self):
        for path, branch, expected in ((".worktrees/x", "run/x", (False, False)),
                                      (".worktrees/x", "feature", (True, True)),
                                      ("outside/x", "run/x", (True, True)),
                                      (".worktrees/y", "run/x", (True, True)),
                                      (".", "feature", (False, True))):
            with self.subTest(path=path, branch=branch):
                self.setUp()
                header = "Command: fixture\nCreated: 2026-10-27 · Test\nBase: " + self.git("rev-parse", "HEAD").stdout.strip() + "\nInputs: none\nStatus: complete\n"
                self.write(Path(".workflow") / "x/brainstorm.md", header)
                self.write(Path(".workflow") / "x/plan.md", header + "## Checklist\n- fixture\n")
                self.commit("checkout fixture")
                if path == ".":
                    self.git("checkout", "-qb", branch)
                else:
                    self.git("worktree", "add", "-qb", branch, path)
                result = subprocess.run([sys.executable, str(SCRIPT.with_name("check-run.py")),
                                         "x", "--repo", str(self.repo / path)], capture_output=True, text=True)
                self.assertEqual(("linked worktree" in result.stdout, "on branch" in result.stdout), expected, result.stdout)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("== x", result.stdout)


class DoctorTests(RepoTests):
    def test_Doctor_reports_missing_setup_from_committed_primary(self):
        for setup, expected in ((False, 1), (True, 0)):
            with self.subTest(setup=setup):
                self.setUp()
                self.started("B")
                if setup:
                    self.write("AGENTS.md", "## Worktree setup\ntrue\n")
                    self.commit("setup")
                self.git("worktree", "add", "-qb", "run/B", ".worktrees/B")
                self.write("AGENTS.md", "## Worktree setup\ntrue\n" if not setup else "uncommitted removal\n")
                result = self.run_command("doctor", slug=None)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.count("## Worktree setup"), expected, result.stdout)
                self.assertEqual(len(result.stdout.splitlines()), expected, result.stdout)

    def test_Doctor_reports_orphan_worktrees(self):
        for status, expected in ((None, 1), ("done", 1), ("parked", 1), ("complete", 0), ("drafting", 0)):
            with self.subTest(status=status):
                self.setUp()
                self.write("AGENTS.md", "## Worktree setup\ntrue\n")
                if status:
                    self.started("old", status=status)
                else:
                    self.commit("setup")
                self.git("worktree", "add", "-qb", "run/old", ".worktrees/old")
                result = self.run_command("doctor", slug=None)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.count(".worktrees/old"), expected, result.stdout)
                self.assertEqual(len(result.stdout.splitlines()), expected, result.stdout)
