"""Checker's CLI probes. All mutations stay in temporary fixture repositories."""
import ast
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST = ROOT / '.github/skills/jflow/scripts/tests/test_github.py'
spec = importlib.util.spec_from_file_location('fixtures', TEST)
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


def fixture():
    case = fixtures.GitHubMode()
    case.setUp()
    return case


def start(case, text=None):
    case.record('spec', '--file', case.file('spec.md', text or case.spec()))
    case.open_pr()
    sha = case.code()
    case.record('check', '--file', case.file('r1.md', fixtures.receipt(1, sha)))


def attack(name):
    c = fixture()
    try:
        start(c, c.spec(human='- trial') if name == 'member-approval' else None)
        if name == 'respec':
            changed = c.spec().replace('| 1 | a |', '| 1 | changed claim |')
            c.record('spec', '--file', c.file('spec2.md', changed))
            print('respec: next=' + c.next()['step'])
        elif name == 'delete-spec':
            state = c.load()
            state['comments']['42'] = state['comments']['42'][1:]
            c.save(state)
            p = c.run_jflow('next', '#42', '--json')
            print(f'delete-spec: exit={p.returncode}; {p.stdout.strip() or p.stderr.strip()}')
        elif name == 'unrecorded-spec':
            state = c.load()
            state['comments']['42'] = state['comments']['42'][:1]
            c.save(state)
            print('unrecorded-spec: next=' + c.next()['step'])
        elif name == 'deleted-receipt':
            state = c.load()
            state['comments']['7'] = [x for x in state['comments']['7'] if 'jflow:receipt ' not in x['body']]
            c.save(state)
            print('deleted-receipt: next=' + str(c.next()['step']))
        elif name == 'edit-receipt':
            state = c.load()
            state['comments']['7'][0]['body'] = state['comments']['7'][0]['body'].replace('PROVED', 'BROKEN')
            c.save(state)
            print('edit-receipt: next=' + c.next()['step'])
        elif name == 'strip-spec-marker':
            state = c.load()
            state['comments']['42'][0]['body'] = state['comments']['42'][0]['body'].split('\n', 1)[1]
            c.save(state)
            p = c.run_jflow('next', '#42', '--json')
            print(f'strip-spec-marker: exit={p.returncode}; {p.stdout.strip() or p.stderr.strip()}')
        elif name == 'respec-after-done':
            c.record('done')
            changed = c.spec().replace('| 1 | a |', '| 1 | changed claim |')
            c.record('spec', '--file', c.file('spec2.md', changed))
            n = c.next()
            print(f'respec-after-done: step={n["step"]}; why={n["why"]}')
        elif name == 'respec-summary':
            c.record('done')
            changed = c.spec().replace('| 1 | a |', '| 1 | changed claim |')
            c.record('spec', '--file', c.file('spec2.md', changed))
            sha = c.code(text='x = 2\n')
            c.record('check', '--file', c.file('r2.md', fixtures.receipt(2, sha)))
            c.record('done')
            summary = json.loads(c.ok('summary', '#42', '--json'))
            added, deleted, _ = c.git(c.repo, 'diff', '--numstat', c.base + '..HEAD', '--', 'app.py').split('\t')
            print(f'respec-summary: net_code={summary["net_code"]}; actual diff={added} added, {deleted} deleted; checks={summary["checks"]}')
        elif name == 'summary-cycles':
            c.record('done')
            expected_lines = 1
            for n, add_code in ((2, False), (3, True), (4, True)):
                revised = c.spec().replace('| 1 | a |', f'| 1 | revision {n} |')
                c.record('spec', '--file', c.file(f'spec{n}.md', revised))
                decision = c.next()
                assert (decision['step'], decision['n']) == ('check', n), decision
                if add_code:
                    c.code(text=f'x = {n}\n')
                    expected_lines += 1
                active = json.loads(c.ok('summary', '#42', '--json'))
                assert active['net_code'] == expected_lines, active
                c.record('check', '--file', c.file(f'r{n}.md', fixtures.receipt(n, c.head())))
                assert c.next()['step'] == 'done', c.next()
                c.record('done')
                finished = json.loads(c.ok('summary', '#42', '--json'))
                assert (finished['net_code'], finished['checks']) == (expected_lines, n), finished
                state = c.load()
                last = json.loads(state['comments']['7'][-1]['body'].split('```json\n')[1].split('\n```')[0])
                assert last['summary']['net_code'] == expected_lines, last
            c.code(text='x = 99\n')
            frozen = json.loads(c.ok('summary', '#42', '--json'))
            assert frozen['net_code'] == expected_lines, frozen
            print('summary-cycles: 4 checks; no-code and code revisions, active/final/recorded totals and post-done cutoff OK')
        elif name == 'replaced-fork-pr':
            stub = (c.bin / 'gh').read_text().replace(
                '"head": {"ref": p["head"]}',
                '"head": {"ref": p["head"]}, "state": p.get("state", "open"), "draft": True')
            (c.bin / 'gh').write_text(stub)
            state = c.load()
            state['pulls'] = [
                {'number': 7, 'head': 'jflow/42', 'owner': 'fork', 'state': 'closed'},
                {'number': 8, 'head': 'jflow/42', 'owner': 'fork', 'state': 'open'},
            ]
            state['timeline'] = {'42': [
                {'event': 'cross-referenced', 'source': {'issue': {
                    'number': n, 'pull_request': {}, 'repository': {'full_name': 'o/r'}}}}
                for n in (7, 8)
            ]}
            c.save(state)
            c.ok('note', '#42', '--file', c.file('note.md', 'current run note\n'))
            state = c.load()
            targets = [n for n, comments in state['comments'].items()
                       if any('current run note' in item['body'] for item in comments)]
            print('replaced-fork-pr: note posted to PR #' + ','.join(targets) + '; open run PR #8')
        elif name == 'member-approval':
            print('member-approval: before=' + str(c.next()['role']))
            c.post(7, 'notes', 'Yes: done · "sure" · 2026-11-23\n')
            state = c.load()
            state['comments']['7'][-1]['author_association'] = 'MEMBER'
            c.save(state)
            print('member-approval: after=' + c.next()['step'] + '; association=MEMBER; permission not queried')
        elif name == 'fork-pr':
            stub = (c.bin / 'gh').read_text().replace('s["nwo"].split("/")[0] + ":" + p["head"]', 'p.get("owner", s["nwo"].split("/")[0]) + ":" + p["head"]')
            (c.bin / 'gh').write_text(stub)
            state = c.load()
            state['pulls'][0]['owner'] = 'fork-owner'
            c.save(state)
            p = c.run_jflow('next', '#42', '--json')
            print(f'fork-pr: exit={p.returncode}; {p.stderr.strip()}')
        elif name == 'repo-option':
            stub = (c.bin / 'gh').read_text().replace('state_path = os.environ["GH_STUB"]',
                'if "{owner}/{repo}" in sys.argv[2] and not os.path.isdir(".git"):\n'
                '    sys.exit(print("cannot infer repository from cwd", file=sys.stderr) or 1)\n'
                'state_path = os.environ["GH_STUB"]')
            (c.bin / 'gh').write_text(stub)
            p = c.run_jflow('next', '#42', '--json', '--repo', str(c.repo), repo=c.tmp)
            print(f'repo-option: exit={p.returncode}; {p.stderr.strip()}')
    finally:
        c.doCleanups()


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode in ('rows', 'fixes'):
        names = [
            'test_entry_points_enter_github_mode_without_jflow_files',
            'test_full_run_through_comments',
            'test_wait_points_cap_edge_and_accepted_match_jflow_mode',
            'test_jflow_files_on_the_branch_are_refused',
            'test_spec_comment_edited_after_record_spec_is_refused',
            'test_missing_gh_auth_or_pr_fails_on_one_line_without_writes',
        ] if mode == 'rows' else [
            'test_spec_comment_with_its_marker_removed_is_refused',
            'test_spec_recorded_after_the_newest_check_needs_another_check',
            'test_marked_comment_counts_only_from_the_gh_user_or_write_access',
            'test_repo_option_runs_gh_in_that_clone',
            'test_fork_pull_request_found_through_its_issue_reference',
        ]
        result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(fixtures.GitHubMode(n) for n in names))
        sys.exit(not result.wasSuccessful())
    elif mode == 'imports':
        files = sorted((ROOT / '.github/skills/jflow/scripts').glob('*.py'))
        for path in files:
            tree = ast.parse(path.read_text(), feature_version=(3, 9))
            for node in ast.walk(tree):
                modules = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) else []
                for module in modules:
                    name = module.split('.')[0]
                    assert name in sys.stdlib_module_names or name in {p.stem for p in files}, (path.name, name)
        print(f'row 8: {len(files)} scripts; Python 3.9 AST OK; third-party imports=0')
    else:
        attack(mode)
