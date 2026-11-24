#!/usr/bin/env python3
"""Reproduce delete-workflow proof rows using disposable local repositories."""
import argparse
import os
from pathlib import Path
import random
import re
import shutil
import string
import subprocess
import sys
import tempfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
BASE = 'f2137fb'
HOOK = ROOT / '.github/skills/jflow/scripts/hooks.py'
TRIALS = ROOT / '.github/skills/checkup/scripts/skill-trials.py'


def run(*args, cwd=ROOT, env=None, expected=0):
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    if expected is not None and result.returncode != expected:
        raise AssertionError(f'{args}: exit {result.returncode}\n{result.stdout}{result.stderr}')
    return result


def isolated(folder):
    home = folder / 'home'
    home.mkdir()
    return {**os.environ, 'HOME': str(home), 'CODEX_HOME': str(home / '.codex'),
            'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}


def repo(folder, env):
    folder.mkdir()
    run('git', 'init', '-q', cwd=folder, env=env)
    run('git', 'config', 'user.name', 'Fixture', cwd=folder, env=env)
    run('git', 'config', 'user.email', 'fixture@example.invalid', cwd=folder, env=env)
    return folder


def row1():
    assert not (ROOT / '.github/skills/workflow').exists()
    assert not (ROOT / 'skills/workflow').is_symlink()
    result = run('grep', '-rnwi', 'workflow', '.github/skills', 'skills', 'README.md',
                 'AGENTS.md', '.claude-plugin/plugin.json', '--exclude=triggers.tsv', expected=None)
    lines = result.stdout.splitlines()
    history = [line for line in lines if '/SKILL-IMPACT' in line]
    assert history, 'Inspect remaining matches manually'
    print(f'row 1: folders gone; grep finds {len(history)} ledger matches naming retired skill/files')


def row2():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        env = isolated(folder)
        work = repo(folder / 'repo', env)
        remote = folder / 'remote.git'
        run('git', 'init', '-q', '--bare', str(remote), env=env)
        run('git', 'remote', 'add', 'origin', str(remote), cwd=work, env=env)
        run(sys.executable, str(HOOK), 'install', cwd=work, env=env)
        rng = random.Random(731)
        key = 'AK' + 'IA' + ''.join(rng.choices(string.ascii_uppercase + '234567', k=16))
        (work / 'fixture.txt').write_text('aws_access_key_id = ' + key + '\n')
        run('git', 'add', '.', cwd=work, env=env)
        run('git', 'commit', '-qm', 'fixture', cwd=work, env=env)
        result = run('git', 'push', 'origin', 'HEAD:refs/heads/secret', cwd=work, env=env, expected=None)
        assert result.returncode and re.search(r'RuleID:\s+aws-access-token', result.stdout + result.stderr), result.stdout + result.stderr
        assert key not in result.stdout + result.stderr
        run('git', 'checkout', '--orphan', 'clean', cwd=work, env=env)
        run('git', 'rm', '-qf', 'fixture.txt', cwd=work, env=env)
        (work / 'clean.txt').write_text('clean\n')
        run('git', 'add', '.', cwd=work, env=env)
        run('git', 'commit', '-qm', 'clean', cwd=work, env=env)
        run('git', 'push', 'origin', 'HEAD:refs/heads/clean', cwd=work, env=env)
        minimal = folder / 'bin'
        minimal.mkdir()
        for name in ('git', 'python3', 'sh'):
            (minimal / name).symlink_to(shutil.which(name))
        result = run('git', 'push', 'origin', 'HEAD:refs/heads/no-scanner', cwd=work,
                     env={**env, 'PATH': str(minimal)}, expected=None)
        assert result.returncode and 'install gitleaks' in result.stderr
    print('row 2: AWS secret blocked with finding; clean push succeeds; missing gitleaks blocks')


def row3():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        env = isolated(folder)
        a, b, c = [repo(folder / name, env) for name in ('a', 'b', 'c')]
        old = folder / 'old-hooks.py'
        old.write_text(run('git', 'show', BASE + ':.github/skills/workflow/scripts/hooks.py').stdout)
        run(sys.executable, str(old), 'install', cwd=a, env=env)
        assert (a / '.git/hooks/pre-commit').exists()
        run(sys.executable, str(HOOK), 'install', cwd=a, env=env)
        assert 'skills/workflow' not in (a / '.git/hooks/pre-push').read_text()
        assert not (a / '.git/hooks/pre-commit').exists()
        foreign = b / '.git/hooks/pre-push'
        foreign.write_text('#!/bin/sh\n# foreign\nexit 0\n')
        before = foreign.read_bytes()
        run(sys.executable, str(HOOK), 'install', cwd=b, env=env, expected=1)
        assert foreign.read_bytes() == before
        run('git', 'config', 'core.hooksPath', 'custom', cwd=c, env=env)
        run(sys.executable, str(HOOK), 'install', cwd=c, env=env, expected=1)
        assert not (c / 'custom').exists()
    print('row 3: actual old stubs upgraded; pre-commit removed; foreign hook and hooksPath refused')


def row4():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for name in ('SKILL-IMPACT.md', 'SKILL-IMPACT_ARCHIVE.md'):
            content = run('git', 'show', BASE + ':.github/skills/workflow/' + name).stdout
            (folder / name).write_text(content)
            assert content == (ROOT / '.github/skills/checkup' / name).read_text()
        current = run(sys.executable, str(TRIALS), '--sweep').stdout
        old = run(sys.executable, str(TRIALS), '--sweep', '--impact', str(folder / 'SKILL-IMPACT.md')).stdout
        assert current == old
    print(f'row 4: both ledgers byte-identical; default sweep equals old impact ({len(current.splitlines())} lines)')


def row5():
    names = ['checkup/references/seats.md', 'checkup/references/report.md',
             'agent-docs/SKILL.md', 'design/SKILL.md', 'evals/SKILL.md']
    for name in names:
        text = (ROOT / '.github/skills' / name).read_text()
        assert re.search(r'jflow\.py\s+seat|config\.json', text), name
        assert 'ROUTING.md' not in text, name
    assert 'jflow/references/check.md' in (ROOT / '.github/skills/evals/SKILL.md').read_text()
    print('row 5: all five seat readers match jflow; evals names check.md; no ROUTING.md')


def row6():
    for name in ('retro', 'understand', 'memory.compact', 'memory.remember', 'plain'):
        files = [p for p in (ROOT / '.github/skills' / name).rglob('*') if p.is_file() and p.suffix in ('.md', '.py', '.tsv')]
        text = '\n'.join(p.read_text() for p in files)
        assert '.workflow' not in text, name
        assert '.jflow' in text, name
    text = (ROOT / '.github/skills/checkup/references/workspace.md').read_text()
    assert '.workflow' not in text and '.jflow' in text
    print('row 6: all six readers contain .jflow and zero .workflow references')


def row7():
    readme = (ROOT / 'README.md').read_text()
    first = re.search(r'```[^\n]*\n([^\n]+)', readme)[1]
    assert first.startswith('jflow spec '), first
    links = 0
    for name in ('README.md', 'AGENTS.md'):
        path = ROOT / name
        for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', path.read_text()):
            if re.match(r'[a-zA-Z]+:|#', target):
                continue
            assert (path.parent / unquote(target.split('#')[0])).exists(), (name, target)
            links += 1
    agents = (ROOT / 'AGENTS.md').read_text()
    assert len(re.findall(r'python3 -m unittest discover', agents)) == 3
    print(f'row 7: first command is jflow spec; {links} relative links resolve; AGENTS names three suites')


def attack_trials():
    import runpy
    trials = runpy.run_path(str(TRIALS))
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        impact = folder / 'impact.md'
        impact.write_text('| 2026-11-10 | jflow | Fixture change | fixture | 1 runs | trialing |\n')
        # Each entry has exactly the shape required by jflow/references/done.md.
        (folder / 'WORKLOG.md').write_text(
            '## 2026-11-11 · after · shipped fixture · builder\n'
            '- Changed fixture.\n- Commits: abcdef0\n'
            '- jflow: 3 sessions · 0 fix rounds · 1 rows · 0 accepted · check clean'
            ' · net code +1 · tests +0 · docs +0\n'
            '## 2026-11-09 · before · shipped fixture · builder\n'
            '- Changed fixture.\n- Commits: abcdef1\n'
            '- jflow: 5 sessions · 1 fix rounds · 1 rows · 0 accepted · check 1 defects'
            ' · net code +1 · tests +0 · docs +0\n')
        entries = trials['worklogs']([folder])
        report = run(sys.executable, str(TRIALS), '--impact', str(impact), str(folder)).stdout
        sweep = run(sys.executable, str(TRIALS), '--sweep', '--impact', str(impact), str(folder)).stdout
        assert entries == [('2026-11-09', ['jflow'], 2),
                           ('2026-11-11', ['jflow'], 0)], entries
        assert 'trial complete' in report and 'numbers better (before 2.0 → after 0.0)' in report, report
        assert 'keep' in sweep and 'numbers better' in sweep, sweep
        # Clean checks can follow fix rounds; both quantities still count separately.
        for check, rounds, score in [('clean', 0, 0), ('clean', 2, 2),
                                     ('0 defects', 0, 0), ('3 defects', 2, 5)]:
            (folder / 'WORKLOG.md').write_text(
                '## 2026-11-11 · fixture · shipped fixture · builder\n'
                f'- jflow: 3 sessions · {rounds} fix rounds · 1 rows · 0 accepted · check {check}'
                ' · net code +1 · tests +0 · docs +0\n')
            assert trials['worklogs']([folder]) == [('2026-11-11', ['jflow'], score)]
        print('attack trials: clean and numeric checks recognized; fix rounds retained; completed trial reports before 2.0 → after 0.0')


def attack_design():
    import json
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / 'config.json'
        config.write_text(json.dumps({'schema_version': 1, 'seats': {'build': {
            'model': 'gpt-6.2-sol', 'vendor': 'openai', 'effort': 'high', 'fallback': None}}}))
        seat = json.loads(run(sys.executable, str(ROOT / '.github/skills/jflow/scripts/jflow.py'),
                              'seat', 'build', '--config', str(config)).stdout)
        checker = json.loads(run(sys.executable, str(ROOT / '.github/skills/jflow/scripts/jflow.py'),
                                 'seat', 'check', '--config', str(config)).stdout)
        instructions = (ROOT / '.github/skills/design/SKILL.md').read_text()
        assert seat['vendor'] == 'openai'
        assert checker['vendor'] != seat['vendor']
        assert 'When the design seat is OpenAI' in instructions
        assert 'use `jflow.py seat check`' in instructions
        print('attack design: OpenAI build override selects Anthropic fresh eyes through jflow check seat')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('row', choices=[str(n) for n in range(1, 8)] + ['attack-trials', 'attack-design'])
    args = parser.parse_args()
    if args.row == 'attack-trials':
        attack_trials()
    elif args.row == 'attack-design':
        attack_design()
    else:
        globals()[f'row{args.row}']()
