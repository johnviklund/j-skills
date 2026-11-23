# check-3 @ 86bd967e72b71c72f08b56aded2c23a96b0492af · gpt-6.1-sol · high
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
- 1. [use] jflow_gh.py Hub.replay / jflow.py summary: after done, record a revised spec, commit another code line, record check-2 and done. Summary stops at the first done and omits the later code. It should count the current run through its latest done. Evidence: run, `python3 .jflow/jflow-issue-pr-mode/drive.py respec-summary` → net_code=1; actual diff=2 added, 0 deleted; checks=2.

## Maybes
- none
