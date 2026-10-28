Command: workflow review lean-skill-hubs · patch cycle 1
Created: 2026-10-28 · claude-opus-5-5
Base:    c4aa5a7
Inputs:  .workflow/lean-skill-hubs/review.md @ c4aa5a7
Status:  complete

## Execution state
Current: C1-T2 todo · writer: GPT-6.1 Sol
C1-T1 @ 2f648a8
Proof: ledger 3 OK; M12 killed in a throwaway copy; sentence-ledger.py unchanged.
Uncommitted: this execution record · pending decision: none

## Tickets

### C1-T1 — The ledger flags a contents list below line 12
Delivers: B3 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +0 · tests +4
Seam: `test_reference_disclosure` in `.workflow/lean-skill-hubs/scripts/test_sentence_ledger.py`; `sentence-ledger.py:73`
Change: a test-only fix. Add one case: a linked 101-line `references/c.md` whose `Contents:` line is line 13 → exit 1 and `references/c.md: missing contents`. The script stays unchanged.
Accept:
- [x] the new case passes, and `lines[:12]` → `lines` in a throwaway copy turns the suite red (B3)
- [x] the commit changes no line of `sentence-ledger.py` (B3)
Verify: `cd .workflow/lean-skill-hubs/scripts && python3 -m unittest test_sentence_ledger` (pre: 3 OK, M12 survives)
Skills: none
Status: done @ 2f648a8
Writer: GPT-6.1 Sol

### C1-T2 — Pointers left by the moves name where the text now lives
Delivers: B2, B4 · Blocked by: none · Lane: mechanical
Fixes: C1-2 (P3)
Budget: code +6 · tests +0
Seam: the five lines in review.md C1-2 (a)–(e); the ledger with `notes/dups-*.txt`
Change: (a) "in step 2" → "below" · (b) "The repeat rule above" → "The repeat rule in `SKILL.md`" · (c) "commands like the following" → "commands like the ones each section lists" · (d) "need only this file and `ROUTING.md`" → "need only `worktrees.md` and `ROUTING.md`" (+3 bytes; the hub is read anyway) · (e) delete the bullet at `phase-3-execute.md:29` and its blank line. Each changed hub sentence of Base gets a `notes/dups-<skill>.txt` row (removed sentence · path · its new phrase), so the ledger still accounts for it.
Accept:
- [ ] `grep -rc` of `naming-collision rule in step 2`, `repeat rule above`, `commands like the following`, `need only this file and` and `Commit after each verified ticket` over `.github/skills` → 0 each (B4)
- [ ] ledger vs ed2c63b for workflow, memory.remember, checkup → `unaccounted 0`, exit 0; `wc -c` workflow `SKILL.md` ≤ 11,500 (B1, B2)
Verify: `for s in workflow memory.remember checkup; do python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/$s ed2c63b; done && wc -c .github/skills/workflow/SKILL.md` (pre: unaccounted 0 ×3 · 11494)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo
