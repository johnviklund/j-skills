"""Run proof rows 1, 3, and 4 in a disposable Git worktree."""

import argparse
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


SKILL = Path('.github/skills/jflow')
REFERENCES = tuple(Path('references') / f'{step}.md' for step in ('spec', 'build', 'check', 'done'))
SIZE_TEST = [
    sys.executable, '-m', 'unittest', 'discover', '-s', str(SKILL / 'scripts/tests'),
    '-k', 'test_skill_size',
]


def run_case(skill, name, padding, expected_failure=None):
    path = skill / name
    original = path.read_bytes()
    try:
        path.write_bytes(original + padding)
        result = subprocess.run(SIZE_TEST, cwd=skill.parents[2], text=True, capture_output=True)
    finally:
        path.write_bytes(original)

    if expected_failure is None:
        matched = result.returncode == 0 and result.stderr.rstrip().endswith('OK')
    else:
        matched = result.returncode == 1 and expected_failure in result.stderr
    if matched:
        print(f'{name}, +{len(padding)} bytes: {expected_failure or "OK"}')
    else:
        print(f'{name}, +{len(padding)} bytes:\n{result.stdout}{result.stderr}', file=sys.stderr)
    return matched


def markdown_padding(count):
    if count < 1:
        raise SystemExit(f'Cannot pad a Markdown file by {count} bytes with this fixture')
    return b'\n' + b'x' * (count - 1)


def prove(skill, row):
    if row == '1':
        passed = sum(run_case(skill, name, markdown_padding(1000))
                     for name in ('SKILL.md', 'references/check.md'))
        print(f'{passed}/2 additions of 1,000 bytes passed')
        return passed == 2
    if row == '3':
        skill_size = (skill / 'SKILL.md').stat().st_size
        largest_reference = max((skill / name).stat().st_size for name in REFERENCES)
        targets = [('SKILL.md', skill_size + largest_reference)]
        targets.extend((name, skill_size + (skill / name).stat().st_size) for name in REFERENCES)
        rejected = sum(run_case(skill, name, markdown_padding(14001 - size),
                                'AssertionError: 14001 not less than or equal to 14000')
                       for name, size in targets)
        print(f'{rejected}/5 reads of 14,001 bytes failed the size test')
        return rejected == 5

    name = 'scripts/jflow.py'
    padding = b'\n#' + b'x' * 3997 + b'\n'
    size = (skill / name).stat().st_size + len(padding)
    rejected = run_case(skill, name, padding, f'AssertionError: {size} not less than or equal to 30000')
    if rejected:
        print(f'4,000 added comment bytes failed the size test at {size:,} bytes')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('row', choices=('1', '3', '4'))
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    with TemporaryDirectory(prefix='jflow-size-room-') as directory:
        clone = Path(directory) / 'clone'
        worktree = Path(directory) / 'worktree'
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', repo, clone], check=True)
        subprocess.run(['git', '-C', clone, 'worktree', 'add', '--quiet', '--detach', worktree, head],
                       check=True)
        if not prove(worktree / SKILL, args.row):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
