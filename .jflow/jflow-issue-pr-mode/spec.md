# jflow-issue-pr-mode
Status: done
Base: 4a396e5
Serves: none

## Problem
Shared and public repositories often reject `.jflow/` files and direct pushes to the default branch. A developer using jflow on one of those repositories cannot commit `.jflow/<slug>/` or push straight to `main`, so they skip jflow or strip its files by hand before opening a pull request. An issue and pull request mode lets jflow run on pull request gated GitHub repositories without committing run files.

## Goals
1. Passing an issue number such as `#42` or a GitHub issue URL enters issue and pull request mode with zero `.jflow/` files in the repository. Setting `git config jflow.mode github` or an external config via `--config` or `$JFLOW_CONFIG` enables it for plain slugs, while plain slugs without that setting stay in `.jflow/` mode.
2. `jflow.py` runs `validate`, `record`, `next` in text, `--ask`, and `--json` forms, and `summary` against GitHub via `gh`. The issue holds the spec as a comment on an existing issue, or as a new issue for a plain slug, plus `## Accepted` comments. The linked draft pull request holds check receipts, builder notes, `Yes:` approvals, `Checks allowed:` lines, and step records as structured comments.
3. In issue and pull request mode, `validate` and `next` refuse staged or committed `.jflow/` files on the branch, and flag any edit to the approved spec comment outside `## Accepted` comments.
4. `jflow.py next` enforces the same wait points, check cap without counting no-code-change reruns, `[edge]`-only stops, and `## Accepted` commit SHA and order rules as `.jflow/` mode.
5. Missing `gh`, unauthenticated `gh`, or a missing linked pull request fails with a clear single-line error, no traceback, and no partial state written.
6. The jflow skill docs cover issue and pull request mode for `spec`, `build`, `check`, and `done`. They specify preserving existing issue bodies, opening a draft pull request on a branch, keeping `drive.py` untracked, keeping `check` blind to builder note comments until findings are drafted, marking the pull request ready for review at `done` without merging, and confirming before GitHub writes on public repositories per `public_paid_needs_human`.
7. Existing `.jflow/` mode outputs on historical runs, Python 3.9+ standard-library compatibility, the 14,000-byte step-reading cap, and the 30,000-byte `jflow.py` cap stay intact.

## Non-goals
- Supporting GitLab, Forgejo, Bitbucket, or any host other than GitHub via `gh`.
- Auto-merging pull requests at `jflow done`.
- Mirroring `.jflow/` files in git alongside GitHub comments.
- Changing default `.jflow/` mode behavior for repositories that do not opt in.
- Adding third-party Python packages.

## Constraints
- Must not break: existing `.jflow/` mode on the five historical runs and four test suites; Python 3.9+ standard library only; 14,000-byte cap on `SKILL.md` plus each of `spec.md`, `build.md`, `check.md`, and `done.md`; 30,000-byte cap on `jflow.py`; locked rules `public_paid_needs_human`, `checker_read_only`, and `no_secrets`.
- Ask first: the structured comment marker format on issues and pull requests, the issue and pull request link convention, and the config schema for GitHub mode.
- Gate: none

## Proof
Rows 1 to 6 run `jflow.py` as a subprocess in scratch git repositories with no `.jflow/` folder and a stateful stub `gh` executable on `PATH`.

| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Issue number, GitHub issue URL, `git config jflow.mode github`, and `$JFLOW_CONFIG` enter issue and pull request mode with zero `.jflow/` files | `jflow.py` CLI | Run `jflow.py next --json` with `#42`, a GitHub issue URL, and a plain slug under `git config jflow.mode github` and `$JFLOW_CONFIG` | Exits 0 in all four cases, returns the expected step from stub `gh` state, and creates no `.jflow/` directory | new | red |
| 2 | A full run works through issue and pull request comments without editing an existing issue body or committing `.jflow/` files | `jflow.py` CLI | Drive an existing issue `#42` through `validate spec`, `record spec`, branch commit and draft pull request, `validate check`, `record check`, `fix`, clean `check-2`, `record done`, and `summary --json` | Every step exits 0, `next --json` routes `spec`, `build`, `check`, `fix`, `check`, `done`, `summary` matches counts and diff stats, original issue body stays unchanged, and `git status` shows no `.jflow/` files | new | red |
| 3 | Wait points, check cap, `[edge]`-only stops, and `## Accepted` SHA and order checks match `.jflow/` mode | `jflow.py` CLI | Drive `jflow.py next --json` across `Ask first` with `## Approach` and `Yes: approach`, `Gate:` and `Yes: gate`, `Human checks` and `Maybes` with `Yes: done`, a no-code-change rerun, `Checks allowed: 4`, `[edge]`-only defects, and wrong vs matching SHA `## Accepted` comments | Every wait point and `[edge]` stop returns `role: "human"`, each clearance unblocks only its own item or wait point, and the no-code-change rerun does not consume the cap | new | red |
| 4 | Staged or committed `.jflow/` files on the branch are refused in issue and pull request mode | `jflow.py` CLI | Stage and then commit `.jflow/42/notes.md` on the run branch, then run `jflow.py validate check #42` and `jflow.py next #42` | Both commands refuse the run with an error naming `.jflow/` | new | red |
| 5 | Editing the approved spec comment after `spec` is detected | `jflow.py` CLI | Mutate the stub `gh` spec comment body after `record spec`, then run `jflow.py validate check #42` and `jflow.py next #42` | Refuses or blocks the run because the spec changed after approval | new | red |
| 6 | Missing `gh`, unauthenticated `gh`, or no linked pull request fails cleanly without traceback or partial writes | `jflow.py` CLI | Run `jflow.py next #42` and `jflow.py record #42 check --model m --effort high` with no `gh` on `PATH`, with stub `gh` returning an auth error, and with no linked pull request | Exits non-zero with a single-line error naming the cause, prints no traceback, and writes no partial comment or file | new | red |
| 7 | Skill docs specify the issue and pull request workflow, blind `check`, untracked `drive.py`, non-merging `done`, and public-repo confirmation | Skill Markdown | Read `SKILL.md` and the issue and pull request mode reference under `.github/skills/jflow/` | Documents comment-on-existing vs new-issue spec, draft pull request build, blind `check` ignoring builder notes, untracked `drive.py`, ready-for-review `done` without merge, and confirmation before GitHub writes on public repos | new | red |
| 8 | All jflow scripts use Python 3.9+ standard library only | `python3` | Check non-local imports in `.github/skills/jflow/scripts/*.py` against `sys.stdlib_module_names`, and run `ast.parse` with `feature_version=(3, 9)` | Zero third-party imports and Python 3.9 AST parse succeeds for every script | keep | green |
| 9 | Historical `.jflow/` runs, the 14,000-byte step-reading cap, and the 30,000-byte `jflow.py` cap stay intact | `test_validate.py` | `python3 -I -m unittest discover -s .github/skills/jflow/scripts/tests -k test_next_and_summary_match_base_on_five_runs -k test_skill_size_and_agent_instruction` | Both tests pass with `OK` | keep | green |

## Human checks
- Run one end-to-end trial on a real GitHub repository using `gh` and confirm that issue comments, draft pull request comments, ready-for-review handoff, and public-repo confirmation prompts work as expected.
