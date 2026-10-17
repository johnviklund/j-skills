P1 — which ratio rule flags real test bloat but not rewrites and moves?
Variants (61 done logic/contract tickets in cx-intelligence runs from 2026-10-09, `done @` commits, receipts excluded):
added-rule (today: tests added vs code added) · net-rule (tests net vs code net) · hybrid (tests net vs code added). All use ≥ 50 lines and 1.5×.
Script: `prototypes/P1-net-ratio/measure.py <repo>` (read-only, git numstat). Run on cx-intelligence @ 573dfe16.
Result: flags 22 · 21 · 18. On governed-execution-discovery T2 (tests +201 −305), T3 (+252 −128) and T4 (+116 −18, code +84 −24): added flags T2, T3; net flags T4 only (deleted code shrinks its denominator); hybrid flags none.
Waiver reach: 15 of the 22 added-rule flags sit on tickets named under `## Deviations`, which skips the check.
Run level (hybrid, tests net vs 1.5× code added, ≥ 100): 5 of 12 runs flag; governed-execution-discovery does not (tests net 150, code added 366).
