# jflow-next-properties
Status: ready
Base: d546f8c
Serves: none

## Problem
The conductor trusts `jflow.py next` to pick every step and every stop for the human, and that logic keeps breaking in small ways. On 9 Nov the `jflow-next` and `wait-points` runs needed five fixes, each found by a full check session and not by the 14 unit tests. Between 17 and 20 Nov four more commits changed `next` rules for cap overrides, `[edge]` defects, unproved-row order, and late acceptance. A wrong `next` decision in an unattended conductor run skips a human stop or loops with nobody watching.

## Goals
1. One standard-library `unittest` command generates random run folders in real git repositories and checks `jflow.py next` against these rules:
   - Never skips a wait point: `Ask first` with `## Approach`, `Gate:` with `WAITING`, `Human checks`, or `Maybes` before `done`, including a real Maybe that starts with `None`.
   - Never counts a rerun of only `BLOCKED` or `WAITING` rows with no code change toward the check cap, and uses the last `Checks allowed:` line.
   - Never lets an `Accepted` line or a `Yes:` line clear anything other than the exact item, check sha, receipt commit order, carried lineage, or wait point it names.
   - Routes `[edge]`-only defects to the human, stops for `BLOCKED` or `UNREACHABLE` rows before `[edge]` defects, and lets late acceptance at the cap close the run only when every open row and defect is accepted.
2. When a generated run breaks a rule, the failure output prints the seed and a summary of the generated run so rerunning with that seed reproduces the same failure.
3. The property tests pass on `HEAD` `jflow.py` and fail when past 9 Nov bugs or violations of the newer `next` rules are restored.
4. Default `python3 -m unittest discover -s .github/skills/jflow/scripts/tests` runs the property tests with at least 50 generated runs in under 10 seconds of added time, and environment variables let callers set the seed and run count.
5. `jflow.py` stays unchanged unless a property test finds a real bug in `next`.

## Non-goals
- TLA+, Lean, or any model of the flow outside the test file.
- Adding Hypothesis or any other third-party package.
- Editing `jflow.py` unless a generated test exposes a real bug.
- Replacing or deleting existing tests in `test_jflow.py`.

## Constraints
- Must not break: existing `jflow.py` behavior on historical runs; the 30,000-byte script cap and 14,000-byte step-reading cap; Python 3.9+ standard library only; test budget of about 150 to 170 lines.
- Ask first: nothing.
- Gate: none.

## Proof
Rows 1 to 3 run the new property test command in scratch copies of the repo with each listed `jflow.py` change applied.

| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | one command generates random run folders and fails if `next` skips a wait point, counts a rerun of only BLOCKED or WAITING rows toward the cap, or lets an Accepted or `Yes:` line clear anything other than what it names; it fails on at least one of the five past bugs. | `unittest` | run the new property test command at `HEAD`, then in scratch copies restoring the `2f8aaa8` `None`-prefix Maybe bug, the `38b1e04` acceptance sha and prose bug, and the `f6fb039` acceptance commit-order bug | exits 0 at `HEAD` and exits non-zero on all three buggy copies | new | red |
| 2 | Generated runs catch a rerun-cap counting bug and a `Yes:` cross-clearing bug | `unittest` | run the property test command in scratch copies where `counted` counts every receipt and where `yes()` accepts any `Yes:` line | exits non-zero on both buggy copies | new | red |
| 3 | Generated runs catch violations of the `next` rules added since 17 Nov | `unittest` | run the property test command in scratch copies restoring first `Checks allowed:` line, `[edge]` before `BLOCKED` or `UNREACHABLE`, `[edge]`-only routed to `fix`, and `accepted_late` disabled | exits non-zero on all four buggy copies | new | red |
| 4 | A failure prints its seed and generated run summary, and rerunning with that seed reproduces the failure | `unittest` | capture failure output from a buggy copy in row 1, then rerun the property test command with the printed seed env var | output prints the seed and run summary, and the rerun fails on the same case | new | red |
| 5 | Default discovery runs at least 50 generated runs in under 10 seconds and honors the count override | `unittest` | time the new property test under `python3 -m unittest discover -s .github/skills/jflow/scripts/tests -k <test>` with defaults, then rerun with a larger count env var | default exits 0 in under 10 seconds covering at least 50 runs, and the override runs more cases | new | red |
| 6 | The new tests use only Python 3.9+ standard library | `python3` | run the property test under `python3 -I`, check non-local imports against `sys.stdlib_module_names`, and run `ast.parse(src, feature_version=(3, 9))` | isolated run exits 0, zero third-party imports, and Python 3.9 AST parse succeeds | new | red |
| 7 | Existing `next` outputs on historical runs and the 30,000-byte script cap stay intact | `test_validate.py` | `python3 -I -m unittest discover -s .github/skills/jflow/scripts/tests -k test_next_and_summary_match_base_on_five_runs -k test_skill_size_and_agent_instruction` | both tests pass with `OK` | keep | green |

## Human checks
- none
