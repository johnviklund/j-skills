Command: workflow wrap lean-skill-hubs
Created: 2026-10-28
Base:    f80148f
Inputs:  .workflow/lean-skill-hubs/review.md @ f80148f
Status:  done

## Outcome
Six skill hubs (`memory.remember`, `memory.compact`, `workflow`, `checkup`, `understand`, `verify`) now keep in `SKILL.md` only what every run needs. Branch-only text moved to linked `references/` files, so a run loads less. A sentence ledger shows every removed sentence as moved or duplicated, and none unaccounted. Installed copies under `~/.agents/skills/` match the repo.

## What shipped
- T1 → 526f6a4, 46d79f0: sentence ledger and its tests (run script, in `.workflow/`)
- T2 → f7a16ad: memory.remember 27,506 to 19,132 bytes, three references
- T3 → efc114a: memory.compact 17,119 to 14,422
- T4 → fb6a5d2, b9cb0f2: workflow hub 13,238 to 11,499, `secret-scan.md`
- T5 → b640a54: checkup 23,975 to 6,058, six scope references
- T6 → 6973783: understand 15,230 to 11,984, `pictures.md`, `video.md` moved
- T7 → 076d68d: verify 14,934 to 2,914; `SKILL-IMPACT.md` trial row
- T8 → 778f70f: operator install, seven copies identical
- C1-T1 → 2f648a8, C1-T2 → be06046: patch cycle for review C1-1 (P1) and C1-2 (P3)

## Review
Cross-vendor (GPT-6.1 Sol wrote, Opus 5.5 reviewed). Ship as-is after 2 cycles, 0 open. Cycle 1 found an untested ledger window (P1) and five stale pointers (P3); both fixed.

## Deferred and routed
- Nothing deferred. No P2 findings, so `TODO.md` is unchanged.
- Two lessons routed to `.github/skills/workflow/MEMORY.md` @ 9b4f63e (a bumped page and a new page).
- Eval deposit: none. C1-1 is a missing test in a run script, a shape the exam set already holds (`missed-assistant-privacy-guard-has-no-test`).
- Product docs: none exist. Feature map: no verify-* feature directory. `TODO.md` size 476 bytes.
- Final checks: workflow 81 OK, checkup 8 OK, ledger 3 OK, `check-run.py --all` 0 errors.

Retired: none — text moved to references, no code path, flag or shim was replaced

## Receipts
`receipts/` (t8-handoff.md, t8-install.txt, c1-install.txt) · `notes/` (five `dups-*.txt` ledger inputs) · `scripts/` (sentence-ledger.py and its test). Worklog entry in `WORKLOG.md`; trial row in `workflow/SKILL-IMPACT.md`.
