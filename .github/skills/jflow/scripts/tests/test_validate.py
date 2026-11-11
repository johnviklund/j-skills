import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_jflow as fixture

SCRIPT = fixture.SCRIPT

ROOT = SCRIPT.parents[4]
RUNS = ('drive-py-at-done', 'jflow-config', 'jflow-next', 'receipt-evidence-cap', 'wait-points')


class Validation(unittest.TestCase):
    setUp = fixture.RunRecord.setUp
    tearDown = fixture.RunRecord.tearDown
    git = fixture.RunRecord.git
    commit = fixture.RunRecord.commit
    receipt = fixture.RunRecord.receipt

    def cli(self, step, command='validate'):
        args = [sys.executable, str(SCRIPT), command, 'demo', step, '--repo', str(self.repo)]
        if command == 'record':
            args += ['--model', 'test', '--effort', 'high']
        return subprocess.run(args, capture_output=True, text=True)

    def assert_clean(self, step):
        result = self.cli(step)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))

    def assert_bad(self, step, fault):
        result = self.cli(step)
        self.assertEqual(result.returncode, 1, result)
        lines = (result.stdout + result.stderr).splitlines()
        self.assertTrue(lines)
        for line in lines:
            self.assertRegex(line, r'^\.jflow/demo/(spec\.md|receipts/check-[^:]+\.md):\d+: ')
        self.assertIn(fault, '\n'.join(lines))

    def test_historical_specs_and_all_sixteen_receipts(self):
        objects = self.repo / '.git/objects/info/alternates'
        objects.write_text(str(ROOT / '.git/objects') + '\n')
        count = 0
        for slug in RUNS:
            source = ROOT / '.jflow' / slug
            shutil.copyfile(source / 'spec.md', self.run_dir / 'spec.md')
            self.assert_clean('spec')
            count += 1
            for receipt in sorted((source / 'receipts').glob('check-*.md')):
                with self.subTest(slug=slug, receipt=receipt.name):
                    for old in (self.run_dir / 'receipts').glob('*'):
                        old.unlink()
                    shutil.copyfile(receipt, self.run_dir / 'receipts' / receipt.name)
                    self.assert_clean('check')
                    count += 1
        self.assertEqual(count, 21)

    def test_spec_faults_and_both_kind_base_pairs(self):
        path = self.run_dir / 'spec.md'
        good = path.read_text()
        cases = [('Status: ready', 'Status: draft', 'Status'),
                 (self.git('rev-parse', 'HEAD~1'), 'abcdef0', 'sha'),
                 ('## Goals', '## Goal', 'Goals'),
                 ('| Surface ', '| Target ', 'columns'),
                 ('| new | red', '| typo | red', 'Kind'),
                 ('| new | red', '| new | green', 'Base'),
                 ('| keep | green', '| keep | red', 'Base'),
                 ('- Gate: none.', '', 'Gate'),
                 ('| 2 | b ', '| 1 | b ', 'duplicate')]
        for before, after, fault in cases:
            with self.subTest(fault=fault, after=after):
                path.write_text(good.replace(before, after))
                self.assert_bad('spec', fault)
        for status in ('ready', 'done'):
            path.write_text(good.replace('ready', status).replace('| new | red', '| live | red'))
            self.assert_clean('spec')

    def test_receipt_faults_and_evidence_boundary(self):
        self.receipt(1, 'PROVED', '- 1. app.py: input -> bad -> good. Evidence: run, bad')
        path = self.run_dir / 'receipts/check-1.md'
        good = path.read_text()
        cases = [('# check-1', '# check-2', 'header'),
                 (self.git('rev-parse', 'HEAD'), 'abcdef0', 'sha'),
                 ('| 2 | PROVED | `cmd` -> ok |\n', '', 'missing row 2'),
                 ('| 2 | PROVED', '| 3 | PROVED', 'unknown row'),
                 ('| 1 | PROVED', '| 1 | NOPE', 'verdict'),
                 ('`cmd` -> ok', 'x' * 241, '240'),
                 ('Evidence: run, bad', 'Evidence: ' + 'x' * 241, '240'),
                 ('Evidence: run, bad', 'Evidence: ' + 'x' * 241 + ' Evidence: x', '240'),
                 ('| 1 | PROVED | `cmd` -> ok |', '| 1 | BROKEN | defect 2 |', 'unknown defect 2'),
                 ('| 1 | PROVED', '| 1 | ACCEPTED', 'Accepted'),
                 ('## Maybes', '## Extra\n\n## Maybes', 'extra section'),
                 ('| 2 | PROVED', '| 1 | PROVED', 'duplicate'),
                 ('Evidence: run, bad', 'run, bad', 'invalid defect')]
        for before, after, fault in cases:
            with self.subTest(fault=fault, after=after[:40]):
                path.write_text(good.replace(before, after))
                self.assert_bad('check', fault)
        path.write_text(good.replace('`cmd` -> ok', 'x' * 240).replace('Evidence: run, bad', 'Evidence: ' + 'x' * 240))
        self.assert_clean('check')
        for verdict in ('PROVED', 'BROKEN', 'BLOCKED', 'UNREACHABLE', 'WAITING'):
            path.write_text(good.replace('| 1 | PROVED', '| 1 | ' + verdict).replace('`cmd` -> ok', 'defect 1'))
            self.assert_clean('check')

    def test_accepted_faults_and_valid_accepted_row(self):
        path = self.run_dir / 'spec.md'
        good = path.read_text()
        sha = self.git('rev-parse', 'HEAD')
        accepted = f'\n## Accepted\n- Row 1 · miss · "accept it" · 2026-11-10 · {sha}\n'
        for text, fault in [(accepted.replace(' · ' + sha, ''), 'Accepted'),
                            (accepted.replace('Row 1', 'Row 3'), 'unknown row 3'),
                            (accepted.replace(sha, 'abcdef0'), 'sha'),
                            (accepted.replace('"accept it" · ', ''), 'Accepted')]:
            with self.subTest(fault=fault):
                path.write_text(good + text)
                self.assert_bad('accept', fault)
        path.write_text(good + accepted.replace(' · ' + sha, ''))
        self.receipt(1, 'ACCEPTED', '- none')
        self.assert_bad('check', 'Accepted')
        path.write_text(good + accepted + f'- Defect 1 · crash · "accept" · 2026-11-10 · {sha}\n')
        self.assert_clean('accept')
        self.receipt(1, 'ACCEPTED', '- none')
        self.assert_clean('check')

    def test_only_broken_direct_citations_require_a_defect(self):
        quote = '`grep -c "defect 1" receipts/check-1.md` → 2'
        defect = '- 1. app.py: input -> bad -> good. Evidence: run, bad'
        cases = [('PROVED', quote, '- none', 0), ('BROKEN', quote, '- none', 0),
                 ('PROVED', 'defect 1', '- none', 0), ('BROKEN', 'defect 1', '- none', 1),
                 ('BROKEN', 'Defect 1', '- none', 1), ('BROKEN', 'defect 1', defect, 0)]
        log = self.run_dir / 'run.jsonl'
        for verdict, evidence, defects, code in cases:
            with self.subTest(verdict=verdict, evidence=evidence, defects=defects):
                self.receipt(1, verdict, defects)
                path = self.run_dir / 'receipts/check-1.md'
                path.write_text(path.read_text().replace('`cmd` -> ok', evidence, 1))
                log.write_text('{"step": "decision"}\n')
                before = log.read_bytes()
                if code:
                    self.assert_bad('check', 'unknown defect 1')
                else:
                    self.assert_clean('check')
                result = self.cli('check', 'record')
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(log.read_bytes() == before, bool(code))

    def test_broken_citation_lists_check_each_defect(self):
        defect = '- 1. app.py: input -> bad -> good. Evidence: run, bad'
        both = defect + '\n' + defect.replace('- 1.', '- 9.')
        quote = '`grep -c "defect 1, defect 9" receipts/check-1.md` → 2'
        cases = [('BROKEN', 'defect 1, defect 9', '- none', 1),
                 ('BROKEN', 'defect 1, defect 9', defect, 1),
                 ('BROKEN', 'defect 9, defect 1', defect, 1),
                 ('BROKEN', 'defect 1,defect 9', defect, 1),
                 ('BROKEN', 'defect 1, defect 9', both, 0),
                 ('PROVED', 'defect 1, defect 9', '- none', 0),
                 ('BROKEN', quote, '- none', 0)]
        log = self.run_dir / 'run.jsonl'
        for verdict, evidence, defects, code in cases:
            with self.subTest(verdict=verdict, evidence=evidence, defects=defects):
                self.receipt(1, verdict, defects)
                path = self.run_dir / 'receipts/check-1.md'
                path.write_text(path.read_text().replace('`cmd` -> ok', evidence, 1))
                log.write_text('{"step": "decision"}\n')
                before = log.read_bytes()
                if code:
                    self.assert_bad('check', 'unknown defect 9')
                else:
                    self.assert_clean('check')
                result = self.cli('check', 'record')
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(log.read_bytes() == before, bool(code))

    def test_record_guards_leave_log_unchanged_and_other_steps_write(self):
        log = self.run_dir / 'run.jsonl'
        sentinel = '{"step": "decision"}\n'
        log.write_text(sentinel)
        spec = self.run_dir / 'spec.md'
        good = spec.read_text()
        self.receipt(1, 'NOPE', '- none')
        for step in ('check', 'spec', 'accept'):
            with self.subTest(step=step):
                spec.write_text(good if step == 'check' else good.replace('Status: ready', 'Status: draft')
                                if step == 'spec' else good + '\n## Accepted\n- Row 1 · missing sha\n')
                result = self.cli(step, 'record')
                self.assertEqual(result.returncode, 1)
                self.assertIn('.jflow/demo/', result.stderr)
                self.assertEqual(log.read_text(), sentinel)
        self.assertEqual(self.cli('build', 'record').returncode, 0)
        self.assertNotEqual(log.read_text(), sentinel)
        spec.write_text(good)
        self.receipt(1, 'PROVED', '- none')
        self.assertEqual(self.cli('check', 'record').returncode, 0)
        self.assert_clean('check')

    def test_serves_must_name_a_product_outcome(self):
        spec = self.run_dir / 'spec.md'
        good = spec.read_text()
        product = '# p\n## The desired state\n### Counts you can trust\n'
        fenced = product + '```markdown\n### Retired outcome\n```\n'
        example = good.replace('A fixture run.', '```text\nServes: Counts you can trust\n```')
        log = self.run_dir / 'run.jsonl'
        for product_md, text, serves, ok in (
                (product, good, '', False), (product, good, 'Serves: Fast\n', False),
                (product, good, 'Serves: The desired state\n', False),
                (product, good, 'Serves: Counts you can trust\n', True), (product, good, 'Serves: none\n', True),
                (product, example, '', False),  # check-1 defect 1: a quoted example is not the header
                (fenced, good, 'Serves: Retired outcome\n', False),  # defect 2: fenced heading
                (product.replace('trust\n', 'trust ###\n'), good, 'Serves: Counts you can trust\n', True)):
            with self.subTest(product=product_md, serves=serves, example=text is example):
                (self.repo / 'PRODUCT.md').write_text(product_md)
                spec.write_text(text.replace('A run with', serves + 'A run with'))
                if ok:
                    self.assert_clean('spec')
                else:
                    self.assert_bad('spec', 'Serves')
                    self.assertEqual(self.cli('spec', 'record').returncode, 1)
                    self.assertFalse(log.exists())

    def test_missing_files_report_problems_without_traceback(self):
        self.assert_bad('check', 'missing receipt')
        (self.run_dir / 'spec.md').unlink()
        self.assert_bad('spec', 'cannot read file')

    def test_next_and_summary_match_base_on_five_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / 'jflow'
            shutil.copytree(SCRIPT.parents[1], skill, ignore=shutil.ignore_patterns('tests', '__pycache__'))
            old = skill / 'scripts/jflow.py'
            old.write_bytes(subprocess.check_output(['git', '-C', str(ROOT), 'show',
                                                    'd53d8d1:.github/skills/jflow/scripts/jflow.py']))
            for slug in RUNS:
                for command in ('next', 'summary'):
                    with self.subTest(slug=slug, command=command):
                        args = [command, slug, '--json', '--repo', str(ROOT)]
                        before = subprocess.check_output([sys.executable, str(old)] + args)
                        after = subprocess.check_output([sys.executable, str(SCRIPT)] + args)
                        self.assertEqual(after, before)

    def test_skill_size_and_agent_instruction(self):
        files = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '.github/skills/jflow'], text=True)
        self.assertLess(sum((ROOT / f).stat().st_size for f in files.splitlines() if '/tests/' not in f), 50000)
        lines = [line for line in (SCRIPT.parents[1] / 'SKILL.md').read_text().splitlines() if 'validate' in line]
        self.assertEqual(len(lines), 1)
        self.assertTrue(all(word in lines[0] for word in ('record', 'spec', 'check', 'accept')))
