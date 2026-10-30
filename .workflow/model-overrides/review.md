Command: workflow review model-overrides
Created: 2026-10-30 · Opus 5.5
Base:    ad0afd9
Inputs:  .workflow/model-overrides/plan.md @ 43bd7b2
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing: four `test_override_*` cases in `test_next_step.py:67-116`, `test_override_validation` in `test_check_run.py:104`; Verify 30 OK · 53 OK
- [x] T2 — acceptance 3/3: `grep -c 'routing\.md'` SKILL.md 2 · MAINTAINING.md 1 · README.md 1; `wc -l < SKILL.md` 180
- [x] B1…B6 delivered · Outcome observed on the card and JSON of a scratch run against the real `ROUTING.md`, manual (no verify skill, no user surface beyond the CLI): override shows `GPT-6 Sol · xhigh · standard (override)`, fallback unchanged, a header-only `routing.md` leaves the card byte-identical · out of scope untouched
- [x] .workflow/ dependency check — the only hits are next-step.py and run-worktree.py, which read run folders by design; this diff adds none
Size: +54 code · +65 tests · ratio 1.20 · net +103 · over 1,000: none
Reachability: no new file; `overrides` and `PHASE_COLUMNS` called from `check_run` (check-run.py:815-818) and `next_step`/`routing` (next-step.py:18, :111) · guards shown failing: 19/19 mutations — unknown key, effort guard, header exemption, routing branch, ARTIFACTS entry, Effort cell, file read, writer prefixes `execute:` and `fix:`, reviewer keys `plan` and `review`, overlap always and never, `(override)` suffix, blocker pop, trial reset, card warning line, step warning, override flag
Independence: cross-vendor — writer GPT-6.1 Sol (OpenAI), reviewer Opus 5.5 (Anthropic)
Threats: none — the diff reads one more local run file and prints text; no outside input, shell, network, auth or permission
Tests: workflow 117 OK · checkup 8 OK · existing test files only gain lines · escape-hatch scan: none · new dependencies: none

## Cycle 1 findings

### P2 — A done run's routing.md breaks next-step and check-run after a ROUTING.md key change
- Evidence: done runs stay in `.workflow/<slug>/` for good (`wrap.md:185`), so plan Risks' "wrap archives runs" premise is false. Repro: done brief + `routing.md` row `execute:logic`, then `ROUTING.md` renames that key → `next-step.py x` exits 1 `unknown routing key` instead of the ✅ Done card, and `workflow status` runs next-step on every slug (`worktrees.md:27`); `check-run.py --all` prints an ERROR beside its own `done run: only header, sha and layout checks apply` note. Sites: next-step.py:107-116 parse before the brief status is read; check-run.py:815-820 sit outside the `rep.done` branch
- Disposition: fix now — small: skip the override for done runs at both sites, one red test first
- Resolved: —

### P2 — Review and execute look up a run's models only in ROUTING.md
- Evidence: decision 2a lets an override name any `Vendor · Model`, and README.md:210 offers `routing.md` for "one run's model", but `phase-4-review.md:6-7` looks up each writer's vendor in `ROUTING.md` and `phase-3-execute.md:138` writes the model "as `ROUTING.md`'s seat mapping names it". Input: `| execute:logic | Google · Gemini 4 | high |` → the writer has no name to copy and the reviewer finds no vendor to judge independence by
- Disposition: fix now — small: both lines name the run's `routing.md` first
- Resolved: —

### P3 — An empty routing.md reports `missing None table`
- Evidence: `table()` puts `heading` in its message (check-run.py:171); decisions.md shares the wording
- Disposition: defer
- Resolved: —

### P3 — check-run's routing.md ERROR repeats the absolute path after the relative one
- Evidence: check-run.py:820 passes `str(error)`, which already starts with `doc.path`; decisions.md at :814 does the same
- Disposition: defer
- Resolved: —

### P3 — SKILL.md grows further past its ~10 KB budget
- Evidence: 11,258 B → 11,478 B (`MAINTAINING.md:98`); the line count held at 180 as F11 planned
- Disposition: defer
- Resolved: —

## Pre-existing / environmental
- The installed skill copy lags this repo until `npx skills update -g` runs after the push (AGENTS.md); this review ran the repo's scripts.

## Cycle 1 verdict
Acceptance holds: every T1/T2 line is tested or grepped, B1–B6 hold, and the card shows the override on the real `ROUTING.md`. Defects: two small P2s, fixed now in patch cycle 1 (`patch_plan.md` C1-T1, C1-T2); three P3s stay here. No P0/P1.
