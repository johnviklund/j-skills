Command: workflow wrap retire-on-no-signal
Created: 2026-11-01 · claude-sonnet-5-5
Base:    3c4ac2c
Inputs:  .workflow/retire-on-no-signal/review.md @ 3c4ac2c
Status:  done

## Outcome
A skill-change trial that ends with no signal is no longer kept by default. `checkup/scripts/skill-trials.py` counts `[saved→skill]` tags per `SKILL-IMPACT.md` row, judges finished trials by saves and `Run:` numbers, and lists the rest as removal candidates for `workflow improve`. `--sweep` labelled all 37 open trialing rows; the human confirmed each choice (`notes/t3-choices.md`, `decisions.md`) and nothing was removed.

## Shipped
- T1 save tags counted per row, `--sweep` labels · 3aeab1c
- T2 finished trials judged by saves and worklog numbers · 1ad5a7d
- T3 sweep applied, 37 choices recorded · dcaedc4
- Patch cycles: C1 953e4ac 59bd7be 7fa0e3d fb6e29b c76edeb · C2 a8b72da 25a4739 · C3 2dc5056

## Review
Cross-vendor (GPT-6.1 Sol wrote, Opus 5.5 reviewed). Ship as-is after 4 cycles, 0 open. Worst finding: archive rows with `\|` crashed the report (P0, fixed). Final suites: workflow 124 OK, checkup 25 OK.

## Deferred
- C1-6 four minor P3 gaps stay in `review.md`.
- Installed `checkup` lacks `skill-trials.py` until `npx skills update -g` runs after the push.

## Receipts
`receipts/` (per-ticket verification, `t3-sweep.txt`, `t3-handoff.md`) · `notes/t3-choices.md`.

## Routed
Learnings: 4 lines → `memory/parser-tests-need-real-file-and-both-sides.md`; 1 eval case deposited in the private exam set (oldest case dropped at the cap). Roadmap step 2 → `ROADMAP_ARCHIVE.md`; `ROADMAP.md` step 3 now next. `PRODUCT.md`, `DESIGN.md`: none exist. No verify skill. `TODO.md`: no change.

Retired: none — the script and its docs are new and replace no code path
