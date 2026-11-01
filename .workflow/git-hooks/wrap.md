Command: workflow wrap git-hooks
Created: 2026-11-01 · Claude Sonnet 5.5
Base:    a152e3e
Inputs:  review.md @ a152e3e
Status:  done

# git-hooks — wrap

Outcome: the two mechanical ground rules are now enforced by git hooks. `hooks.py` installs a
pre-commit hook that runs `check-run.py` when staged paths are under `.workflow/<slug>/`, and a
pre-push hook that runs gitleaks over the commits the push adds. `bootstrap` installs them,
`checkup` flags a repo without them or without a `--no-verify` denial, and the hook finds
`check-run.py` through a stub that searches the README's install folders. Net code +157, tests +246
(ratio waived for the run, see `plan.md` Deviations).

## Shipped
- T1 install + pre-commit gate · f1ed6eb
- T2 pre-push secret scan · 2556e51
- T3 checkup reports missing hooks and open `--no-verify` · cb2e649
- Patch cycle 1: a2d308f (spaced push target), d6de8e2 (mutants), 8667607 (manual fallback), 1c09a05 and fb9bf81 (denial probes, dropped rule)
- Patch cycle 2: 0cf89fa (scan commits absent from the named target), ffc3856 (unknown revision test), 3368007 (each denial probe alone)

## Review
Ship as-is after 3 cycles, 0 open @ a152e3e. Opus 5.5 reviewed GPT-6.1 Sol's code.

## Deferred
- C1-6 and C2-4 (P3) and C3-1 (P3, `--remotes=<name>` glob; URL pushes skip every remote): stay in `review.md`, no TODO line.
- This repo has no hooks installed yet; installing them is checkup's opt-in fix (human's call).

## Routed
- Learnings: guard added by a fix needs a firing test → `memory/fix-guard-needs-firing-test.md` (2nd occurrence); C2-1 missed range exclusion → private exam set (cap 10; stream-whitespace case dropped as a case gap).
- ROADMAP row 1 → `ROADMAP_ARCHIVE.md`; row 2 `retire-on-no-signal` is next. No PRODUCT.md or DESIGN.md; no verify skill.

## Receipts
`receipts/` holds execution, c1 and c2 verification output.

Retired: none — the run adds hooks and replaces no code path, flag or harness.
