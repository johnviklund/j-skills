#!/usr/bin/env bash
# Dependencies: bash, python3 and git. All contents are synthetic.
set -euo pipefail
fixture=/tmp/checkup-fixture
if [[ -e "$fixture" || -L "$fixture" ]]; then
  [[ ! -L "$fixture" && -f "$fixture/.fixture-marker" ]] || {
    echo "Refusing to replace $fixture without its fixture marker." >&2; exit 1;
  }
  rm -rf -- "$fixture"
fi
mkdir -p "$fixture"
python3 - "$fixture" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
files = {
    '.fixture-marker': 'Synthetic checkup fixture\n',
    'AGENTS.md': '# Fixture\nSynthetic backlog tracker. Run `git diff --check` to verify edits.\n',
    'MEMORY.md': '# Memory\n- [Fixture conventions](memory/conventions.md): applies when editing the synthetic backlog.\n',
    'memory/conventions.md': '# Fixture conventions\nApplies when: editing the synthetic backlog.\nStatus: current\nKeep entries synthetic.\n',
    '.agents/skills/verify-fixture/SKILL.md': '---\nname: verify-fixture\ndescription: Verify the synthetic fixture backlog.\n---\nRun `git diff --check` in this repo.\n',
    '.workflow/finished/wrap.md': 'Command: workflow wrap finished\nCreated: 2026-10-25\nBase: none\nInputs: none\nStatus: done\n\nSynthetic setup finished. No outstanding work.\n',
    '.workflow/finished/brainstorm.md': 'Command: workflow brainstorm finished\nCreated: 2026-10-25 · Fixture\nBase: none\nInputs: none\nStatus: done\n\nCreate a synthetic backlog for checkup.\n',
    'TODO.md': '# Backlog\n\n' + ''.join(
        f'- [ ] Synthetic task {n}: review the sample backlog entry and propose whether to keep it for a later pass.\n'
        for n in range(180)),  # Exceeds the checkup threshold of 15,360 bytes.
}
for name, content in files.items():
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
PY
git -C "$fixture" init -q -b main
git -C "$fixture" add .
git -C "$fixture" -c user.name='Fixture' -c user.email='fixture@example.invalid' commit -qm 'Create synthetic checkup fixture'
