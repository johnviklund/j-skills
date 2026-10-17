Command: workflow wrap lean-runs
Created: 2026-10-17
Base:    4a085e5
Inputs:  review.md @ 4a085e5
Status:  done

## Outcome
Workflow runs now have hard size limits. `check-run.py` errors when a brief has more than 8 behaviours, or a plan more than 20 acceptance lines, unless a `Split declined by human:` line is present. It also errors when a logic or contract ticket's tests grow past 1.5× its code, and warns when a Budget is high with no `why:`. Runs created before 2026-10-18 keep the old rules (3× ratio, logic lane only). The plan, execute and tests references now ask for one test per behaviour, not one per acceptance line.

## Shipped (ticket → commit)
T1 3c64d1b (size limits) · T2 c07710e (1.5× ratio, Budget reasons) · T3 2b6835a (docs)
Patch cycle 1: C1-T1 e92cdbe (test for the old-run lane gate)

## Review
Cross-vendor (writer GPT-6.1 Sol, reviewer Opus 5.5). 2 cycles: C1 found one P1 (C1-1), fixed; C2 ship as-is, 0 open.
Three P3s (C1-2 to C1-4) deferred; they stay in review.md.

## Deferred / routed
- No learnings.md; nothing routed. No eval case deposited (C1-1 offered to the human at wrap).
- No PRODUCT.md or DESIGN.md; workflow ROADMAP.md unchanged. No feature map. TODO.md unchanged.
- Known: check-run's `check_worklog` reads a repo-root WORKLOG.md, so this done run reports one
  "no entry" ERROR (open TODO.md item). The entry is in `.github/skills/workflow/WORKLOG.md`.
- Codex copy needs `npx skills update -g` after push to pick up the new checks.

## Receipts
`receipts/t1-verification.md`, `receipts/t2-verification.md`, `receipts/t3-verification.md`,
`receipts/t3-net-lines.txt`, `receipts/c1-t1-verification.md`, `notes/evidence.md`.

Final checks: 38/38 tests pass; receipt-rule diff 4a085e5..HEAD empty; shortcut grep clean.
Wrap commits: 6474032 (.gitignore for __pycache__/) · 5d5eba7 (WORKLOG entry).
Retired: none — LEGACY_TEST_RATIO and the date gate still serve runs created before 2026-10-18
