#!/usr/bin/env bash
# Dependencies: bash, python3 and git. Each run creates a new synthetic repo and local origin.
set -euo pipefail
fixture=$(mktemp -d /tmp/run-worktrees.XXXXXX)
python3 - "$fixture" <<'PY'
from pathlib import Path
import subprocess
import sys
root = Path(sys.argv[1]); repo = root / 'repo'; repo.mkdir()
def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
def commit(message):
    git('add', '.'); git('commit', '-qm', message); return git('rev-parse', 'HEAD')
git('init', '-q', '-b', 'main')
git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
(repo / 'AGENTS.md').write_text('## Verifying your work\nRun `git diff --check`.\n## Worktree setup\n```sh\ngit diff --check\n```\n')
base = commit('Synthetic baseline')
for slug in ('A', 'B'):
    folder = repo / '.workflow' / slug; folder.mkdir(parents=True)
    header = f'Created: 2026-10-27 · Fixture\nBase: {base}\nInputs: none\nStatus: complete\n'
    brief = f'Command: workflow brainstorm {slug}\n{header}\n## Problem\nTest isolated runs.\n## Outcome\nRead {slug.lower()}.VALUE.\n## Behaviours\n- B1 — import {slug.lower()} → VALUE is {slug}\n## Decisions\nSynthetic values only.\n## Test seams\nPython import.\n## Out of scope\nLive services.\nDocs read: AGENTS.md\n'
    tickets = ''
    for n in range(1, 3 if slug == 'A' else 2):
        value = slug if n == 1 else 'A done'
        tickets += f'### T{n} — Write {value}\nDelivers: B1 · Blocked by: none · Lane: logic\nBudget: code +1 · tests +0\nSeam: {slug.lower()}.py\nAccept:\n- [ ] importing {slug.lower()} yields VALUE {value}\nVerify: `python3 -c "import {slug.lower()}; assert {slug.lower()}.VALUE == \'{value}\'"` (pre: module missing)\nSkills: none\nStatus: todo\n'
    (folder / 'brainstorm.md').write_text(brief)
    (folder / 'plan.md').write_text(f'Command: workflow plan {slug}\n{header}\n## Findings\nSynthetic repo.\n## Tickets\n{tickets}## Coverage\nB1 → T1\n## Risks\nLocal only.\n## TODO impacts\nNone.\n## Product doc impacts\nNone.\n')
commit('Ready runs A and B')
(repo / 'a.py').write_text("VALUE = 'A'\n")
sha = commit('A T1')
plan = repo / '.workflow/A/plan.md'
plan.write_text(plan.read_text().replace('- [ ]', '- [x]', 1).replace('Status: todo', f'Status: done @ {sha}\nWriter: Fixture', 1))
commit('A executing with T2 pending')
git('clone', '-q', '--bare', str(repo), str(root / 'origin.git'))
git('remote', 'add', 'origin', str(root / 'origin.git')); git('fetch', '-q', 'origin')
git('remote', 'set-head', 'origin', 'main'); git('branch', '--set-upstream-to=origin/main', 'main')
PY
printf '%s\n' "$fixture/repo"
