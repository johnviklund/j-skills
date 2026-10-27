#!/usr/bin/env bash
# P1 — does a run worktree inside an ignored .worktrees/ stay invisible to the primary checkout and its tools?
set -u
SRC=${1:?usage: probe.sh <repo>}
T=$(mktemp -d); git clone -q "$SRC" "$T/repo"; cd "$T/repo"
echo ".worktrees/" >> .gitignore && git commit -qam "ignore .worktrees"
git worktree add -q -b run/demo .worktrees/demo
echo "x" > .worktrees/demo/new-file.py
echo "-- primary git status (expect empty):"; git status --porcelain
echo "-- git grep in primary sees worktree file? (expect no)"; git grep -l . -- 'new-file.py' || echo no
echo "-- rg in primary sees worktree file? (expect no)"; (command -v rg >/dev/null && rg --files | grep -c new-file || echo "rg missing")
echo "-- grep -r sees it? (plain grep ignores .gitignore)"; grep -rl "^x$" . --include=new-file.py | head -1
echo "-- find sees it?"; find . -name new-file.py | head -1
cd .worktrees/demo && git add -A && git commit -qm "T1 demo" && T1=$(git rev-parse HEAD)
cd "$T/repo"; echo y > other.txt; git add other.txt; git commit -qm "main moved"
git merge -q --no-edit run/demo && echo "-- merged; T1 sha still on main? $(git merge-base --is-ancestor $T1 HEAD && echo yes)"
python3 "$SRC/skills/workflow/scripts/check-run.py" --help >/dev/null 2>&1; cd .worktrees/demo
python3 -c "import sys; sys.path.insert(0,'$SRC/skills/workflow/scripts'); import importlib; m=importlib.import_module('check-run'.replace('-','_')) " 2>/dev/null
echo "-- check-run warnings from inside the worktree:"; python3 "$SRC/skills/workflow/scripts/check-run.py" --all 2>&1 | grep -iE "worktree|branch" | head -3
cd "$T/repo"; git worktree remove .worktrees/demo && git branch -q -d run/demo && echo "-- cleanup ok"; git worktree list
rm -rf "$T"
