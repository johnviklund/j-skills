"""Exercise installed hooks through real git in disposable repositories."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]


class HookRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.home = self.root / 'home'
        self.home.mkdir()
        self.env = {**os.environ, 'HOME': str(self.home), 'CODEX_HOME': str(self.home / '.codex'),
                    'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull}
        self.scripts = self.root / 'skill' / 'scripts'
        shutil.copytree(SCRIPTS, self.scripts, ignore=shutil.ignore_patterns('tests', '__pycache__'))
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')

    def run_cmd(self, *args, input=None, env=None):
        return subprocess.run(args, cwd=self.repo, env=env or self.env, input=input,
                              text=True, capture_output=True)

    def git(self, *args):
        return self.run_cmd('git', *args)

    def install(self, *args):
        return self.run_cmd(sys.executable, str(self.scripts / 'hooks.py'), 'install', *args)

    def stage(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.git('add', name)

    def commit(self):
        return self.git('commit', '-qm', 'fixture')


class InstallPreCommitTests(HookRepo):
    def test_Install_is_executable_and_idempotent(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        hooks = [self.repo / '.git/hooks' / name for name in ('pre-commit', 'pre-push')]
        before = [p.read_bytes() for p in hooks]
        for p in hooks:
            self.assertTrue(os.access(p, os.X_OK))
            self.assertIn('j-skills workflow hook', p.read_text())
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, [p.read_bytes() for p in hooks])

    def test_Install_refuses_foreign_configuration_without_writes(self):
        for foreign in ('pre-push', 'core.hooksPath'):
            with self.subTest(foreign=foreign):
                path = self.repo / '.git/hooks/pre-push'
                if foreign == 'pre-push':
                    path.write_text('# foreign\n')
                else:
                    self.git('config', 'core.hooksPath', 'custom-hooks')
                result = self.install()
                self.assertEqual(result.returncode, 1)
                self.assertIn(foreign, result.stdout + result.stderr)
                self.assertFalse((self.repo / '.git/hooks/pre-commit').exists())
                if path.exists():
                    self.assertEqual(path.read_text(), '# foreign\n')
                    path.unlink()

    def test_PreCommit_checks_only_staged_live_runs(self):
        self.assertEqual(self.install().returncode, 0)
        self.stage('.workflow/r/brainstorm.md', 'broken\n')
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ERROR', result.stdout + result.stderr)
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'broken fixture')
        for name in ('src.py', '.workflow/.gitkeep', '.workflow/archive/old.txt'):
            self.stage(name, 'fixture\n')
            self.assertEqual(self.commit().returncode, 0, name)
        self.stage('.workflow/r/brainstorm.md',
                   'Command: workflow brainstorm r\nCreated: 2026-11-01\nBase: ' +
                   self.git('rev-parse', 'HEAD').stdout.strip() + '\nInputs: none\nStatus: drafting\n')
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('warnings', result.stdout + result.stderr)

    def test_PreCommit_fallback_and_missing_copy(self):
        self.assertEqual(self.install().returncode, 0)
        target = self.repo / '.agents/skills/workflow'
        target.parent.mkdir(parents=True)
        self.scripts.parent.rename(self.root / 'moved')
        target.symlink_to(self.root / 'moved', target_is_directory=True)
        self.stage('.workflow/r/brainstorm.md', 'broken\n')
        self.assertNotEqual(self.commit().returncode, 0)
        target.unlink()
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr)
        for folder in ('.github', '.agents', '.claude', '.codex', '.copilot'):
            self.assertIn(folder, result.stderr)
