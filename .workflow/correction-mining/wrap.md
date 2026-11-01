Command: workflow wrap correction-mining
Created: 2026-11-02 · Sonnet 5.5
Base:    77efe6d
Inputs:  review.md @ 77efe6d
Status:  done

## Outcome
`python3 .github/skills/checkup/scripts/corrections.py` reads the Claude, Codex and Copilot transcript stores and prints repeated denials and interrupts plus the redirect turns to stdout; it writes no file. `checkup` reports the top 5 repeats and `retro` cites a matching repeat in its *Recurring* test. Review: ship as-is after 2 cycles.

## Shipped
- T1 interrupts from Claude transcripts: 00623b1
- T2 Codex and Copilot readers, denials, redirects: a5cd7fc
- T3 `checkup` and `retro` call the script: 5683806
- C1-T1 unmatched quote in a denied command: eecbc49 (red test), 9911caa (fix)
- C1-T2, C1-T3 mutation survivors covered: c3a6606, f7c04bf

## Review
2 cycles. Cycle 1: 2 P1 (C1-1 crash on an unmatched quote, C1-2 15 of 48 mutants survived), fixed. Cycle 2: clean, 22 of 22 mutants red.

## Deferred
- C2-1 (P2): a record of an unexpected shape still kills the whole report → `TODO.md`, Review deferrals.
- 5 P3 stay in `review.md` (command-head keys, subfolder sessions, Codex `wait`, unobserved denial shape, control characters).

## Learnings
3 lines routed: `parser-tests-need-real-file-and-both-sides` (now 2 occurrences), `fix-guard-needs-firing-test` (now 9).

## Receipts
`receipts/execute-verification.md`, `receipts/cycle-1-verification.md`.

Product docs: no `PRODUCT.md` or `DESIGN.md`; `ROADMAP.md` step 3 archived to `ROADMAP_ARCHIVE.md`.
Retired: none — the run replaced no existing code path.
