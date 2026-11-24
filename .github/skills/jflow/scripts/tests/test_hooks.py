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


OLD_STUB = '#!/bin/sh\n# j-skills old hook\nexec python3 /gone/hooks.py {hook} "$@"\n'


class InstallTests(HookRepo):
    def test_Install_is_executable_and_idempotent(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        hook = self.repo / '.git/hooks/pre-push'
        before = hook.read_bytes()
        self.assertTrue(os.access(hook, os.X_OK))
        self.assertIn('# j-skills hook', hook.read_text())
        self.assertFalse((self.repo / '.git/hooks/pre-commit').exists())
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, hook.read_bytes())

    def test_Install_upgrades_old_stubs_and_keeps_foreign_pre_commit(self):
        hooks = self.repo / '.git/hooks'
        for hook in ('pre-commit', 'pre-push'):
            (hooks / hook).write_text(OLD_STUB.format(hook=hook))
        self.assertEqual(self.install('--check').stdout.strip(),
                         'would install pre-push, would remove pre-commit')
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((hooks / 'pre-commit').exists())
        self.assertNotIn('/gone/', (hooks / 'pre-push').read_text())
        self.assertEqual(self.install('--check').stdout.strip(), 'installed')
        (hooks / 'pre-commit').write_text('# foreign\n')
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual((hooks / 'pre-commit').read_text(), '# foreign\n')

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
                if path.exists():
                    self.assertEqual(path.read_text(), '# foreign\n')
                    path.unlink()


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

    def test_PrePush_url_target_excludes_only_its_own_ref(self):
        work = self.root / 'work.git'
        self.assertEqual(self.git('init', '-q', '--bare', str(work)).returncode, 0)
        self.assertEqual(self.git('remote', 'add', 'work', str(work)).returncode, 0)
        self.stage('first.txt', 'clean\n')
        self.assertEqual(self.commit().returncode, 0)
        result = self.git('push', str(self.origin), 'HEAD:refs/heads/first')
        self.assertEqual(result.returncode, 0, result.stderr)
        # The target moves on to a commit this repo lacks; a force push scans everything instead.
        other = self.root / 'other'
        self.assertEqual(self.git('clone', '-q', '-b', 'first', str(self.origin), str(other)).returncode, 0)
        for args in (('commit', '-q', '--allow-empty', '-m', 'elsewhere'), ('push', '-q', 'origin', 'first')):
            self.assertEqual(subprocess.run(['git', '-C', str(other), '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=t',
                                            '-c', 'user.email=t@t.invalid', *args],
                                            env=self.env, capture_output=True).returncode, 0)
        result = self.git('push', '--force', str(self.origin), 'HEAD:refs/heads/first')
        self.assertEqual(result.returncode, 0, result.stderr)
        token = 'gh' + 'p_' + ''.join(random.Random(17).sample(string.ascii_letters + string.digits, 36))
        self.stage('credential.txt', token + '\n')
        self.assertEqual(self.commit().returncode, 0)
        unhooked = ('-c', 'core.hooksPath=/dev/null', 'push')
        self.assertEqual(self.git(*unhooked, 'work', 'HEAD:refs/heads/seed').returncode, 0)
        result = self.git('push', str(self.origin), 'HEAD:refs/heads/leak')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(token, result.stdout + result.stderr)
        # Once the target's own ref holds the secret, a clean commit on top of it pushes.
        self.assertEqual(self.git(*unhooked, str(self.origin), 'HEAD:refs/heads/seed').returncode, 0)
        self.stage('clean.txt', 'clean\n')
        self.assertEqual(self.commit().returncode, 0)
        result = self.git('push', str(self.origin), 'HEAD:refs/heads/seed')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_PrePush_unknown_revision_is_refused(self):
        result = self.run_cmd(sys.executable, str(self.scripts / 'hooks.py'), 'pre-push', 'origin',
                              input='refs/heads/x 1234567890abcdef1234567890abcdef12345678 '
                                    'refs/heads/x ' + '0' * 40 + '\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('refs/heads/x', result.stderr)

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
        self.assertEqual(result.stdout.strip(), 'would install pre-push')
        self.assertFalse((self.repo / '.git/hooks/pre-push').exists())
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.install('--check').stdout.strip(), 'installed')
        (self.repo / '.git/hooks/pre-push').chmod(0o644)
        self.assertEqual(self.install('--check').stdout.strip(), 'would install pre-push')
