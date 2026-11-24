# headless-done-wait-point
Status: ready
Base: 0fcb2e5
Serves: none

## Problem
Headless conductor runs abort with exit 1 (`no progress`) at `jflow done` whenever `done` asks to approve `PRODUCT.md`, `DESIGN.md`, `TODO.md` or `drive.py` verb edits. This forces a manual session resume and happened in 3 of 3 recent conductor runs: `hq-py39`, `jflow-issue-pr-mode` and a work-repo run on 2026-11-24. Separately, `jflow.py next --json` emits no typed `wait_point` field, so `conductor.py` relied on a regex against blocker prose that broke when blocker wording changed.

## Goals
1. When all Proof rows are proved or accepted with no open defect and `notes.md` has a `## Proposed edits` section without a `Yes: edits` line, `jflow.py next --json` stops with `step: "human"`, `role: "human"`, `wait_point: "edits"`, and a blocker that shows the proposed edits and asks the human to approve or change them. Once a line starting with `Yes: edits` is committed in `notes.md`, `next --json` routes back to `step: "done"` in the builder session.
2. `jflow.py next --json` emits a typed `wait_point` field on every wait point: `"approach"`, `"gate"`, `"done"` and `"edits"`. Non-wait-point human stops and non-human steps omit `wait_point` so historical `next --json` outputs stay unchanged.
3. A `Yes: <point>` line clears only its own wait point. A mid-run `jflow spec` invalidates earlier `## Proposed edits` and `Yes: edits` lines in `notes.md`, matching `Yes: approach` and `Yes: gate`.
4. Issue and pull request mode (`jflow_gh.py`) handles `## Proposed edits`, `wait_point` and `Yes: edits` identically to `.jflow/` mode.
5. `SKILL.md` and `references/done.md` document the `edits` wait point and `wait_point` JSON field. Interactive `jflow done` keeps asking in chat as today. An unattended `jflow done` that proposes `PRODUCT.md`, `DESIGN.md`, `TODO.md` or `drive.py` verb edits without `Yes: edits` writes them under `## Proposed edits` in `notes.md`, commits only `notes.md`, and stops. When `Yes: edits` is present, `done` applies those edits and finishes without waiting again.
6. Size caps and existing behavior stay intact: `jflow.py` stays at or under 30,000 bytes, `SKILL.md` plus each step reference stays at or under 14,000 bytes, Python 3.9+ standard library only, and all five historical runs match byte for byte.

## Non-goals
- Editing `conductor.py` or `conductor/SKILL.md`, which belong to the follow-up `conductor` run.
- Changing interactive `jflow done` chat questions when a human is in the session.
- Rewriting `jflow.py` beyond what is needed to stay under the 30,000-byte cap.
- Adding a new file in `.jflow/<slug>/` for proposed edits.

## Constraints
- Must not break: existing `.jflow/` mode and GitHub mode behavior; byte-for-byte `next --json` and `summary --json` equality on the five historical runs in `test_validate.py`; the 30,000-byte cap on `jflow.py`; the 14,000-byte cap on `SKILL.md` plus each of `spec.md`, `build.md`, `check.md` and `done.md`; Python 3.9+ standard library only; locked rules `public_paid_needs_human`, `checker_read_only` and `no_secrets`.
- Ask first: nothing.
- Gate: none.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | A run at `done` with `## Proposed edits` in `notes.md` stops cleanly with `wait_point: "edits"` and routes back to `done` after `Yes: edits` is committed | `jflow.py next --json` | In a scratch git repo with all Proof rows PROVED, commit `## Proposed edits` with proposed `PRODUCT.md` and `TODO.md` lines in `notes.md`, run `jflow.py next demo --json`, then commit `Yes: edits · "yes" · 2026-11-24` and run `jflow.py next demo --json` again | First call exits 0 with `step: "human"`, `role: "human"`, `wait_point: "edits"`, and the proposed lines in `blocker`; second call exits 0 with `step: "done"`, `session: "builder"`, and no `wait_point` key | new | red |
| 2 | `jflow.py next --json` emits typed `wait_point` for `approach`, `gate`, `done` and `edits`, and omits `wait_point` on non-wait-point stops and non-human steps | `jflow.py next --json` | In a scratch git repo, run `jflow.py next demo --json` at `approach`, `gate`, `done`, `edits`, check cap, BLOCKED row, `[edge]`-only defect, and `build` | The four wait points return `wait_point` equal to `"approach"`, `"gate"`, `"done"` and `"edits"`; the non-wait-point stops and `build` have no `wait_point` key | new | red |
| 3 | `Yes: edits` and `Yes: done` do not clear each other, and a mid-run re-spec invalidates earlier `## Proposed edits` and `Yes: edits` | `jflow.py next --json` | In a scratch git repo with Human checks and `## Proposed edits`, test `Yes: done` alone and `Yes: edits` alone; then edit `spec.md` body after `Yes: edits` and re-prove | `Yes: done` alone stops at `wait_point: "edits"`; `Yes: edits` alone stops at `wait_point: "done"`; after a mid-run re-spec, earlier `## Proposed edits` and `Yes: edits` neither trigger nor clear `edits` | new | red |
| 4 | Issue and pull request mode handles `## Proposed edits`, `wait_point` and `Yes: edits` identically to `.jflow/` mode | `jflow.py next --json` in GitHub mode | Run `jflow.py next #42 --json` against a stub `gh` repo with a proved receipt and a `notes` comment holding `## Proposed edits`, then add a `notes` comment with `Yes: edits · "yes" · 2026-11-24` | First call returns `step: "human"` and `wait_point: "edits"`; second call returns `step: "done"` and `session: "builder"` | new | red |
| 5 | `SKILL.md` and `references/done.md` document `## Proposed edits`, `Yes: edits`, `wait_point` and the unattended-vs-interactive rule | Skill docs | Read `.github/skills/jflow/SKILL.md` and `.github/skills/jflow/references/done.md` and grep for `Proposed edits`, `Yes: edits` and `wait_point` | `SKILL.md` names all four wait points and `wait_point` in `--json`; `done.md` keeps interactive chat questions unchanged, instructs unattended runs to commit `## Proposed edits` and stop, and instructs `done` to apply them when `Yes: edits` is present | new | red |
| 6 | Historical runs stay byte-for-byte identical, and script and skill size caps hold | `jflow.py` CLI and `test_validate.py` | Run `python3 -m unittest discover -s .github/skills/jflow/scripts/tests -p test_validate.py` | Exits 0 with all 14 tests OK; `jflow.py` is at most 30,000 bytes and `SKILL.md` plus each step reference is at most 14,000 bytes | keep | green |

## Human checks
- After both this `j-skills` run and the follow-up `conductor` run ship and `npx skills update -g` runs, verify one real `conductor` run whose `done` step proposes a doc or `TODO.md` edit stops with exit 2 and finishes after `conductor SLUG --answer yes`.

## Accepted
- Row 3 · after a re-spec, a proposal deleted then reposted, or trimmed, can skip its edits stop · "A" · 2026-11-24 · 0de041566c30f6a341e14ae018a07ead145f6153
- Defect 1 · cleanup commit then identical repost after re-spec returns done · "A" · 2026-11-24 · 0de041566c30f6a341e14ae018a07ead145f6153
- Defect 2 · trimmed proposal with its stale yes removed after re-spec returns done · "A" · 2026-11-24 · 0de041566c30f6a341e14ae018a07ead145f6153
