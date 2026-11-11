#!/usr/bin/env python3
"""Run spec-why proof rows against this checkout; raw transcripts stay in /tmp.

Requires Python 3, git, and authenticated Claude Code for rows 1 and 2.
Each model evaluation starts a fresh, read-only CLI session on the configured spec seat.
"""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
SKILL = ROOT / '.github/skills/jflow'
CLI = SKILL / 'scripts/jflow.py'
SOLVED = 'Text files keep their word counts, and PNG files contribute zero words.'
PRODUCT = '''# tally
## The desired state
### Counts you can trust
Folder word counts include text and exclude binary data.
### Fast on big folders
Count large folders without an unnecessary full-file scan.
'''
ROADMAP = f'''# Roadmap
## Next up
### skip-binary
- Problem: Writers running tally on exported folders see PNG bytes counted as words. In a folder
  containing a three-word text file and one PNG, tally reports 74 words instead of 3.
- Why now: The next export includes images, so the current total cannot be used.
- Options: Skip files containing a NUL byte in the first 8 KiB; chosen. Extension filtering misses
  unnamed binary files. Decoding all bytes guesses whether non-UTF-8 text is binary.
- Solved when: {SOLVED}
- Out of scope: No recursive traversal changes or new output format.
- Serves: Counts you can trust
- Open for spec: Should a skipped binary file appear in the existing verbose listing?
'''


def run(args, cwd=ROOT):
    return subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True, text=True)


def git(repo, *args):
    result = run(['git', '-C', repo, *args])
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def init_repo(repo):
    repo.mkdir(parents=True)
    git(repo, 'init', '-q')
    git(repo, 'config', 'user.email', 'fixture@example.invalid')
    git(repo, 'config', 'user.name', 'Fixture')
    (repo / 'tally.py').write_text('''import sys
from pathlib import Path
print(sum(len(p.read_bytes().split()) for p in Path(sys.argv[1]).iterdir() if p.is_file()))
''')
    git(repo, 'add', '.')
    git(repo, 'commit', '-qm', 'fixture base')
    return git(repo, 'rev-parse', 'HEAD')


def claude_binary():
    configured = os.environ.get('JFLOW_CLAUDE_BIN')
    if configured:
        return configured
    found = shutil.which('claude')
    if found and run([found, '--version']).returncode == 0:
        return found
    # mise's lazy wrapper can try to write shims inside a read-only sandbox.
    installs = Path.home() / '.local/share/mise/installs/claude'
    candidates = sorted((p for p in installs.glob('*/claude')
                         if all(v.isdigit() for v in p.parent.name.split('.'))),
                        key=lambda p: tuple(int(v) for v in p.parent.name.split('.')))
    if candidates:
        return str(candidates[-1])
    raise RuntimeError('Claude Code not found; set JFLOW_CLAUDE_BIN')


def session(raw, row, attempt):
    repo = raw / f'row{row}-run{attempt}'
    init_repo(repo)
    (repo / 'PRODUCT.md').write_text(PRODUCT)
    (repo / 'DESIGN.md').write_text('# Design\nPython standard library CLI. The command prints a folder word count.\n')
    (repo / 'ROADMAP.md').write_text(ROADMAP if row == 1 else '# Roadmap\n## Next up\n')
    for name in ('jflow', 'plain'):
        dest = repo / '.claude/skills' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / '.github/skills' / name, dest,
                        ignore=shutil.ignore_patterns('__pycache__', 'tests'))
    git(repo, 'add', '.')
    git(repo, 'commit', '-qm', 'fixture context')
    message = ('jflow spec skip-binary: roadmap item skip-binary in ROADMAP.md' if row == 1
               else 'jflow spec skip-binary: tally counts binary files such as PNGs as words')
    prompt = message + '''

Use the project-local jflow skill in .claude/skills/jflow/SKILL.md.
Stop after round 1. Print the questions for that round, followed by a tentative spec header and
the first Proof row. Do not write or commit a spec and do not run later steps.
'''
    seat = json.loads(run([sys.executable, CLI, 'seat', 'spec']).stdout)
    args = [claude_binary(), '-p', prompt, '--model', seat['model'], '--effort', seat['effort'],
            '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
            '--tools', 'Read,Glob,Grep,Skill,Bash', '--allowedTools', 'Read Glob Grep Skill Bash(git *)',
            '--permission-mode', 'dontAsk', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}']
    result = subprocess.run(args, cwd=repo, capture_output=True, text=True, timeout=300)
    (raw / f'row{row}-run{attempt}.jsonl').write_text(result.stdout)
    (raw / f'row{row}-run{attempt}.stderr').write_text(result.stderr)
    answers = []
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'assistant':
            answers.extend(block['text'] for block in event.get('message', {}).get('content', [])
                           if block.get('type') == 'text')
    answer = '\n'.join(answers)
    (raw / f'row{row}-run{attempt}.txt').write_text(answer)
    return {'run': attempt, 'exit': result.returncode, 'answer': answer,
            'raw': str(raw / f'row{row}-run{attempt}.jsonl')}


def sessions(row, raw):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda n: session(raw, row, n), (1, 2)))
    for result in results:
        print(json.dumps(result))
    return int(any(r['exit'] for r in results))


def validation(row, raw):
    repo = raw / f'validation-row{row}'
    base = init_repo(repo)
    sys.path.insert(0, str(SKILL / 'scripts/tests'))
    from test_jflow import SPEC
    folder = repo / '.jflow/demo'
    folder.mkdir(parents=True)
    spec = folder / 'spec.md'
    original = SPEC.format(base=base)
    if row == 4:
        spec.write_text(original)
        result = run([sys.executable, CLI, 'validate', 'demo', 'spec', '--repo', repo])
        assert (result.returncode, result.stdout, result.stderr) == (0, '', ''), result
        result = run([sys.executable, '-m', 'unittest',
                      'test_validate.Validation.test_historical_specs_and_all_sixteen_receipts'],
                     cwd=SKILL / 'scripts/tests')
        (raw / 'historical.txt').write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and 'Ran 1 test' in result.stderr and 'OK' in result.stderr, result
        print('row 4: historical-specs unittest OK; no PRODUCT.md: validate exit 0, no output')
        return 0
    (repo / 'PRODUCT.md').write_text(PRODUCT)
    for label, serves, expected in [('missing', '', 1), ('unknown', 'Serves: Unknown\n', 1),
                                     ('known', 'Serves: Counts you can trust\n', 0)]:
        spec.write_text(original.replace('A run with', serves + 'A run with'))
        results = []
        for command in ('validate', 'record'):
            args = [sys.executable, CLI, command, 'demo', 'spec', '--repo', repo]
            if command == 'record':
                args += ['--model', 'fixture', '--effort', 'medium']
            result = run(args)
            results.append({'command': command, 'exit': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr})
            assert result.returncode == expected, results
            if expected:
                assert 'Serves' in result.stderr and 'spec.md:' in result.stderr, results
                assert not (folder / 'run.jsonl').exists(), results
        (raw / f'validation-{label}.json').write_text(json.dumps(results, indent=2))
        print(f'{label}: validate={results[0]["exit"]}, record={results[1]["exit"]}, '
              f'run.jsonl lines={len((folder / "run.jsonl").read_text().splitlines()) if (folder / "run.jsonl").exists() else 0}')
    return 0


def attack(raw):
    repo = raw / 'attack'
    base = init_repo(repo)
    sys.path.insert(0, str(SKILL / 'scripts/tests'))
    from test_jflow import SPEC
    folder = repo / '.jflow/demo'
    folder.mkdir(parents=True)
    original = SPEC.format(base=base)
    cases = [
        ('body-example', PRODUCT,
         original.replace('A fixture run.', 'The old header was:\n```text\nServes: Counts you can trust\n```')),
        ('fenced-outcome', PRODUCT + '\n## Old examples\n```markdown\n### Retired outcome\n```\n',
         original.replace('A run with', 'Serves: Retired outcome\nA run with')),
        ('closing-hashes', PRODUCT.replace('### Counts you can trust', '### Counts you can trust ###'),
         original.replace('A run with', 'Serves: Counts you can trust\nA run with')),
    ]
    for name, product, text in cases:
        (repo / 'PRODUCT.md').write_text(product)
        (folder / 'spec.md').write_text(text)
        log = folder / 'run.jsonl'
        log.unlink(missing_ok=True)
        results = []
        for command in ('validate', 'record'):
            args = [sys.executable, CLI, command, 'demo', 'spec', '--repo', repo]
            if command == 'record':
                args += ['--model', 'fixture', '--effort', 'medium']
            result = run(args)
            results.append({'command': command, 'exit': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr})
        (raw / f'{name}.json').write_text(json.dumps(results, indent=2))
        (raw / f'{name}-spec.md').write_text(text)
        (raw / f'{name}-PRODUCT.md').write_text(product)
        print(f'{name}: validate={results[0]["exit"]}, record={results[1]["exit"]}, '
              f'run.jsonl lines={len(log.read_text().splitlines()) if log.exists() else 0}')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('row', choices=('1', '2', '3', '4', 'attack'))
    args = parser.parse_args()
    raw = Path(tempfile.mkdtemp(prefix=f'spec-why-row{args.row}-'))
    print(f'Raw output: {raw}', flush=True)
    if args.row == 'attack':
        return attack(raw)
    row = int(args.row)
    return sessions(row, raw) if row in (1, 2) else validation(row, raw)


if __name__ == '__main__':
    sys.exit(main())
