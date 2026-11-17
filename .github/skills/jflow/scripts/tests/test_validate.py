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

    def test_second_receipt_needs_new_input_and_at_most_3000_bytes(self):
        self.receipt(1, 'PROVED', '- none')
        self.receipt(2, 'PROVED', '- none')
        self.assert_bad('check', 'no new input since check-1')  # check-1 never committed
        self.commit('check-1')
        self.assert_bad('check', 'no new input since check-1')
        other = self.repo / '.jflow/other/receipts/check-1.md'
        other.parent.mkdir(parents=True)
        other.write_text('x\n')
        self.commit('check-2 and another run receipt only')
        self.assert_bad('check', 'no new input since check-1')
        (self.run_dir / 'notes.md').write_text('Yes: done\n')
        self.commit('notes')
        self.assert_clean('check')
        path = self.run_dir / 'receipts/check-2.md'
        text = path.read_text().replace('## Maybes\n', '## Maybes\n- PAD\n')
        for size, clean in ((3000, True), (3001, False)):
            path.write_text(text.replace('PAD', 'x' * (size - len(text.encode()) + 3)))
            self.assertEqual(len(path.read_bytes()), size)
            if clean:
                self.assert_clean('check')
            else:
                self.assert_bad('check', 'over 3,000 bytes')
        crlf = text.replace('\n', '\r\n')
        path.write_bytes(crlf.replace('PAD', 'x' * (3001 - len(crlf.encode()) + 3)).encode())
        self.assertEqual(len(path.read_bytes()), 3001)
        self.assert_bad('check', 'over 3,000 bytes')

    def test_input_in_a_rename_or_merge_counts_and_unreadable_prior_is_reported(self):
        self.receipt(1, 'PROVED', '- none')
        first = self.run_dir / 'receipts/check-1.md'
        first.write_bytes(first.read_text().encode('utf-16'))
        self.receipt(2, 'PROVED', '- none')
        self.assert_bad('check', 'cannot read check-1')
        self.receipt(1, 'PROVED', '- none')
        self.git('add', str(first))
        self.git('commit', '-qm', 'check-1')
        self.git('mv', 'app.py', '.jflow/demo/app.py')
        self.git('commit', '-qm', 'move code into the run folder')
        self.assert_clean('check')
        self.git('reset', '-q', '--hard', 'HEAD~1')
        self.git('checkout', '-qb', 'side')
        (self.repo / '.jflow/other').mkdir()
        (self.repo / '.jflow/other/x.md').write_text('x\n')
        self.git('add', '.jflow/other')
        self.git('commit', '-qm', 'side')
        self.git('checkout', '-q', '-')
        self.git('merge', '-q', '--no-ff', '--no-commit', 'side')
        (self.run_dir / 'notes.md').write_text('Yes: done\n')
        self.git('add', str(self.run_dir / 'notes.md'))
        self.git('commit', '-qm', 'merge with notes')
        self.assert_clean('check')

    def test_new_input_accepts_a_git_path_with_a_non_utf8_byte(self):
        self.receipt(1, 'PROVED', '- none')
        self.commit('check-1')
        self.receipt(2, 'PROVED', '- none')
        notes = self.run_dir / 'notes.md'
        notes.write_text('New input\n')
        self.git('add', str(notes))
        # Stage the raw Git path without relying on the filesystem to accept it.
        blob = self.git('rev-parse', 'HEAD:app.py').encode('ascii')
        subprocess.run(['git', 'update-index', '-z', '--index-info'], cwd=self.repo,
                       input=b'100644 ' + blob + b'\tscratch-\xff.py\0', check=True)
        self.git('commit', '-qm', 'notes and a raw Git path')
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
                (product.replace('trust\n', 'trust ###\n'), good, 'Serves: Counts you can trust\n', True),
                # check-2 defects 2, 3: nested, indented and unclosed fences; an indented heading
                (product + '````md\n```\n### Retired outcome\n```\n````\n', good, 'Serves: Retired outcome\n', False),
                (product + '   ```\n### Retired outcome\n   ```\n', good, 'Serves: Retired outcome\n', False),
                (product + '~~~\n### Retired outcome\n', good, 'Serves: Retired outcome\n', False),
                (product.replace('###', '   ###'), good, 'Serves: Counts you can trust\n', True),
                (product.replace('###', '    ###'), good, 'Serves: Counts you can trust\n', False),
                # check-3: a comment block hides a heading; a tab may follow the hashes
                (product + '<!-- old\n### Retired outcome\n-->\n', good, 'Serves: Retired outcome\n', False),
                (product + '<!-- x -->\n### Later\n', good, 'Serves: Later\n', True),
                (product.replace('### ', '###\t'), good, 'Serves: Counts you can trust\n', True)):
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
        skill = SCRIPT.parents[1]
        skill_size = (skill / 'SKILL.md').stat().st_size
        # Each step's session reads SKILL.md plus one reference: cap that read at 14,000 bytes.
        # Cap the script separately at 30,000 bytes against implementation bloat.
        for step in ('spec', 'build', 'check', 'done'):
            with self.subTest(step=step):
                self.assertLessEqual(skill_size + (skill / 'references' / f'{step}.md').stat().st_size, 14000)
        self.assertLessEqual(SCRIPT.stat().st_size, 30000)
        lines = [line for line in (SCRIPT.parents[1] / 'SKILL.md').read_text().splitlines() if 'validate' in line]
        self.assertEqual(len(lines), 1)
        self.assertTrue(all(word in lines[0] for word in ('record', 'spec', 'check', 'accept')))
