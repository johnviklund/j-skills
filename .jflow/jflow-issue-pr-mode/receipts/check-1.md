# check-1 @ de709e7a6db2f7e408a470534d50b181b0a044b8 · gpt-6.1-sol · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → entry-points test: ok |
| 2 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → full-run test: ok |
| 3 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → wait-points/cap/acceptance test: ok |
| 4 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → staged/committed-files test: ok |
| 5 | BROKEN | defect 1 |
| 6 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py rows` → missing-gh/auth/PR test: ok |
| 7 | PROVED | `cat .github/skills/jflow/references/github.md` → Spec, Build, Check, Done and Public repos cover the required instructions |
| 8 | PROVED | `python3 .jflow/jflow-issue-pr-mode/drive.py imports` → 2 scripts; Python 3.9 AST OK; third-party imports=0 |
| 9 | BROKEN | defect 6; both named tests pass |

## Defects
- 1. [edge] jflow_gh.py Hub.__init__: editing an approved spec comment to remove its marker makes `specs` empty; next exits 0 and offers spec. It should refuse the changed approved comment. Evidence: run, `python3 .jflow/jflow-issue-pr-mode/drive.py strip-spec-marker` → exit=0; next=spec.
- 2. [use] jflow_gh.py Hub.replay: recording a replacement spec after a green check preserves its receipts; next offers done for the changed claim. It should require every row again. Evidence: run, `python3 .jflow/jflow-issue-pr-mode/drive.py respec` → respec: next=done.
- 3. [use] jflow_gh.py TRUSTED/Hub.__init__: a read-only organization member's marked Yes: done clears the human wait. It should require write permission; MEMBER only denotes membership per the [schema](https://docs.github.com/en/graphql/reference/issues#commentauthorassociation). Evidence: run, `python3 .jflow/jflow-issue-pr-mode/drive.py member-approval` → before=human; after=done; permission not queried.
- 4. [use] jflow_gh.py api: running next from outside the clone with --repo keeps gh in the caller's directory; repository inference fails or targets another clone. It should use --repo for gh too. Evidence: run with cwd-aware stub, `python3 .jflow/jflow-issue-pr-mode/drive.py repo-option` → exit=1; cannot infer repository from cwd.
- 5. [edge] jflow_gh.py Hub.__init__: a draft PR from fork-owner:jflow/42 with Refs #42 is excluded by the upstream-owner head filter. It should find the linked fork PR. Evidence: run with owner-aware stub, `python3 .jflow/jflow-issue-pr-mode/drive.py fork-pr` → exit=1; no linked pull request.
- 6. [use] SKILL.md GitHub-mode pointer: check loads SKILL.md, check.md and github.md, totaling 18,246 bytes. It should stay within the 14,000-byte step-reading cap. Evidence: run, `wc -c .github/skills/jflow/{SKILL.md,references/check.md,references/github.md}` → 18246 total.

## Maybes
- none
