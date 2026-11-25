# TODO archive

- Worktree setup as a script — run a committed `.worktree-setup` instead of parsing `## Worktree setup` from AGENTS.md; the parser drew 5 of 17 run-worktrees findings — dropped: the worktree parser went with workflow · 2026-11-24 · delete-workflow

- Guardrail: structure — emit a typed `wait_point` field (`"approach"`, `"gate"`, `"done"`, or `null`) in `jflow.py next --json` so drivers stop scraping blocker prose · must fail on 4a7487c (make room under `jflow.py`'s 30,000-byte cap first; promoted to `ROADMAP.md` under `headless-done-wait-point`) — done 2026-11-24 · headless-done-wait-point

- Headless done wait point — `jflow done` writes proposed `PRODUCT.md`, `DESIGN.md`, or `drive.py` verb edits under `## Proposed edits` in `notes.md` and stops; `jflow.py next` returns `wait_point: "edits"` until `Yes: edits` is committed (promoted to `ROADMAP.md` under `headless-done-wait-point`; 3 of 3 conductor runs hit exit 1 at done: `hq-py39`, `jflow-issue-pr-mode`, and a private-repo run on 2026-11-24) — done 2026-11-24 · headless-done-wait-point

- `spec-why`: the jflow skill is at 49,995 of the 50,000 bytes (2026-11-17) its size test allows. Before the next jflow change, decide whether to raise the limit or split the text; `ROADMAP.md` item jflow-size-room. — done 2026-11-17 · jflow-size-room

- `receipt-evidence-cap`: Decide whether an escaped pipe counts as one or two characters toward the evidence cap. Counting stays unspecified at close. — done 2026-11-10 · jflow-validate

- `drive-py-at-done`: On the next run that reaches `done` with a `drive.py`, confirm the done commit deletes it and any reusable verb is one `TODO.md` line. — done 2026-11-08 · jflow-config

- `check-run.py`: `check_worklog` reads only a repo-root `WORKLOG.md`; this repo's worklog is `.github/skills/workflow/WORKLOG.md`, so a done run errors "no entry" (seen at run-sizing wrap). — archived 2026-10-18 · 9974505 (growth-ratchets T2 moved the worklog to the root)
- growth-ratchets C1-2 (P2, 2026-10-18) — the execute doc dropped two rules to stay at net zero lines; restore them and measure doc growth in words. — archived 2026-10-18 · e478a17 (guard-keys T1)
- `check-run.py`: retire the date gates (`SLOP_SINCE`, `SIZING_SINCE`, `LEAN_SINCE`, `GROWTH_SINCE`) and their legacy branches; check only runs not yet done (2026-10-18). — archived 2026-10-18 · moved to workflow ROADMAP.md step 2 (`retire-date-gates`)
- workflow `SKILL.md:54` live-run grep misses briefs written `Status:  complete` (two spaces); six briefs affected, so `workflow status` skips them (P2). — archived 2026-10-28 · 27f1f39 (run-worktrees T4)
- checkup-next-actions C1-1 (P1, 2026-10-25) — Guardrail: a small script prints the card's `Model:` and `Fallback:` lines for a command from ROUTING.md and checkup copies its output; needs its own tests (run-sized). — archived 2026-10-30 · a354025 (next-step T5: `next-step.py --key` prints the Model and Fallback lines)
- unattended-mode C3-1 (P1, 2026-10-30) — `test_run_worktree.py:149-152` fixture holds one `decisions.md` row, so `any`→`all` at `run-worktree.py:100` survives; add a `plan` row before the execute row (human approved deferral) — archived 2026-10-31 · 893682d (fixture leads with a `plan` row; the `all` mutant now fails)
- unattended-mode C3-2 (P2, 2026-10-30) — `run-worktree.py:213` catches `RuntimeError, OSError, CalledProcessError` but `checks.decisions` raises `ValueError` on a bad row, so `open` can crash on a malformed `decisions.md` — archived 2026-10-31 · 893682d (`ValueError` caught; `open` exits 1 naming the row)
