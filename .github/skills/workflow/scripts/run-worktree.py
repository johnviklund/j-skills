#!/usr/bin/env python3
"""Open and find isolated workflow runs. Paths on stdout are relative to the primary checkout."""
import argparse
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

spec = importlib.util.spec_from_file_location("check_run", Path(__file__).with_name("check-run.py"))
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def add_worktree(repo, slug, start):
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    exclude = common / "info/exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    text = exclude.read_text() if exclude.exists() else ""
    if ".worktrees/" not in text.splitlines():
        exclude.write_text(text.rstrip("\n") + "\n.worktrees/\n")
    path, branch = repo / ".worktrees" / slug, f"run/{slug}"
    if checks.git_out(repo, "rev-parse", "--verify", f"refs/heads/{branch}"):
        git(repo, "worktree", "add", str(path), branch)
    else:
        git(repo, "worktree", "add", "-b", branch, str(path), start)
    agents = checks.git_out(repo, "show", f"{checks.primary_branch(repo)}:AGENTS.md")
    block = re.search(r"^## Worktree setup\s*\n(.*?)(?=^#{1,2} |\Z)", agents, re.M | re.S)
    if not block:
        print("no ## Worktree setup in AGENTS.md", file=sys.stderr)
    else:
        body = block.group(1)
        commands = "\n".join(re.findall(r"```(?:sh|bash|shell)?\n(.*?)```", body, re.S)) if "```" in body else body
        print(commands, file=sys.stderr, flush=True)
        subprocess.run(["bash", "-e", "-c", commands], cwd=path, stdout=sys.stderr, check=True)
    return path


def where(repo, slug):
    remote = f"refs/remotes/origin/run/{slug}"
    if "origin" in git(repo, "remote").splitlines():
        git(repo, "fetch", "--quiet", "--prune", "origin", "+refs/heads/run/*:refs/remotes/origin/run/*")
    path = repo / ".worktrees" / slug
    remote_sha = checks.git_out(repo, "rev-parse", "--verify", remote)
    if not path.exists() and (remote_sha or checks.git_out(repo, "rev-parse", "--verify", f"refs/heads/run/{slug}")):
        add_worktree(repo, slug, remote)
    if path.exists():
        if git(path, "branch", "--show-current") != f"run/{slug}":
            raise RuntimeError(f"{path} is not on run/{slug}")
        if remote_sha and git(path, "rev-parse", "HEAD") != remote_sha:
            if checks.git_out(path, "merge-base", "HEAD", remote) != remote_sha:
                git(path, "merge", "--ff-only", remote)
        return path
    return repo


def open_run(repo, slug):
    path = where(repo, slug)
    if path != repo:
        return path
    busy = bool(git(repo, "status", "--porcelain"))
    for brief in (repo / ".workflow").glob("*/brainstorm.md"):
        if brief.parent.name == slug or (repo / ".worktrees" / brief.parent.name).exists():
            continue
        if checks.Doc(str(brief)).status() in ("done", "parked"):
            continue
        for name in ("plan.md", "patch_plan.md"):
            plan = brief.with_name(name)
            if plan.exists():
                busy |= any(checks.field(t, "Status")[1] not in (None, "todo")
                            for t in checks.parse_tickets(checks.Doc(str(plan))))
    return add_worktree(repo, slug, checks.primary_branch(repo)) if busy else repo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("open", "where"))
    parser.add_argument("slug")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.slug):
        parser.error("slug must contain only letters, digits, dots, underscores and hyphens")
    try:
        repo = Path(git(args.repo, "worktree", "list", "--porcelain").splitlines()[0][len("worktree "): ])
        git(repo, "check-ref-format", "--branch", f"run/{args.slug}")
        if not checks.primary_branch(repo):
            raise RuntimeError("no primary branch found")
        path = open_run(repo, args.slug) if args.command == "open" else where(repo, args.slug)
        print(path.relative_to(repo).as_posix())
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
