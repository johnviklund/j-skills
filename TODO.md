# TODO

Archived items: see TODO_ARCHIVE.md (grep it).

## jflow
- Guardrail: structure — emit a typed `wait_point` field (`"approach"`, `"gate"`, `"done"`, or `null`) in `jflow.py next --json` so drivers stop scraping blocker prose · must fail on 4a7487c (make room under `jflow.py`'s 30,000-byte cap first)
- Headless done wait point — `jflow done` writes proposed `PRODUCT.md`, `DESIGN.md`, or `drive.py` verb edits under `## Proposed edits` in `notes.md` and stops; `jflow.py next` returns `wait_point: "edits"` until `Yes: edits` is committed (hq-py39 retro)
- Unpushed commits on Human checks stop — `jflow.py next` adds an `Unpushed: N commits ahead of <upstream>` detail line when `@{u}..HEAD` has commits (hq-py39 retro)

## Simplify
- Worktree setup as a script — run a committed `.worktree-setup` instead of parsing `## Worktree setup` from AGENTS.md; the parser drew 5 of 17 run-worktrees findings

## Review deferrals
- `jflow-config`: Unsupported flags or invalid `--session` values can echo key-like text in stderr; nothing is recorded. The human kept this existing behavior on 2026-11-08.
- `receipt-evidence-cap`: Measure the next three trial runs. Every Evidence cell and defect `Evidence:` part must be at most 240 characters, and each receipt under 3 KB. A work-repo run done 2026-11-17: every Evidence cell at most 240 characters; all 15 receipts over 3 KB, 3.0 to 7.7 KB, mostly Maybes.
- `check-scope`: After five runs, measure row 1 with `jflow.py summary --json` and receipt sizes: median checks a run under 3.5, Maybes under 1.7 a check, no check rerun without new input, every receipt under 3 KB. Also judge whether check still catches real defects. Accepted at done on 2026-11-17: a numbered list under a bare `Checks allowed:` heading can override the cap line above it.
- `check-reach`: After five runs, judge whether edge-only stops replaced fix rounds without hiding a real bug. `jflow.py` is at 29,987 of its 30,000 bytes, so the next change to it must make room.
- `jflow-validate`: Revisit non-template BROKEN citation lists and leading-zero defect IDs if needed; check-3 records the limits kept at done on 2026-11-10.
