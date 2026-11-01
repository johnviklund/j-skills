"""Exercise installed hooks through real git in disposable repositories."""
import os
import random
import string
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
        for name in ('src.py', '.workflow/.gitkeep', '.workflow/archive/old.txt', 'docs/r/notes.md'):
            self.stage(name, 'fixture\n')
            self.assertEqual(self.commit().returncode, 0, name)
        self.assertEqual(self.git('rm', '-r', '.workflow/r').returncode, 0)
        self.assertEqual(self.commit().returncode, 0)
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

    def test_PreCommit_missing_checker_warns_and_allows(self):
        self.assertEqual(self.install().returncode, 0)
        (self.scripts / 'check-run.py').unlink()
        self.stage('.workflow/r/brainstorm.md', 'broken\n')
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('check-run.py', result.stderr)

    def test_PreCommit_external_CODEX_HOME_fallback(self):
        self.env['CODEX_HOME'] = str(self.root / 'codex-external')
        self.assertEqual(self.install().returncode, 0)
        target = Path(self.env['CODEX_HOME']) / 'skills/workflow'
        target.parent.mkdir(parents=True)
        self.scripts.parent.rename(target)
        self.stage('.workflow/r/brainstorm.md', 'broken\n')
        result = self.commit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ERROR', result.stdout + result.stderr)


class PrePushTests(HookRepo):
    def setUp(self):
        super().setUp()
        self.origin = self.root / 'origin.git'
        self.git('init', '-q', '--bare', str(self.origin))
        self.git('remote', 'add', 'origin', str(self.origin))
        self.assertEqual(self.install().returncode, 0)

    def test_PrePush_secret_on_other_remote_is_refused(self):
        work = self.root / 'work.git'
        self.assertEqual(self.git('init', '-q', '--bare', str(work)).returncode, 0)
        self.assertEqual(self.git('remote', 'add', 'work', str(work)).returncode, 0)
        token = 'gh' + 'p_' + ''.join(random.Random(17).sample(string.ascii_letters + string.digits, 36))
        self.stage('credential.txt', token + '\n')
        self.assertEqual(self.commit().returncode, 0)
        self.assertEqual(self.git('-c', 'core.hooksPath=/dev/null', 'push', 'work',
                                  'HEAD:refs/heads/seed').returncode, 0)
        result = self.git('push', 'origin', 'HEAD:refs/heads/feature')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(token, result.stdout + result.stderr)
        self.assertNotEqual(self.git('--git-dir=' + str(self.origin), 'rev-parse', '--verify',
                                     'refs/heads/feature').returncode, 0)

    def test_PrePush_secret_to_spaced_target_is_refused(self):
        spaced = self.root / 'origin space.git'
        self.origin.rename(spaced)
        token = 'gh' + 'p_' + ''.join(random.Random(17).sample(string.ascii_letters + string.digits, 36))
        self.stage('credential.txt', token + '\n')
        self.assertEqual(self.commit().returncode, 0)
        result = self.git('push', str(spaced), 'HEAD:refs/heads/leak')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(token, result.stdout + result.stderr)
        self.assertNotEqual(self.git('--git-dir=' + str(spaced), 'rev-parse', '--verify',
                                     'refs/heads/leak').returncode, 0)

    def test_PrePush_secret_is_redacted_and_remote_history_is_excluded(self):
        token = 'gh' + 'p_' + ''.join(random.Random(17).sample(string.ascii_letters + string.digits, 36))
        self.stage('credential.txt', token + '\n')
        self.assertEqual(self.commit().returncode, 0)
        result = self.git('push', 'origin', 'HEAD:refs/heads/seed')
        out = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(out, r'RuleID:\s+github-pat')
        self.assertIn('File:', out)
        self.assertNotIn(token, out)
        # Seed remote history without installed hooks, then restore them.
        result = self.git('-c', 'core.hooksPath=/dev/null', 'push', 'origin', 'HEAD:refs/heads/seed')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git('checkout', '-qb', 'clean')
        self.stage('clean.txt', 'clean\n')
        self.assertEqual(self.commit().returncode, 0)
        result = self.git('push', 'origin', 'clean')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('push', 'origin', '--delete', 'clean').returncode, 0)

    def test_PrePush_missing_scanner_or_script_blocks(self):
        self.stage('clean.txt', 'clean\n')
        self.assertEqual(self.commit().returncode, 0)
        minimal = self.root / 'bin'
        minimal.mkdir()
        for name in ('git', 'python3', 'sh'):
            (minimal / name).symlink_to(shutil.which(name))
        env = {**self.env, 'PATH': str(minimal)}
        result = self.run_cmd('git', 'push', 'origin', 'HEAD:refs/heads/new', env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('install gitleaks', result.stderr)
        shutil.rmtree(self.scripts.parent)
        result = self.git('push', 'origin', 'HEAD:refs/heads/new')
        self.assertNotEqual(result.returncode, 0)
        for folder in ('.github', '.agents', '.claude', '.codex', '.copilot'):
            self.assertIn(folder, result.stderr)


class HookCheckTests(HookRepo):
    def test_HookCheck_dry_run_and_installed(self):
        result = self.install('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'would install pre-commit, pre-push')
        self.assertFalse((self.repo / '.git/hooks/pre-commit').exists())
        self.assertFalse((self.repo / '.git/hooks/pre-push').exists())
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.install('--check').stdout.strip(), 'installed')
        (self.repo / '.git/hooks/pre-push').chmod(0o644)
        self.assertEqual(self.install('--check').stdout.strip(), 'would install pre-push')
        (self.repo / '.git/hooks/pre-push').unlink()
        self.assertEqual(self.install('--check').stdout.strip(), 'would install pre-push')
