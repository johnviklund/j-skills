# Patch cycle 1 verification

Synthetic fixtures only. No transcript text or local store paths are recorded here.
Writer: GPT-6.1 Sol.

## C1-T1
- Reuse search found one free-text parser, shlex.split in command_head, and no fallback helper.
- Red commit eecbc49 adds two malformed-command cases. Both fail with No closing quotation.
- Fix commit 9911caa changes only corrections.py and catches ValueError with command.split.
- StoreTests: 4 tests, OK. Full suites: workflow 126 OK; checkup 34 OK; exit 0.
- Mutation removes the fallback by re-raising ValueError. The whole-file control passes 9 tests; the mutant fails.

## C1-T2
- Reused Fixture.write, Fixture.report, user and tool. No new helper.
- Whole-file Verify: 11 tests, OK. Full suites: workflow 126 OK; checkup 36 OK; exit 0.
- Each named mutant ran alone in a detached throwaway worktree. Control: 11 tests, OK.
- cx-um, cx-tool-reset, cl-user, cl-tu, nocwd and root-rc each fail the whole-file suite.
- Assertion calls increase from 21 to 24. No existing assertion changes.
- Test growth: net 23 lines against the 30-line budget.

## C1-T3
- Reused existing command and Copilot cases, plus Fixture.write, user and tool.
- Whole-file Verify: 14 tests, OK. Detached-worktree control: 14 tests, OK.
- Full suites: workflow 126 tests OK; checkup 39 tests OK; exit 0.
- cp-um, cp-clear, once1, sortkey, cd-amp, records-dict and nl each fail alone.
- The Copilot assertion now compares every redirect line with an exact list for each decision case.
  This replaces its conditional assertIn; the new check also rejects dropped and second-message redirects.
- Assertion calls increase from 24 to 28. No assertion is removed without replacement.
- Test growth: net 19 lines against the 30-line budget.

## Mutation procedure
Copy the current script and tests into the throwaway worktree. Run unittest discover with
test_corrections.py unchanged first. Require exit 0 and a nonzero test count.
For each review mutant, replace its named condition alone, run the whole file and require a nonzero exit.
Restore the script after each group. All 13 non-equivalent review survivors fail.
The two equivalent mutants remain excluded as the patch plan specifies.
