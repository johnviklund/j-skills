"""Drive the correction report against synthetic transcript stores."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'corrections.py'


def user(text, **extra):
    return dict(type='user', message={'content': text}, **extra)


def tool(name='Bash', **inputs):
    return dict(type='assistant', message={'content': [
        dict(type='tool_use', id='t1', name=name, input=inputs)]})


INTERRUPT = user([dict(type='text', text='[Request interrupted by user for tool use]')])


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / 'home'
        self.repo = Path(self.tmp.name) / 'repo'
        self.home.mkdir()
        self.repo.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)

    def write(self, records, name='a', cwd=None, age=0, store='claude'):
        roots = {'claude': f'.claude/projects/r/{name}.jsonl',
                 'codex': f'.codex/sessions/2026/11/01/rollout-{name}.jsonl',
                 'copilot': f'.copilot/session-state/{name}/events.jsonl'}
        path = self.home / roots[store]
        path.parent.mkdir(parents=True, exist_ok=True)
        if store == 'claude':
            records = [dict(type='system', cwd=str(cwd or self.repo)), *records]
        path.write_text(''.join(json.dumps(r) + '\n' for r in records))
        stamp = time.time() - age * 86400
        os.utime(path, (stamp, stamp))

    def report(self, *args):
        env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_CONFIG_DIR', 'CODEX_HOME')}
        r = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.repo,
                           env={**env, 'HOME': str(self.home)}, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout


class ClaudeTests(Fixture):
    def test_ClaudeTests_interrupt_shapes(self):
        for records, key in [([tool(), INTERRUPT], 'Bash'),
                             ([tool(), user('new turn'), INTERRUPT], 'no tool'),
                             ([user('[Request interrupted by user]')], 'no tool'),
                             ([user([dict(type='tool_result', content='quoted [Request interrupted by user]')])], None),
                             ([dict(INTERRUPT, isSidechain=True)], None),
                             ([user('quoted [Request interrupted by user]')], None)]:
            with self.subTest(records=records):
                self.write(records)
                out = self.report()
                self.assertEqual('once: 1 key(s)' in out, key is not None)
                if key:
                    self.write(records, 'b')
                    self.assertIn(f'- interrupt · {key} · 2 sessions · 2 times', self.report())
                    (self.home / '.claude/projects/r/b.jsonl').unlink()

    def test_ClaudeTests_redirect(self):
        self.write([tool(), INTERRUPT, user('meta', isMeta=True),
                    user('<command-name>test</command-name>'),
                    user([dict(type='tool_result', content='result')]),
                    user('x' * 250), user('later')])
        redirects = [line for line in self.report().splitlines() if line.startswith('- claude')]
        self.assertEqual(redirects, ['- claude · interrupt · Bash: ' + 'x' * 200])

    def test_ClaudeTests_repeats_count_sessions(self):
        records = [tool(), INTERRUPT, user('continue'), tool(), INTERRUPT]
        self.write(records)
        self.assertIn('once: 1 key(s)', self.report())
        self.assertNotIn('sessions ·', self.report())
        self.write([tool(), INTERRUPT], 'b')
        self.assertIn('- interrupt · Bash · 2 sessions · 3 times', self.report())

    def test_ClaudeTests_filters(self):
        cases = [(0, None, (), True), (15, None, (), False), (20, None, ('--days', '30'), True),
                 (13, self.repo / '.worktrees/x', (), True),
                 (0, str(self.repo) + '-old', (), False),
                 (0, self.home, (), False), (0, self.home, ('--all-repos',), True)]
        for age, cwd, args, kept in cases:
            with self.subTest(age=age, cwd=cwd, args=args):
                self.write([INTERRUPT], cwd=cwd, age=age)
                self.assertEqual('once: 1 key(s)' in self.report(*args), kept)

    def test_ClaudeTests_missing_stores(self):
        self.assertEqual(self.report().splitlines()[0],
                         'stores: claude missing · codex missing · copilot missing')


class StoreTests(Fixture):
    def test_StoreTests_denials(self):
        prefix = "The user doesn't want to proceed with this tool use."
        for name, text, expected in [
                ('Bash', prefix, 'denial · Bash · git'),
                ('Edit', prefix, 'denial · Edit'),
                ('Bash', 'quoted ' + prefix, None),
                ('Bash', prefix + " the user said:\nuse a branch", 'denial · Bash · git')]:
            with self.subTest(name=name, text=text):
                result = user([dict(type='tool_result', tool_use_id='t1', content=text)])
                self.write([tool(name, command='cd /r && git push'), result, user('next')])
                out = self.report()
                self.assertEqual('once: 1 key(s)' in out, expected is not None)
                if expected:
                    redirect = 'use a branch' if 'the user said:' in text else 'next'
                    self.assertIn(f'- claude · {expected}: {redirect}', out)
                    if redirect == 'use a branch':
                        self.assertNotIn(': next', out)

    def test_StoreTests_codex(self):
        for source, reason, kept in [('vscode', 'interrupted', True),
                                     ({'subagent': {'guardian_review': {}}}, 'interrupted', False),
                                     ('vscode', 'completed', False)]:
            with self.subTest(source=source, reason=reason):
                rows = [dict(type='session_meta', payload=dict(cwd=str(self.repo), source=source)),
                        dict(type='response_item', payload=dict(type='custom_tool_call', name='exec')),
                        dict(type='event_msg', payload=dict(type='turn_aborted', reason=reason)),
                        dict(type='response_item', payload=dict(type='message', role='developer',
                             content=[dict(type='input_text', text='<turn_aborted>') ])),
                        dict(type='event_msg', payload=dict(type='item_completed',
                             item=dict(type='UserMessage', content=[dict(type='text', text='try again')]))),
                        dict(type='event_msg', payload=dict(type='item_completed',
                             item=dict(type='UserMessage', content=[dict(type='text', text='later')]))),
                        dict(type='response_item', payload=dict(type='turn_aborted', reason='interrupted'))]
                self.write(rows, store='codex')
                out = self.report()
                self.assertIn('codex 1 file(s)', out)
                self.assertEqual('once: 1 key(s)' in out, kept)
                if kept:
                    self.assertIn('- codex · interrupt · exec: try again', out)
                    self.assertNotIn(': later', out)
                    self.write(rows, 'b', store='codex')
                    self.assertIn('- interrupt · exec · 2 sessions · 2 times', self.report())
                    (self.home / '.codex/sessions/2026/11/01/rollout-b.jsonl').unlink()

    def test_StoreTests_copilot(self):
        for source, kind, kept in [('unattended_fallback', 'denied-no-approval-rule', False),
                                   ('user', 'denied-interactively-by-user', True),
                                   ('user', 'approved', False)]:
            with self.subTest(source=source, kind=kind):
                self.write([
                    dict(type='session.start', data=dict(context=dict(cwd=str(self.repo)))),
                    dict(type='permission.requested', data=dict(requestId='r1', permissionRequest=dict(
                         kind='shell', commands=[dict(identifier='ls')]))),
                    dict(type='permission.completed', data=dict(requestId='r1',
                         result=dict(kind=kind), decisionSource=source)),
                    dict(type='user.message', data=dict(content='use rg'))], store='copilot')
                out = self.report()
                self.assertIn('copilot 1 file(s)', out)
                self.assertEqual('once: 1 key(s)' in out, kept)
                if kept:
                    self.assertIn('- copilot · denial · shell · ls: use rg', out)


if __name__ == '__main__':
    unittest.main()
