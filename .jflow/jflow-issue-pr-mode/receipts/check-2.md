# check-2 @ 6827ad751d7a055ef8274f4abc70c1ff33e81384 · gpt-6.1-sol · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → entry-points test: ok |
| 2 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → full-run test: ok |
| 3 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → wait-points/cap/acceptance test: ok |
| 4 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → staged/committed-files test: ok |
| 5 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → edited-spec test: ok |
| 6 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → missing-gh/auth/PR test: ok |
| 7 | PROVED | `cat .github/skills/jflow/references/github.md` → Spec, Build, Check, Done and Public repos cover the required instructions |
| 8 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py imports` → 2 scripts; Python 3.9 AST OK; third-party imports=0 |
| 9 | PROVED | `python3 -I -m unittest discover -s .github/skills/jflow/scripts/tests -k test_next_and_summary_match_base_on_five_runs -k test_skill_size_and_agent_instruction` → Ran 2 tests; OK |

## Defects
- 1. [use] jflow_gh.py Hub.replay: after record done, record spec with a changed claim on the same issue succeeds, but an old done record forces the replacement spec to done. next skips checking it; the ready spec should require a fresh check. Evidence: run, `python3 .jflow/jflow-issue-pr-mode/drive.py respec-after-done` → step=None; why=the spec says Status: done.
- 2. [use] jflow_gh.py Hub.find_pr: close fork PR #7 and open replacement draft #8 from the same jflow/42 branch, both referencing #42. The oldest timeline reference wins; note posts to closed #7. It should use the active linked PR #8. Evidence: run, `python3 .jflow/jflow-issue-pr-mode/drive.py replaced-fork-pr` → note posted to PR #7; open run PR #8.

## Maybes
- none
