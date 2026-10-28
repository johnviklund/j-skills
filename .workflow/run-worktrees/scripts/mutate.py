#!/usr/bin/env python3
"""Mutation sweep for run-worktrees: apply each mutation to a temporary copy of the workflow skill,
run the full suite there, and report the mutations no test catches. Tracked files are never edited.
Exit 0: every mutation fails the suite · 1: some survive · 2: a pattern no longer matches once."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

R, C = "run-worktree.py", "check-run.py"
I8 = " " * 8
TAGS = 'tag[0] in ("sh", "bash", "shell")'
# (id, file, text, replacement). Left out as equivalent: X22, starting `shell` as true, since
# `shell` is read only inside a fence and every fence opening sets it.
MUTATIONS = [
    # setup parser, `add_worktree` (C4-1)
    ("M25", R, "elif fenced and shell:", "elif shell:"),
    ("M26", R, "elif fenced and shell:", "elif fenced:"),
    ("M27", R, 'if line.lstrip().startswith("```"):', 'if line.startswith("```"):'),
    ("M28", R, "shell = not tag or ", "shell = False or "),
    ("X1", R, "shell = not tag or " + TAGS, "shell = True"),
    ("X2", R, TAGS, 'tag[0] in ("bash", "shell")'),
    ("X3", R, TAGS, 'tag[0] in ("sh", "shell")'),
    ("X4", R, TAGS, 'tag[0] in ("sh", "bash")'),
    ("X5", R, "found |= shell", "found = shell"),
    ("X6", R, "found |= shell", "found = True"),
    ("X7", R, "if not found:", "if False:"),
    ("X8", R, "if not fenced:", "if True:"),
    ("X9", R, "fenced = not fenced", "fenced = True"),
    ("X10", R, "tag = line.lstrip()[3:].split()", "tag = line[3:].split()"),
    ("X11", R, "tag = line.lstrip()[3:].split()", 'tag = line.lstrip()[3:].split(" ")'),
    ("X12", R, 'tag[0] in ("sh"', 'tag[-1] in ("sh"'),
    ("X13", R, "commands.append(line)", "pass"),
    ("X14", R, "fenced = shell = found = False", "shell = found = False\n" + I8 + "fenced = True"),
    ("X15", R, "fenced = shell = found = False", "fenced = shell = False\n" + I8 + "found = True"),
    ("X16", R, "if not fenced:", "if fenced:"),
    ("X17", R, "fenced = not fenced", "fenced = False"),
    ("X18", R, "elif fenced and shell:", "elif fenced or shell:"),
    ("X19", R, "tag = line.lstrip()[3:]", "tag = line.lstrip()[4:]"),
    ("X20", R, 'tag[0] in ("sh"', 'tag[0] not in ("sh"'),
    ("X21", R, 'commands = "\\n".join(commands)', 'commands = " ".join(commands)'),
    # the rest of `add_worktree` and `worktree_setup`
    ("A1", R, 'if ".worktrees/" not in text.splitlines():', "if True:"),
    ("A2", R, 'if checks.git_out(repo, "rev-parse", "--verify", f"refs/heads/{branch}"):', "if False:"),
    ("A3", R, '    if body is None:\n        print("no ## Worktree setup', '    if False:\n        print("no ## Worktree setup'),
    ("A4", R, "cwd=path, stdout=sys.stderr, check=True)", "cwd=path, stdout=sys.stderr, check=False)"),
    ("A5", R, '["bash", "-e", "-c", commands]', '["bash", "-c", commands]'),
    ("W1", R, "if block is not None else None", "if block else None"),
    # where
    ("WH1", R, 'if "origin" in git(repo, "remote").splitlines():', "if True:"),
    ("WH3", R, "if not path.exists() and (remote_sha or", "if (remote_sha or"),
    ("WH4", R, "and (remote_sha or checks.git_out", "and (checks.git_out"),
    ("WH5", R, '(remote_sha or checks.git_out(repo, "rev-parse", "--verify", f"refs/heads/run/{slug}"))', "(remote_sha)"),
    ("WH6", R, 'if git(path, "branch", "--show-current") != f"run/{slug}":', "if False:"),
    ("WH9", R, '                git(path, "merge", "--ff-only", remote)', "                pass"),
    # started, open_run
    ("S1", R, 'not in (None, "todo")', 'not in ("todo",)'),
    ("S2", R, 'for name in ("plan.md", "patch_plan.md")', 'for name in ("plan.md",)'),
    ("O1", R, "    if path != repo:\n        return path\n    if started", "    if started"),
    ("O2", R, '    if started(repo / ".workflow" / slug):\n        return repo\n', ""),
    ("O3", R, 'busy = bool(git(repo, "status", "--porcelain"))', "busy = False"),
    ("O5", R, ' or (repo / ".worktrees" / brief.parent.name).exists()', ""),
    ("O6", R, 'in ("done", "parked"):\n            continue', 'in ("done",):\n            continue'),
    ("O7", R, 'in ("done", "parked"):\n            continue', 'in ("parked",):\n            continue'),
    ("O8", R, "busy |= started(brief.parent)", "busy = started(brief.parent)"),
    ("O9", R, "if busy else repo", "if True else repo"),
    # land
    ("L1", R, 'if git(repo, "branch", "--show-current") != primary:', "if False:"),
    ("L2", R, '    if path == repo:\n        raise RuntimeError(f"no worktree', '    if False:\n        raise RuntimeError(f"no worktree'),
    ("L3", R, "    if dirty:\n", "    if False:\n"),
    ("L4", R, "if preview.returncode == 1:", "if preview.returncode == 2:"),
    ("L5", R, 'if not conflicts or conflicts == [""]:', "if False:"),
    ("L6", R, "if all(Path(p).suffix in", "if any(Path(p).suffix in"),
    ("L7", R, 'suffix in (".md", ".txt") for p', 'suffix in (".md",) for p'),
    ("L8", R, "    if preview.returncode:\n        raise", "    if False:\n        raise"),
    ("L9", R, "    if unpushed:\n", "    if False:\n"),
    ("L10", R, '"merge", "--ff", "--no-edit", branch', '"merge", "--no-ff", "--no-edit", branch'),
    ("L11", R, 'if git(repo, "ls-remote", "--heads", "origin", branch):', "if True:"),
    ("L12", R, '        git(repo, "push", "origin", "--delete", branch)', "        pass"),
    ("L13", R, '    git(repo, "branch", "-d", branch)\n', ""),
    ("L14", R, '    git(repo, "push", "origin", primary)\n', ""),
    # doctor
    ("D1", R, "if paths and worktree_setup(repo) is None:", "if worktree_setup(repo) is None:"),
    ("D2", R, "if not brief.is_file() or checks", "if checks"),
    ("D3", R, 'not in ("drafting", "complete"):', 'not in ("drafting",):'),
    ("D3b", R, 'not in ("drafting", "complete"):', 'not in ("complete",):'),
    # main
    ("MN1", R, "if args.slug and not re.fullmatch(", "if False and not re.fullmatch("),
    ("MN2", R, 'if args.command != "doctor" and not args.slug:', "if False:"),
    ("MN3", R, '            git(repo, "check-ref-format", "--branch", f"run/{args.slug}")\n', "            pass\n"),
    ("MN4", R, "        if not checks.primary_branch(repo):\n", "        if False:\n"),
    # this run's lines in check-run.py
    ("C1", C, '            if not fence and text.startswith("# "):\n                current = None\n', ""),
    ("C2", C, 'branch == f"run/{slug}" and', "True and"),
    ("C3", C, '            os.path.realpath(repo) == os.path.join(os.path.dirname(common), ".worktrees", slug))', "            True)"),
    ("C5", C, "branch != primary and not own_run:", "branch != primary:"),
    ("C6b", C, '    return primary or next((b for b in ("main", "master")\n'
                '                            if git_out(repo, "rev-parse", "--verify", "-q", b)), "")', "    return primary"),
]


def run(skill, mutation):
    name, target, old, new = mutation
    with tempfile.TemporaryDirectory(prefix="rw-mutate-") as tmp:
        copy = Path(tmp) / "workflow"
        shutil.copytree(skill, copy, ignore=shutil.ignore_patterns("__pycache__"))
        path = copy / "scripts" / target
        text = path.read_text()
        if text.count(old) != 1:
            return name, "missing", f"pattern found {text.count(old)} times in {target}"
        path.write_text(text.replace(old, new))
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(copy / "scripts/tests")],
                                capture_output=True, text=True)
    failed = sorted({line.split(" (")[0].split(": ", 1)[1] for line in result.stderr.splitlines()
                     if line.startswith(("FAIL: ", "ERROR: "))})
    return name, "killed" if result.returncode else "SURVIVED", " ".join(failed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids", nargs="*", help="run only these mutation ids")
    parser.add_argument("--skill", default=str(Path(__file__).resolve().parents[3] / ".github/skills/workflow"))
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    args = parser.parse_args()
    chosen = [m for m in MUTATIONS if not args.ids or m[0] in args.ids]
    unknown = set(args.ids) - {m[0] for m in MUTATIONS}
    if unknown:
        parser.error(f"unknown mutation ids: {' '.join(sorted(unknown))}")
    with ThreadPoolExecutor(args.jobs) as pool:
        results = list(pool.map(lambda m: run(args.skill, m), chosen))
    for name, outcome, detail in results:
        print(f"{outcome:8} {name:4} {detail}")
    outcomes = [outcome for _, outcome, _ in results]
    print(f"{outcomes.count('killed')} killed · {outcomes.count('SURVIVED')} survived · {outcomes.count('missing')} missing")
    return 2 if "missing" in outcomes else 1 if "SURVIVED" in outcomes else 0


if __name__ == "__main__":
    sys.exit(main())
