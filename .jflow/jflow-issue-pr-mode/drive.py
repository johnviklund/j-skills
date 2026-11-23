"""Checker's CLI probes. All mutations stay in temporary fixture repositories."""
import ast
import importlib.util
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
            print(f'strip-spec-marker: exit={p.returncode}; next={__import__("json").loads(p.stdout)["step"]}')
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
    if mode == 'rows':
        names = [
            'test_entry_points_enter_github_mode_without_jflow_files',
            'test_full_run_through_comments',
            'test_wait_points_cap_edge_and_accepted_match_jflow_mode',
            'test_jflow_files_on_the_branch_are_refused',
            'test_spec_comment_edited_after_record_spec_is_refused',
            'test_missing_gh_auth_or_pr_fails_on_one_line_without_writes',
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
