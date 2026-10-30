"""Run-worktree commands exercised against real repositories and a bare origin."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
        for state in ("clean", "isolated", "done", "parked", "missing status"):
            with self.subTest(state=state):
                if state == "isolated":
                    self.started()
                    self.git("worktree", "add", "-qb", "run/A", ".worktrees/A")
                    self.write(".git/info/exclude", ".worktrees/\n")
                elif state == "done":
                    self.started(status="done")
                    self.git("worktree", "remove", ".worktrees/A")
                elif state in ("parked", "missing status"):
                    self.started(status="parked" if state == "parked" else "complete")
                    if state == "missing status":
                        self.write(".workflow/A/plan.md", "### T1 — ticket\n")
                        self.commit("missing ticket status")
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

    def test_Open_keeps_dirty_checkout_busy_with_an_unstarted_run(self):
        self.started()
        self.write(".workflow/A/plan.md", "### T1 — ticket\nStatus: todo\n")
        self.commit("unstarted run")
        self.write("src.py", "uncommitted\n")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".worktrees/B")

    def test_Open_resumes_first_ticket_with_an_execute_decision(self):
        for phase in ("execute", "plan"):
            with self.subTest(phase=phase):
                self.setUp()
                self.write(".workflow/B/plan.md", "### T1 — ticket\nStatus: todo\n")
                self.write(".workflow/B/decisions.md",
                           "| ID | Phase | Question | Default | Status | Answer |\n"
                           "|---|---|---|---|---|---|\n"
                           f"| D1 | {phase} | Approve T1? | commit | answered | commit |\n")
                self.commit("first ticket decision")
                self.write("src.py", "pending UI code\n")
                before = self.git("worktree", "list").stdout
                result = self.run_command("open")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "." if phase == "execute" else ".worktrees/B")
                if phase == "execute":
                    self.assertEqual(self.git("worktree", "list").stdout, before)
                self.assertEqual((self.repo / "src.py").read_text(), "pending UI code\n")

    def test_Open_stops_when_setup_fails(self):
        self.write("AGENTS.md", "## Worktree setup\n```sh\nfalse\ntouch ready\n```\n")
        self.commit("failing setup")
        self.write("src.py", "uncommitted\n")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue((self.repo / ".worktrees/B").exists())
        self.assertFalse((self.repo / ".worktrees/B/ready").exists())

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

    def test_Open_setup_stops_at_top_level_heading(self):
        self.write("AGENTS.md", "## Worktree setup\n```sh\ntouch ready\n```\n# Appendix\n```sh\ntouch appendix_ran\n```\n")
        self.commit("setup and appendix")
        self.write("src.py", "uncommitted\n")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.repo / ".worktrees/B/ready").exists())
        self.assertFalse((self.repo / ".worktrees/B/appendix_ran").exists())
        self.assertNotIn("appendix_ran", result.stderr)

    def test_Open_setup_validates_shell_fence_before_creating_checkout(self):
        for tag, expected in (("zsh", 1), ("sh ", 0)):
            with self.subTest(tag=tag):
                self.setUp()
                self.write("AGENTS.md", f"## Worktree setup\n```{tag}\ntouch ready\n```\n")
                self.commit("setup fence")
                self.write("src.py", "uncommitted\n")
                result = self.run_command("open")
                self.assertEqual(result.returncode, expected, result.stderr)
                if expected:
                    self.assertIn("## Worktree setup", result.stderr)
                    self.assertIn("sh", result.stderr)
                    self.assertFalse((self.repo / ".worktrees/B").exists())
                    self.assertNotEqual(self.git("rev-parse", "--verify", "refs/heads/run/B", check=False).returncode, 0)
                else:
                    self.assertTrue((self.repo / ".worktrees/B/ready").exists())


    def test_Open_setup_reads_shell_fences_line_by_line(self):
        cases = (
            ("# install deps\ntouch ready\n", 1),
            ("```zsh\ntouch zsh_ran\n```\n\n```sh\ntouch ready\n```\n", 0),
            ("```console\n$ make\n```\nThen run:\n```sh\ntouch ready\n```\n", 0),
            ('```bash title="setup"\ntouch ready\n```\n', 0),
            ("```sh\ntouch ready\n```\nThen run the app.\n", 0),
            ("```\ntouch ready\n```\n", 0),
            ("1. Install:\n   ```sh\n   touch ready\n   ```\n", 0),
            ("```shell\ntouch ready\n```\n", 0),
            ("```sh\ntouch ready\n```\n```text\nok\n```\n", 0),
        )
        for body, expected in cases:
            with self.subTest(body=body):
                self.setUp()
                self.write("AGENTS.md", "## Worktree setup\n" + body)
                self.commit("setup fence shapes")
                self.write("src.py", "uncommitted\n")
                result = self.run_command("open")
                self.assertEqual(result.returncode, expected, result.stderr)
                if expected:
                    self.assertIn("## Worktree setup", result.stderr)
                    self.assertIn("fence", result.stderr)
                    self.assertFalse((self.repo / ".worktrees/B").exists())
                    self.assertNotEqual(self.git("rev-parse", "--verify", "refs/heads/run/B", check=False).returncode, 0)
                else:
                    self.assertTrue((self.repo / ".worktrees/B/ready").exists())
                    self.assertFalse((self.repo / ".worktrees/B/zsh_ran").exists())
                    self.assertNotIn("Then run:", result.stderr)


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

    def test_Where_recovers_an_unpushed_local_branch(self):
        self.started()
        self.assertEqual(self.run_command("open").returncode, 0)
        tip = self.git("rev-parse", "run/B").stdout
        self.git("worktree", "remove", ".worktrees/B")
        result = self.run_command("where")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".worktrees/B")
        self.assertEqual(self.git("rev-parse", "HEAD", repo=self.repo / ".worktrees/B").stdout, tip)

    def test_Where_without_origin_uses_the_primary_checkout(self):
        self.git("remote", "remove", "origin")
        result = self.run_command("where")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".")
        self.assertNotIn("could not fetch", result.stderr)

    def test_Where_checks_slugs_and_primary_fallback(self):
        for command, slug, code, error in (("open", "a/b", 2, "slug must contain only"),
                                            ("open", None, 2, "a run slug is required"),
                                            ("where", "a..b", 1, "not a valid branch name")):
            with self.subTest(command=command, slug=slug):
                result = self.run_command(command, slug)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertIn(error, result.stderr)
        self.git("remote", "set-head", "origin", "-d")
        result = self.run_command("where")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git("branch", "-m", "trunk")
        result = self.run_command("where")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("no primary branch found", result.stderr)

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

    def test_Where_skips_a_run_landed_from_another_clone(self):
        self.started()
        self.assertEqual(self.run_command("open").returncode, 0)
        tree = self.repo / ".worktrees/B"
        self.write(".workflow/B/brainstorm.md", "Command: brainstorm\nCreated: now\nBase: x\nInputs: none\nStatus: complete\n", repo=tree)
        self.commit("brief", repo=tree)
        self.git("push", "-qu", "origin", "run/B", repo=tree)
        clone = self.root / "clone"
        self.git("clone", "-q", str(self.remote), str(clone))
        self.assertEqual(self.run_command("where", repo=clone).stdout.strip(), ".worktrees/B")
        self.git("push", "-q", "origin", "main")
        self.assertEqual(self.run_command("land").returncode, 0)
        self.write(".workflow/B/brainstorm.md", "Command: brainstorm\nCreated: now\nBase: x\nInputs: none\nStatus: done\n")
        self.commit("archive B")
        self.git("push", "-q", "origin", "main")
        for state in ("stale folder", "branch only"):
            with self.subTest(state=state):
                if state == "branch only":
                    self.git("worktree", "remove", str(clone / ".worktrees/B"), repo=clone)
                result = self.run_command("where", repo=clone)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), ".")
                self.assertIn("landed", result.stderr)
                self.assertEqual((clone / ".worktrees/B").exists(), state == "stale folder")
                if state == "stale folder":
                    self.assertIn(".worktrees/B has no live run", self.run_command("doctor", slug=None, repo=clone).stdout)


class LandTests(RepoTests):
    def test_Land_routes_mixed_and_text_only_conflicts(self):
        for paths, expected in ((("src.py", "WORKLOG.md"), 3), (("skills/x/SKILL.md",), 3), (("notes.txt",), 3),
                                ((".workflow/B/scripts/x.py",), 3),
                                (("WORKLOG.md", "TODO.md", "TODO_ARCHIVE.md", ".workflow/B/receipts/r.md"), 4)):
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

    def run_branch(self, path="src.py", push=True):
        self.started()
        self.git("push", "-q", "origin", "main")
        result = self.run_command("open")
        self.assertEqual(result.returncode, 0, result.stderr)
        tree = self.repo / ".worktrees/B"
        self.write(path, "run change\n", repo=tree)
        ticket = self.commit("run ticket", repo=tree)
        self.write(Path(".workflow") / "B/plan.md", f"### T1 — ticket\nStatus: done @ {ticket}\n", repo=tree)
        tip = self.commit("run state", repo=tree)
        if push:
            self.git("push", "-qu", "origin", "run/B", repo=tree)
        return tree, ticket, tip

    def test_Land_preserves_history_and_cleans_up(self):
        for shape in ("fast-forward", "merge", "never pushed"):
            with self.subTest(shape=shape):
                if shape != "fast-forward":
                    self.setUp()
                tree, ticket, tip = self.run_branch(push=shape != "never pushed")
                if shape == "merge":
                    self.write("other.py", "primary change\n")
                    self.commit("primary advance")
                    self.git("push", "-q", "origin", "main")
                result = self.run_command("land")
                if shape == "merge":
                    moved = self.git("rev-parse", "main").stdout.strip()
                    self.assertEqual(result.returncode, 5, result.stdout + result.stderr)
                    self.assertIn("full suite", result.stderr)
                    self.assertEqual(self.git("rev-parse", "main").stdout.strip(), moved)
                    self.assertEqual(self.git("rev-parse", "HEAD^2", repo=tree).stdout.strip(), moved)
                    self.assertNotEqual(self.git("rev-parse", "--verify", "MERGE_HEAD", repo=tree, check=False).returncode, 0)
                    result = self.run_command("land")
                self.assertEqual(result.returncode, 0, result.stderr)
                head = self.git("rev-parse", "HEAD").stdout.strip()
                if shape != "merge":
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

    def test_Land_requires_a_worktree(self):
        result = self.run_command("land")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("no worktree for B", result.stderr)

    def test_Land_stops_on_merge_preflight_errors(self):
        real_git = shutil.which("git")
        for code in (1, 128):
            with self.subTest(code=code):
                self.setUp()
                self.run_branch()
                primary = self.git("rev-parse", "main").stdout
                wrapper = self.root / "bin/git"
                wrapper.parent.mkdir()
                wrapper.write_text(f'#!{sys.executable}\nimport os, sys\nif "merge-tree" in sys.argv: sys.exit({code})\nos.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n')
                wrapper.chmod(0o755)
                with mock.patch.dict(os.environ, PATH=str(wrapper.parent) + os.pathsep + os.environ["PATH"]):
                    result = self.run_command("land")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(self.git("rev-parse", "main").stdout, primary)

    def test_Land_refuses_a_primary_branch_advanced_on_origin(self):
        tree, _, tip = self.run_branch()
        primary = self.git("rev-parse", "main").stdout
        clone = self.root / "other-clone"
        self.git("clone", "-q", str(self.remote), str(clone))
        self.git("config", "user.name", "Test", repo=clone)
        self.git("config", "user.email", "test@example.invalid", repo=clone)
        self.write("other.py", "remote primary change\n", repo=clone)
        self.commit("advance origin main", repo=clone)
        self.git("push", "-q", "origin", "main", repo=clone)
        result = self.run_command("land")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.git("rev-parse", "main").stdout, primary)
        self.assertTrue(tree.exists())
        self.assertEqual(self.git("rev-parse", "run/B").stdout.strip(), tip)
        self.assertIn("origin/main", result.stderr)
        self.assertIn("git merge --no-edit origin/main", result.stderr)

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
    def test_Doctor_is_quiet_without_worktrees_or_setup(self):
        result = self.run_command("doctor", slug=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

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
