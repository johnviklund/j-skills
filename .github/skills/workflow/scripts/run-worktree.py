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


def worktree_setup(repo):
    agents = checks.git_out(repo, "show", f"{checks.primary_branch(repo)}:AGENTS.md")
    block = checks.Doc("AGENTS.md", text=agents).section("Worktree setup")
    return "\n".join(text for _, text in block) if block is not None else None


def add_worktree(repo, slug, start):
    body = worktree_setup(repo)
    if body is not None:
        commands = []
        fenced = shell = found = False
        for line in body.splitlines():
            if line.lstrip().startswith("```"):
                if not fenced:
                    tag = line.lstrip()[3:].split()
                    shell = not tag or tag[0] in ("sh", "bash", "shell")
                    found |= shell
                fenced = not fenced
            elif fenced and shell:
                commands.append(line)
        if not found:
            raise RuntimeError("## Worktree setup requires a sh, bash, shell or untagged fence")
        commands = "\n".join(commands)
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
    if body is None:
        print("no ## Worktree setup in AGENTS.md", file=sys.stderr)
    else:
        print(commands, file=sys.stderr, flush=True)
        subprocess.run(["bash", "-e", "-c", commands], cwd=path, stdout=sys.stderr, check=True)
    return path


def where(repo, slug):
    remote = f"refs/remotes/origin/run/{slug}"
    if "origin" in git(repo, "remote").splitlines():
        try:
            git(repo, "fetch", "--quiet", "--prune", "origin", "+refs/heads/run/*:refs/remotes/origin/run/*")
        except RuntimeError as error:
            print(f"could not fetch origin: {error}; using local refs", file=sys.stderr)
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


def started(run_dir):
    return any(checks.field(t, "Status")[1] not in (None, "todo")
               for name in ("plan.md", "patch_plan.md") if (plan := run_dir / name).exists()
               for t in checks.parse_tickets(checks.Doc(str(plan))))


def open_run(repo, slug):
    path = where(repo, slug)
    if path != repo:
        return path
    if started(repo / ".workflow" / slug):
        return repo
    busy = bool(git(repo, "status", "--porcelain"))
    for brief in (repo / ".workflow").glob("*/brainstorm.md"):
        if brief.parent.name == slug or (repo / ".worktrees" / brief.parent.name).exists():
            continue
        if checks.Doc(str(brief)).status() in ("done", "parked"):
            continue
        busy |= started(brief.parent)
    return add_worktree(repo, slug, checks.primary_branch(repo)) if busy else repo


def land(repo, slug):
    primary, branch = checks.primary_branch(repo), f"run/{slug}"
    if git(repo, "branch", "--show-current") != primary:
        raise RuntimeError(f"primary checkout must be on {primary}")
    git(repo, "fetch", "--quiet", "origin", primary)
    behind = git(repo, "log", "--oneline", f"{primary}..origin/{primary}")
    if behind:
        raise RuntimeError(f"origin/{primary} moved; merge it into the primary checkout with git merge --no-edit origin/{primary}, then land again:\n{behind}")
    path = where(repo, slug)
    if path == repo:
        raise RuntimeError(f"no worktree for {slug}")
    dirty = git(path, "status", "--porcelain")
    if dirty:
        raise RuntimeError(f"commit or remove uncommitted work in {path}:\n{dirty}")
    preview = subprocess.run(["git", "-C", str(repo), "merge-tree", "--write-tree", "--name-only", "-z",
                              primary, branch], capture_output=True, text=True)
    if preview.returncode == 1:
        # Only the run checkout enters a merge, even when the primary checkout is dirty.
        merge = subprocess.run(["git", "-C", str(path), "merge", "--no-edit", primary],
                               capture_output=True, text=True)
        conflicts = git(path, "diff", "--name-only", "--diff-filter=U", "-z").strip("\0").split("\0")
        if not conflicts or conflicts == [""]:
            raise RuntimeError(merge.stderr or merge.stdout or "merge preflight changed; retry land")
        print(merge.stdout + merge.stderr, file=sys.stderr)
        if all(Path(p).suffix in (".md", ".txt") for p in conflicts):
            print("Resolve keeping both sides, commit, land again.", file=sys.stderr)
            return 4
        print(f"Resolve in {path}, commit, run tests, then workflow review {slug}.", file=sys.stderr)
        return 3
    if preview.returncode:
        raise RuntimeError(preview.stderr or preview.stdout)
    unpushed = git(repo, "log", "--oneline", f"origin/{primary}..{primary}")
    if unpushed:
        raise RuntimeError(f"scan and push unpushed primary commits before landing:\n{unpushed}")
    git(repo, "merge", "--ff", "--no-edit", branch)
    git(repo, "push", "origin", primary)
    if git(repo, "ls-remote", "--heads", "origin", branch):
        git(repo, "push", "origin", "--delete", branch)
    git(repo, "worktree", "remove", str(path))
    git(repo, "branch", "-d", branch)
    print(f"landed {slug} on {primary}; pushed and removed {branch} and its worktree")
    return 0


def doctor(repo):
    root = repo / ".worktrees"
    paths = sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
    if paths and worktree_setup(repo) is None:
        print("missing ## Worktree setup in committed primary AGENTS.md")
    for path in paths:
        brief = path / ".workflow" / path.name / "brainstorm.md"
        if not brief.is_file() or checks.Doc(str(brief)).status() not in ("drafting", "complete"):
            print(f"{path.relative_to(repo)} has no live run")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("open", "where", "land", "doctor"))
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    if args.command != "doctor" and not args.slug:
        parser.error("a run slug is required")
    if args.slug and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.slug):
        parser.error("slug must contain only letters, digits, dots, underscores and hyphens")
    try:
        repo = Path(git(args.repo, "worktree", "list", "--porcelain").splitlines()[0][len("worktree "):])
        if args.slug:
            git(repo, "check-ref-format", "--branch", f"run/{args.slug}")
        if not checks.primary_branch(repo):
            raise RuntimeError("no primary branch found")
        if args.command == "doctor":
            return doctor(repo)
        if args.command == "land":
            return land(repo, args.slug)
        path = open_run(repo, args.slug) if args.command == "open" else where(repo, args.slug)
        print(path.relative_to(repo).as_posix())
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
