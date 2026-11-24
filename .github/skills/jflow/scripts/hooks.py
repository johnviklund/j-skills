#!/usr/bin/env python3
"""Install and run the j-skills pre-push hook, which runs gitleaks on outgoing commits.

Run `python3 hooks.py install` in a repo. Python 3, git and gitleaks are required
(install gitleaks with `brew install gitleaks` or `mise use -g gitleaks`). Install
upgrades older j-skills stubs and removes the old pre-commit stub.
"""
import argparse
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

MARKER = '# j-skills hook'
# Any '# j-skills ... hook' line marks a stub an older j-skills version installed.
OURS = re.compile(r'^# j-skills( [\w.-]+)? hook$', re.M)


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def stub():
    # The installing copy wins; runtime fallbacks cover the README install folders.
    paths = [shlex.quote(str(Path(__file__).resolve()))]
    paths += [f'"$root/{folder}/skills/jflow/scripts/hooks.py"'
              for folder in ('.github', '.agents', '.claude', '.codex')]
    paths += [f'"$HOME/{folder}/skills/jflow/scripts/hooks.py"'
              for folder in ('.agents', '.claude', '.codex', '.copilot')]
    paths += ['"${CODEX_HOME:-$HOME/.codex}/skills/jflow/scripts/hooks.py"']
    return f'''#!/bin/sh
{MARKER}
root=$(git rev-parse --show-toplevel) || exit 1
searched=""
for script in {' '.join(paths)}; do
    searched="$searched\n  $script"
    if [ -f "$script" ]; then exec python3 "$script" pre-push "$@"; fi
done
printf 'jflow: hooks.py missing; searched:%b\n' "$searched" >&2
exit 1
'''


def install(check=False):
    configured = subprocess.run(['git', 'config', '--get', 'core.hooksPath'],
                                capture_output=True, text=True)
    if configured.returncode == 0:
        print('Refusing core.hooksPath: ' + configured.stdout.strip(), file=sys.stderr)
        return 1
    directory = Path(git('rev-parse', '--git-path', 'hooks'))
    push, commit = directory / 'pre-push', directory / 'pre-commit'
    if push.exists() and not OURS.search(push.read_text()):
        print(f'Refusing foreign hook: {push}', file=sys.stderr)
        return 1
    old_commit = commit.exists() and OURS.search(commit.read_text())
    if check:
        todo = []
        if not (push.is_file() and os.access(push, os.X_OK)
                and MARKER in push.read_text().splitlines()):
            todo.append('would install pre-push')
        if old_commit:
            todo.append('would remove pre-commit')
        print(', '.join(todo) or 'installed')
        return 0
    directory.mkdir(parents=True, exist_ok=True)
    content = stub()
    if not push.exists() or push.read_text() != content:
        push.write_text(content)
    push.chmod(push.stat().st_mode | 0o111)
    if old_commit:
        commit.unlink()
    print('installed')
    return 0


def pre_push(remote):
    if not shutil.which('gitleaks'):
        print('jflow: install gitleaks before pushing (brew install gitleaks or mise use -g gitleaks)',
              file=sys.stderr)
        return 1
    named = remote in git('remote').splitlines()
    # Git sends one local/remote ref pair per line; all-zero local SHAs delete refs.
    for line in sys.stdin:
        local_ref, local_sha, remote_ref, remote_sha = line.split()
        if set(local_sha) == {'0'}:
            continue
        # A URL or path target is known to hold only the sha its ref points at, when we have it.
        known = set(remote_sha) != {'0'} and not subprocess.run(
            ['git', 'cat-file', '-e', f'{remote_sha}^{{commit}}'], capture_output=True).returncode
        exclusion = [f'--remotes={remote}'] if named else [remote_sha] if known else []
        not_part = ['--not', *exclusion] if exclusion else []
        if subprocess.run(['git', 'rev-list', '--quiet', local_sha, *not_part]).returncode:
            print(f'jflow: cannot list outgoing commits for {local_ref}', file=sys.stderr)
            return 1
        result = subprocess.run(['gitleaks', 'git',
                                 f'--log-opts={" ".join([local_sha, *not_part])}',
                                 '--redact', '-v', '--no-banner'])
        if result.returncode:
            return result.returncode
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'pre-push'))
    parser.add_argument('--check', action='store_true', help='report missing hooks without writing')
    parser.add_argument('args', nargs='*', help='git hook arguments')
    args = parser.parse_args()
    try:
        if args.command == 'install':
            return install(args.check)
        return pre_push(args.args[0])
    except (OSError, subprocess.CalledProcessError) as error:
        print(f'jflow hook: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
