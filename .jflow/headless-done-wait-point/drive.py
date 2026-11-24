import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.github/skills/jflow/scripts/tests'))
from test_github import GitHubMode
from test_jflow import RunRecord


EDITS = '## Proposed edits\n- PRODUCT.md: mark the outcome reached\n- TODO.md: remove the demo item\n'
YES_DONE = 'Yes: done · "yes" · 2026-11-24\n'
YES_EDITS = 'Yes: edits · "yes" · 2026-11-24\n'


def expect(result, step, wait_point=None):
    assert result['step'] == step, result
    if wait_point:
        assert result['wait_point'] == wait_point, result
    else:
        assert 'wait_point' not in result, result
    if step == 'human':
        assert result['role'] == 'human', result
    if step == 'done':
        assert result['session'] == 'builder', result


def local_edits(run):
    run.state('PROVED', code=True)
    notes = run.run_dir / 'notes.md'
    notes.write_text(EDITS)
    run.commit('propose edits')
    stop = run.next()
    expect(stop, 'human', 'edits')
    assert all(line in stop['blocker'] for line in EDITS.splitlines()[1:]), stop
    notes.write_text(EDITS + YES_EDITS)
    run.commit('approve edits')
    expect(run.next(), 'done')
    print('edits shows both proposed lines, then done in the builder session')


def all_wait_points(run):
    spec, notes = run.run_dir / 'spec.md', run.run_dir / 'notes.md'
    start = run.git('rev-parse', 'HEAD')
    cases = [
        ('- Gate: none.\n- Ask first: config shape.', '- none', '## Approach\n- A new setting\n',
         None, '- none', 'human', 'approach', 'config shape'),
        ('- Gate: release.', '- none', '', 'WAITING', '- none', 'human', 'gate', 'release'),
        ('- Gate: none.', '- Try the CLI.', '', 'PROVED', '- none', 'human', 'done', 'Try the CLI'),
        ('- Gate: none.', '- none', EDITS, 'PROVED', '- none', 'human', 'edits', 'PRODUCT.md'),
        ('- Gate: none.', '- none', 'Checks allowed: 1\n', 'BROKEN', '- none', 'human', None, '1 checks used of 1'),
        ('- Gate: none.', '- none', '', 'BLOCKED', '- none', 'human', None, 'Row 1, BLOCKED'),
        ('- Gate: none.', '- none', '', 'PROVED', '- 1. [edge] app.py: odd input', 'human', None, 'defect 1'),
        ('- Gate: none.', '- none', '', None, '- none', 'build', None, None),
    ]
    for gate, human, note, verdict, defects, step, wait_point, blocker in cases:
        run.git('reset', '--hard', start)
        (run.run_dir / 'receipts').mkdir(exist_ok=True)
        spec.write_text(spec.read_text().replace('- Gate: none.', gate).replace('## Human checks\n- none', f'## Human checks\n{human}'))
        notes.write_text(note)
        run.commit('configure fixture')
        if verdict:
            run.state(verdict, defects, code=True)
        result = run.next()
        expect(result, step, wait_point)
        if blocker:
            assert blocker in result['blocker'], result
    print('approach, gate, done and edits typed. Cap, BLOCKED, edge-only and build omit wait_point')


def independent_approvals(run):
    spec, notes = run.run_dir / 'spec.md', run.run_dir / 'notes.md'
    spec.write_text(spec.read_text().replace('## Human checks\n- none', '## Human checks\n- Try the CLI.'))
    run.commit('add Human check')
    run.state('PROVED', code=True)
    for approval, expected in [(YES_DONE, 'edits'), (YES_EDITS, 'done')]:
        notes.write_text(EDITS + approval)
        run.commit('approve one wait point')
        expect(run.next(), 'human', expected)
    spec.write_text(spec.read_text().replace('1. Prove the run.', '1. Prove the revised run.'))
    run.commit('revise spec')
    (run.repo / 'app.py').write_text('a = 2\n')
    run.commit('rebuild')
    run.receipt(2, 'PROVED', '- none')
    run.commit('re-prove')
    expect(run.next(), 'human', 'done')
    notes.write_text(notes.read_text() + YES_DONE)
    run.commit('approve revised Human check')
    expect(run.next(), 'done')
    notes.write_text(notes.read_text() + '\n## Proposed edits\n- DESIGN.md: add a new rule\n')
    run.commit('propose new edits')
    expect(run.next(), 'human', 'edits')
    print('approvals are independent. Re-spec drops old edits and requires fresh approval for new edits')


def github_edits(run):
    run.checked_run()
    run.ok('note', '#42', '--file', run.file('proposed.md', EDITS))
    expect(run.next(), 'human', 'edits')
    run.ok('note', '#42', '--file', run.file('approval.md', YES_EDITS))
    expect(run.next(), 'done')
    print('stub gh routes edits to the human, then done in the builder session')


def replace_after_respec(run):
    spec, notes = run.run_dir / 'spec.md', run.run_dir / 'notes.md'
    notes.write_text(EDITS + YES_EDITS)
    run.commit('approve first proposal')
    run.state('PROVED', code=True)
    spec.write_text(spec.read_text().replace('1. Prove the run.', '1. Prove the revised run.'))
    run.commit('revise spec')
    (run.repo / 'app.py').write_text('a = 2\n')
    run.commit('rebuild')
    run.receipt(2, 'PROVED', '- none')
    run.commit('re-prove')
    expect(run.next(), 'done')
    notes.write_text('## Proposed edits\n- DESIGN.md: add the revised rule\n')
    run.commit('replace the old proposal in notes')
    result = run.next()
    print(f'Replacement after re-spec returned {result["step"]} with wait_point={result.get("wait_point")}')
    expect(result, 'human', 'edits')


def uncommitted_approval(run):
    run.state('PROVED', code=True)
    notes = run.run_dir / 'notes.md'
    notes.write_text(EDITS)
    run.commit('propose edits')
    expect(run.next(), 'human', 'edits')
    notes.write_text(EDITS + YES_EDITS)
    assert run.git('status', '--porcelain', '--', str(notes)).startswith('M .jflow/')
    result = run.next()
    print(f'Uncommitted approval returned {result["step"]} with wait_point={result.get("wait_point")}')
    expect(result, 'human', 'edits')


def github_replacement(run):
    run.checked_run()
    run.ok('note', '#42', '--file', run.file('initial.md', EDITS))
    revised = '## Proposed edits\n- TODO.md: keep the demo item and mark it finished\n'
    run.ok('note', '#42', '--file', run.file('revised.md', revised))
    result = run.next()
    expect(result, 'human', 'edits')
    shown = [line for line in result['blocker'].splitlines() if line.startswith('- ')]
    print('GitHub blocker shows ' + ', '.join(shown), flush=True)
    assert shown == revised.splitlines()[1:], result


def github_done_instructions(run):
    run.checked_run()
    notes = run.repo / '.jflow' / '42' / 'notes.md'
    notes.parent.mkdir(parents=True)
    notes.write_text(EDITS)
    run.git(run.repo, 'add', '.jflow/42/notes.md')
    run.git(run.repo, 'commit', '-qm', 'propose edits')
    result = run.run_jflow('next', '#42', '--json')
    print(result.stderr.strip(), flush=True)
    assert result.returncode == 0, result.stderr


if __name__ == '__main__':
    scenarios = {
        '1': local_edits, '2': all_wait_points, '3': independent_approvals, '4': github_edits,
        'replace-after-respec': replace_after_respec,
        'uncommitted-approval': uncommitted_approval,
        'github-replacement': github_replacement,
        'github-done-instructions': github_done_instructions,
    }
    row = sys.argv[1]
    fixture = GitHubMode() if row == '4' or row.startswith('github-') else RunRecord()
    fixture.setUp()
    try:
        scenarios[row](fixture)
    finally:
        fixture.tearDown()
        fixture.doCleanups()
