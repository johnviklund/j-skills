#!/usr/bin/env python3
"""Reproducible CLI proof and attacks. All fixtures live in temporary repositories."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
SCRIPT = ROOT / '.github/skills/jflow/scripts/jflow.py'
BASE = 'ecdfea7'


def run(*args, cwd=ROOT, check=True):
    return subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True,
                          text=True, check=check)


def git(repo, *args):
    return run('git', '-C', repo, *args).stdout.strip()


class Fixture:
    def __init__(self, repo):
        self.repo = repo
        git(repo, 'init', '-q')
        git(repo, 'config', 'user.name', 'Fixture')
        git(repo, 'config', 'user.email', 'fixture@example.invalid')
        (repo / 'code.py').write_text('value = 0\n')
        self.commit('base')
        self.base = git(repo, 'rev-parse', 'HEAD')
        self.folder = repo / '.jflow/demo'
        self.folder.mkdir(parents=True)
        self.spec = self.folder / 'spec.md'
        self.spec.write_text('# demo\nStatus: ready\nBase: ' + self.base + '\n\n## Proof\n'
                             '| # | Claim | Surface | Check | Pass signal | Kind | Base |\n'
                             '|---|---|---|---|---|---|---|\n'
                             '| 1 | threshold | CLI | count | at least 255 of 300 | new | red |\n'
                             '| 2 | output | CLI | result | correct result | new | red |\n')
        self.commit('spec')
        self.changes = 0

    def commit(self, message):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-qm', message, '--allow-empty')
        return git(self.repo, 'rev-parse', 'HEAD')

    def code(self):
        self.changes += 1
        (self.repo / 'code.py').write_text('value = %d\n' % self.changes)
        return self.commit('code')

    def receipt(self, number, verdict='PROVED', defects='- none', sha=None):
        folder = self.folder / 'receipts'
        folder.mkdir(exist_ok=True)
        path = folder / ('check-%d.md' % number)
        sha = sha or git(self.repo, 'rev-parse', 'HEAD')
        path.write_text('# check-%d @ %s · fixture\n| # | Verdict | Evidence |\n'
                        '|---|---|---|\n| 1 | %s | observed |\n| 2 | PROVED | observed |\n\n## Defects\n%s\n\n'
                        '## Maybes\n- none\n' % (number, sha, verdict, defects))
        self.commit('receipt')

    def cli(self, *args, python=sys.executable, script=SCRIPT):
        return run(python, script, *args, '--repo', self.repo).stdout

    def next(self, *args):
        return json.loads(self.cli('next', 'demo', '--json', *args))


def states():
    with tempfile.TemporaryDirectory(prefix='jflow-states-') as temp:
        f = Fixture(Path(temp))
        checks = []

        def expect(step):
            n = f.next()
            assert n['step'] == step, n
            keys = {'schema_version', 'slug', 'step', 'n', 'role', 'model',
                    'command', 'session', 'blocker', 'why'}
            assert set(n) == keys and n['schema_version'] == 1, n
            if step not in ('human', None):
                seat = json.loads(f.cli('seat', step))
                assert n['model'] == {k: seat[k] for k in ('model', 'vendor', 'effort')}, n
                assert n['session'] == seat['session'] and n['role'] == seat['role'], n
            count = len(list(f.folder.glob('receipts/*.md')))
            assert n['n'] == (count + 1 if step == 'check' else count if step == 'fix' else None), n
            if step in ('check', 'fix'):
                session = 'builder session' if step == 'fix' else 'fresh'
                expected = 'Model: %s · %s. Session: %s.\n\n```text\n%s\n```\n' % (
                    n['model']['model'], n['model']['effort'], session, n['command'])
                assert f.cli('next', 'demo') == expected
            if step == 'fix':
                assert n['session'] == 'builder' and 'receipts/check-1.md' in n['command']
            checks.append(step)
            return n

        f.spec.unlink()
        expect('spec')
        f.spec.write_text('# demo\nStatus: drafting\nBase: ' + f.base + '\n')
        expect('spec')
        f.spec.write_text(f.spec.read_text().replace('drafting', 'ready'))
        f.commit('ready')
        expect('build')
        f.code()
        expect('check')
        assert f.next('--builder-vendor', 'openai')['model']['vendor'] == 'anthropic'
        f.receipt(1, 'BROKEN')
        expect('fix')
        f.receipt(1, 'PROVED', '- 1. code.py: caller sends x; observed bad result')
        expect('fix')
        for verdict, expected in [('BLOCKED', 'human'), ('UNREACHABLE', 'human'), ('WAITING', 'live')]:
            f.receipt(1, verdict)
            n = expect(expected)
            if expected == 'human':
                assert n['role'] == 'human' and n['blocker']
        (f.folder / 'notes.md').write_text('Live done: fixture\n')
        expect('check')
        f.receipt(1)
        expect('done')
        (f.folder / 'notes.md').write_text('receipt-only edit\n')
        f.commit('notes')
        expect('done')
        f.code()
        expect('check')
        f.spec.write_text(f.spec.read_text().replace('ready', 'done'))
        assert expect(None)['command'] is None
        before = git(f.repo, 'status', '--porcelain')
        out = run(sys.executable, SCRIPT, 'next', '../x', '--repo', f.repo, check=False)
        assert out.returncode and 'bad slug' in out.stderr
        assert before == git(f.repo, 'status', '--porcelain')
        print('Rows 2,3,5,6,7,8: PASS; %d states, shape, cards, vendor, slug, code-only changes' % len(checks))


def cap():
    with tempfile.TemporaryDirectory(prefix='jflow-cap-') as temp:
        f = Fixture(Path(temp))
        for number in range(1, 4):
            f.code()
            f.receipt(number, 'BROKEN')
        n = f.next()
        assert n['role'] == 'human' and '3 checks used of 3' in n['blocker'], n
        f.receipt(4, 'BROKEN')
        assert '3 checks used of 3' in f.next()['blocker']
        (f.folder / 'notes.md').write_text('Checks allowed: 5\n')
        f.commit('allow')
        assert f.next()['step'] == 'fix'
        print('Row 4: PASS; cap 3, rerun stays 3, allowance 5 gives fix')


def history():
    count = 0
    with tempfile.TemporaryDirectory(prefix='jflow-history-') as temp:
        mirror = Path(temp) / 'mirror'
        run('git', 'clone', '--shared', '--no-checkout', '-q', ROOT, mirror)
        tree = Path(temp) / 'tree'
        git(mirror, 'worktree', 'add', '--detach', '-q', tree, 'HEAD')
        try:
            for slug in ('drive-py-at-done', 'receipt-evidence-cap', 'jflow-config'):
                folder = '.jflow/' + slug
                commits = git(ROOT, 'log', '--reverse', '--format=%H', '--', folder).splitlines()
                steps = []
                for sha in commits:
                    subject = git(ROOT, 'show', '-s', '--format=%s', sha)
                    steps.append(subject.split()[1])
                for i, sha in enumerate(commits):
                    git(tree, 'checkout', '--detach', '-q', sha)
                    actual = json.loads(run(sys.executable, SCRIPT, 'next', slug, '--json', '--repo', tree).stdout)
                    expected = steps[i + 1] if i + 1 < len(steps) else None
                    if slug == 'jflow-config' and commits.index(next(c for c in commits if c.startswith('3775002'))) <= i <= commits.index(next(c for c in commits if c.startswith('1f0389c'))):
                        assert actual['role'] == 'human' and actual['blocker'], (sha, actual)
                    else:
                        assert actual['step'] == expected, (slug, sha, expected, actual)
                    count += 1
        finally:
            git(mirror, 'worktree', 'remove', '--force', tree)
    print('Row 1: PASS; %d historical run commits, cap interval and final done states' % count)


def compat():
    python = shutil.which('python3.9')
    if not python:
        found = list((Path.home() / '.local/share/uv/python').glob('cpython-3.9*/bin/python3.9'))
        assert found, 'Python 3.9 required'
        python = str(found[0])
    tests = run(python, '-m', 'unittest', 'discover', '-s', '.github/skills/jflow/scripts/tests')
    assert 'Ran 17 tests' in tests.stderr and '\nOK\n' in tests.stderr, tests.stderr
    with tempfile.TemporaryDirectory(prefix='jflow-compat-') as temp:
        repo = Path(temp) / 'repo'
        repo.mkdir()
        f = Fixture(repo)
        assert json.loads(f.cli('next', 'demo', '--json', python=python))['step'] == 'build'
        baseline = Path(temp) / 'base'
        baseline.mkdir()
        (baseline / 'scripts').mkdir()
        for file in ('scripts/jflow.py', 'config.json', 'flow.json'):
            (baseline / file).write_text(git(ROOT, 'show', BASE + ':.github/skills/jflow/' + file) + '\n')
        for args in [('summary', 'jflow-config', '--json'), ('seat', 'check'), ('seat', 'check', '--builder-vendor', 'openai')]:
            old = run(python, baseline / 'scripts/jflow.py', *args).stdout
            new = run(python, SCRIPT, *args).stdout
            assert old == new, (args, old, new)
    print('Row 10: PASS; Python 3.9, 17 tests OK, next runs, 3 outputs byte-identical to Base')


def docs():
    folder = SCRIPT.parents[1]
    first = run('grep', '-n', 'What is next\\|^\\| no `spec.md`', 'SKILL.md', cwd=folder, check=False)
    print('First literal spec grep exits %d; its empty alternative matches every line.' % first.returncode)
    assert '## What is next' not in (folder / 'SKILL.md').read_text()
    assert '| State | Next |' not in (folder / 'SKILL.md').read_text()
    files = [folder / 'SKILL.md'] + sorted((folder / 'references').glob('*.md'))
    second = run('grep', '-n', 'jflow.py next', *files).stdout
    print(second.replace(str(folder) + '/', ''), end='')
    for name in ('SKILL.md', 'references/spec.md', 'references/build.md', 'references/check.md'):
        assert 'jflow.py next' in (folder / name).read_text(), name
    print('Row 9: PASS; table removed; hub, spec, build, fix, live, check call next; done closes without a card')


def budget():
    lines = git(ROOT, 'diff', '--numstat', BASE, '--', str(SCRIPT), str(SCRIPT.parent / 'tests')).splitlines()
    growth = {}
    for line in lines:
        added, deleted, name = line.split('\t')
        growth[name] = int(added) - int(deleted)
    code = growth[str(SCRIPT.relative_to(ROOT))]
    tests = sum(v for k, v in growth.items() if '/tests/' in k)
    folder = SCRIPT.parents[1]
    files = [folder / name for name in ('SKILL.md', 'flow.json', 'config.json', 'scripts/jflow.py')]
    files += [p for p in (folder / 'references').rglob('*') if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    assert code <= 150 and tests <= code and size <= 50000, (code, tests, size)
    print('Row 11: PASS; script +%d, tests +%d, agent files %d bytes' % (code, tests, size))


def attack():
    with tempfile.TemporaryDirectory(prefix='jflow-attack-') as temp:
        f = Fixture(Path(temp))
        old = f.code()
        f.receipt(1, 'BROKEN')
        receipt = f.folder / 'receipts/check-1.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 254 of 300 |'))
        f.commit('describe accepted miss')
        accepted = '\n## Accepted\n- Row 1 · 254 of 300 against a bar of 255 · "accept 254" · 2026-11-09 · ' + old + '\n'
        f.spec.write_text(f.spec.read_text() + accepted)
        f.commit('accept old miss')
        assert f.next()['step'] == 'done'
        f.code()
        assert f.next()['step'] == 'check'
        f.receipt(2, 'BROKEN')
        receipt = f.folder / 'receipts/check-2.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 0 of 300 |'))
        f.commit('describe different miss')
        print('Attack accepted-old-row: latest row BROKEN at new code, old acceptance; next=' + f.next()['step'] + '; expected=fix')
        assert f.next()['step'] == 'fix'
    with tempfile.TemporaryDirectory(prefix='jflow-attack-') as temp:
        f = Fixture(Path(temp))
        sha = f.code()
        f.receipt(1, 'BROKEN')
        receipt = f.folder / 'receipts/check-1.md'
        receipt.write_text(receipt.read_text().replace('| 2 | PROVED |', '| 2 | BROKEN |'))
        f.spec.write_text(f.spec.read_text() + '\n## Accepted\n- Row 1 · missed threshold · "Accept Row 1; Row 2 must be fixed" · 2026-11-09 · ' + sha + '\n')
        f.commit('accept row one only')
        print('Attack quoted-row-reference: only Row 1 accepted, Row 2 BROKEN; next=' + f.next()['step'] + '; expected=fix')
        assert f.next()['step'] == 'fix'
    with tempfile.TemporaryDirectory(prefix='jflow-attack-') as temp:
        f = Fixture(Path(temp))
        f.spec.write_text(f.spec.read_text().replace('| new | red |', '| keep | green |', 1)
                          .replace('| 2 | output | CLI | result | correct result | new | red |',
                                   '| 2 | live data | CLI | update | data updated | live | red |'))
        sha = f.code()
        f.receipt(1, 'BROKEN', sha=sha)
        receipt = f.folder / 'receipts/check-1.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 254 of 300 |')
                           .replace('| 2 | PROVED |', '| 2 | WAITING |'))
        f.spec.write_text(f.spec.read_text() + '\n## Accepted\n- Row 1 · 254 of 300 against a bar of 255 · "accept 254" · 2026-11-09 · ' + sha + '\n')
        f.commit('accept current miss before live steps')
        assert f.next()['step'] == 'live'
        (f.folder / 'notes.md').write_text('Live done: live data updated\n')
        f.commit('live data updated without code change')
        assert f.next()['step'] == 'check'
        f.receipt(2, 'BROKEN', sha=sha)
        receipt = f.folder / 'receipts/check-2.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 0 of 300 after live data update |'))
        f.commit('different miss at unchanged code')
        print('Attack accepted-new-miss-same-sha: after live data update, Row 1 BROKEN at 0 of 300; next=' + f.next()['step'] + '; expected=fix')
        assert f.next()['step'] == 'fix'


def acceptance_edges():
    failures = []
    with tempfile.TemporaryDirectory(prefix='jflow-acceptance-') as temp:
        f = Fixture(Path(temp))
        sha = f.code()
        f.receipt(1, 'BROKEN', sha=sha)
        receipt = f.folder / 'receipts/check-1.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 254 of 300 |')
                           .replace('| 2 | PROVED |', '| 2 | BLOCKED |'))
        f.commit('row two needs a service')
        f.spec.write_text(f.spec.read_text() + '\n## Accepted\n- Row 1 · 254 of 300 against a bar of 255 · "accept 254" · 2026-11-09 · ' + sha + '\n')
        f.commit('accept row one while row two is blocked')
        assert f.next()['step'] == 'human'
        f.receipt(2, 'BROKEN', sha=sha)
        receipt = f.folder / 'receipts/check-2.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | carried from check-1 |'))
        f.commit('rerun only blocked row two after service returns')
        actual = f.next()['step']
        print('Attack accepted-carried-row: check-2 carries accepted Row 1, proves Row 2; next=' + actual + '; expected=done')
        if actual != 'done':
            failures.append('accepted-carried-row')
    with tempfile.TemporaryDirectory(prefix='jflow-acceptance-') as temp:
        f = Fixture(Path(temp))
        old = f.code()
        f.receipt(1, 'BROKEN', sha=old)
        receipt = f.folder / 'receipts/check-1.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 254 of 300 |'))
        f.commit('describe old miss')
        f.code()
        f.receipt(2, 'BROKEN')
        receipt = f.folder / 'receipts/check-2.md'
        receipt.write_text(receipt.read_text().replace('| BROKEN | observed |', '| BROKEN | 0 of 300 |'))
        f.commit('describe new miss')
        f.spec.write_text(f.spec.read_text() + '\n## Accepted\n- Row 1 · 254 of 300 against a bar of 255 · "accept the old 254 result" · 2026-11-09 · ' + old + '\n')
        f.commit('accept only the old code result')
        actual = f.next()['step']
        print('Attack acceptance-other-sha: acceptance names old code, newest Row 1 BROKEN at 0 of 300; next=' + actual + '; expected=fix')
        if actual != 'fix':
            failures.append('acceptance-other-sha')
    assert not failures, failures


def carry_chain():
    with tempfile.TemporaryDirectory(prefix='jflow-carry-') as temp:
        f = Fixture(Path(temp))
        sha = f.code()
        f.receipt(1, 'BROKEN', '- 1. code.py: caller sends x; observed crash', sha)
        f.spec.write_text(f.spec.read_text() + '\n## Accepted\n'
                          '- Row 1 · threshold miss · "accept it" · 2026-11-09 · ' + sha + '\n'
                          '- Defect 1 · crash · "accept it" · 2026-11-09 · ' + sha + '\n')
        f.commit('accept row and defect')
        assert f.next()['step'] == 'done'
        for number in (2, 3):
            carried = 'carried from check-%d' % (number - 1)
            f.receipt(number, 'BROKEN', '- 1. code.py: caller sends x; ' + carried, sha)
            receipt = f.folder / ('receipts/check-%d.md' % number)
            receipt.write_text(receipt.read_text().replace('| BROKEN | observed |',
                                                          '| BROKEN | ' + carried + ' |'))
            f.commit('carry row and defect')
            assert f.next()['step'] == 'done'
        print('Attack carried-chain: accepted row and defect survive two carried receipts; next=done; expected=done')
        f.receipt(4, 'BROKEN', '- 1. code.py: caller sends y; observed new crash', sha)
        assert f.next()['step'] == 'fix'
        print('Attack fresh-after-chain: new row and defect at unchanged code stay open; next=fix; expected=fix')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('states', 'cap', 'history', 'compat', 'docs', 'budget', 'attack', 'acceptance_edges', 'carry_chain'))
    args = parser.parse_args()
    globals()[args.action]()
