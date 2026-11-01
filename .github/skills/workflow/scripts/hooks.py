#!/usr/bin/env python3
"""Install and run workflow git hooks. Python 3 standard library and git required.

Run `python3 hooks.py install` in a repo. pre-push also requires gitleaks
(install with `brew install gitleaks` or `mise use -g gitleaks`).
"""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys

MARKER = '# j-skills workflow hook'
HOOKS = ('pre-commit', 'pre-push')


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def stub(hook):
    # The installing copy wins; runtime fallbacks cover the README install folders.
    paths = [shlex.quote(str(Path(__file__).resolve()))]
    paths += [f'"$root/{folder}/skills/workflow/scripts/hooks.py"'
              for folder in ('.github', '.agents', '.claude', '.codex')]
    paths += [f'"$HOME/{folder}/skills/workflow/scripts/hooks.py"'
              for folder in ('.agents', '.claude', '.codex', '.copilot')]
    paths += ['"${CODEX_HOME:-$HOME/.codex}/skills/workflow/scripts/hooks.py"']
    missing_exit = 0 if hook == 'pre-commit' else 1
    return f'''#!/bin/sh
{MARKER}
root=$(git rev-parse --show-toplevel) || exit 1
searched=""
for script in {' '.join(paths)}; do
    searched="$searched\n  $script"
    if [ -f "$script" ]; then exec python3 "$script" {hook} "$@"; fi
done
printf 'workflow: hooks.py missing; searched:%b\n' "$searched" >&2
exit {missing_exit}
'''


def install():
    configured = subprocess.run(['git', 'config', '--get', 'core.hooksPath'],
                                capture_output=True, text=True)
    if configured.returncode == 0:
        print('Refusing core.hooksPath: ' + configured.stdout.strip(), file=sys.stderr)
        return 1
    directory = Path(git('rev-parse', '--git-path', 'hooks'))
    for hook in HOOKS:
        path = directory / hook
        if path.exists() and MARKER not in path.read_text():
            print(f'Refusing foreign hook: {path}', file=sys.stderr)
            return 1
    directory.mkdir(parents=True, exist_ok=True)
    for hook in HOOKS:
        path = directory / hook
        content = stub(hook)
        if not path.exists() or path.read_text() != content:
            path.write_text(content)
        path.chmod(path.stat().st_mode | 0o111)
    print('installed')
    return 0


def pre_commit():
    os.chdir(git('rev-parse', '--show-toplevel'))
    paths = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z']).decode().split('\0')
    slugs = {parts[1] for path in paths if len(parts := path.split('/')) >= 3
             and parts[0] == '.workflow' and parts[1] != 'archive'
             and Path('.workflow', parts[1]).is_dir()}
    checker = Path(__file__).resolve().with_name('check-run.py')
    if slugs and not checker.is_file():
        print(f'Warning: check-run.py missing; searched: {checker}', file=sys.stderr)
        return 0
    for slug in sorted(slugs):
        result = subprocess.run([sys.executable, str(checker), slug])
        if result.returncode:
            return result.returncode
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', *HOOKS))
    parser.add_argument('args', nargs='*', help='git hook arguments')
    args = parser.parse_args()
    try:
        if args.command == 'install':
            return install()
        if args.command == 'pre-commit':
            return pre_commit()
        return 1  # pre-push is implemented by the next ticket.
    except (OSError, subprocess.CalledProcessError) as error:
        print(f'workflow hook: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
