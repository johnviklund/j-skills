#!/usr/bin/env python3
"""Install and run workflow git hooks. Python 3 standard library and git required.

Run `python3 hooks.py install` in a repo. pre-push also requires gitleaks
(install with `brew install gitleaks` or `mise use -g gitleaks`).
"""
import argparse
import os
from pathlib import Path
import shlex
import shutil
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


def install(check=False):
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
    if check:
        missing = [hook for hook in HOOKS if not (directory / hook).is_file()
                   or not os.access(directory / hook, os.X_OK)]
        print('would install ' + ', '.join(missing) if missing else 'installed')
        return 0
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


def pre_push(remote):
    if not shutil.which('gitleaks'):
        print('workflow: install gitleaks before pushing (brew install gitleaks or mise use -g gitleaks)',
              file=sys.stderr)
        return 1
    # Git sends one local/remote ref pair per line; all-zero local SHAs delete refs.
    for line in sys.stdin:
        local_ref, local_sha, remote_ref, remote_sha = line.split()
        if set(local_sha) == {'0'}:
            continue
        if subprocess.run(['git', 'rev-list', '--quiet', local_sha, '--not', '--remotes']).returncode:
            print(f'workflow: cannot list outgoing commits for {local_ref}', file=sys.stderr)
            return 1
        result = subprocess.run(['gitleaks', 'git',
                                 f'--log-opts={local_sha} --not --remotes',
                                 '--redact', '-v', '--no-banner'])
        if result.returncode:
            return result.returncode
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', *HOOKS))
    parser.add_argument('--check', action='store_true', help='report missing hooks without writing')
    parser.add_argument('args', nargs='*', help='git hook arguments')
    args = parser.parse_args()
    try:
        if args.command == 'install':
            return install(args.check)
        if args.command == 'pre-commit':
            return pre_commit()
        return pre_push(args.args[0])
    except (OSError, subprocess.CalledProcessError) as error:
        print(f'workflow hook: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
