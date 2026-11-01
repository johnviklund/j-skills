# After moving text, relative pointers in moved and kept files go stale
Applies when: writing or reviewing a ticket that moves text between or within docs.
Root cause: a sentence ledger proves no sentence was lost, not that "above", "below", "step N" or "this file" still point at the right place.
Fix: in the ticket that moves text, grep those words in every moved and kept file and read each hit in place; also grep each renamed heading and file name.
Evidence: lean-skill-hubs (C1-2, five stale pointers left by the moves, found in review)
Occurrences: 1 · Last confirmed: 2026-10-28 · Status: active
Enforced by: judgement
<!-- memory.compact 2026-11-01: converted from the legacy workflow/MEMORY.md entry "After moving text, grep every relative pointer in the moved and kept files". -->
