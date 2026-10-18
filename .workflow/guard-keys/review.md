Command: workflow review guard-keys
Created: 2026-10-18
Base:    b98bb26
Inputs:  .workflow/guard-keys/plan.md @ bbf2d45
Status:  done

## Coverage
- [x] T1 — acceptance 6/6 checked: T1's Verify rerun at b98bb26 prints nine 1s, net 5, width 0, trial 1, exit 0
- [x] B1–B6 delivered · Outcome observed in the repo copy of the three references and `SKILL-IMPACT.md:12`, read by hand; no verify skill, and none is needed for a doc-only run · out of scope untouched: the diff touches only the three references and `SKILL-IMPACT.md`
- [x] B3 wording matches `9974505^:phase-3-execute.md:92-95` word for word; B4's waiver lines keep their meaning (`phase-3-execute.md:97-100`)
- [x] .workflow/ dependency check: 0 hits
Size: +0 code · +0 tests · ratio n/a (every touched file is `*.md`) · net +5 reference lines (+17 −11 with `SKILL-IMPACT.md`) · over 1,000: none
Reachability: no new file · guards shown failing: M2, M3, M4 (below)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Escape-hatch scan: 1 hit, `: any` in the `SKILL-IMPACT.md` row's prose ("Judge: any"); not code
Regression proof: the receipt-rule diff bbf2d45..HEAD is empty, so no suite run is needed

Mutations, each in a throwaway worktree and rerun through T1's Verify:
- M1 delete ", differing only in that key" from `tests.md:33` → Verify stays green (P3-1)
- M2 split `Ratio waived: T# — <reason>` across two lines → that grep prints 0
- M3 "mutate each" changed to "mutate one" → that grep prints 0
- M4 drop "the ticket continues" → that grep prints 0
- M5 "list every key" changed to "ask the writer to every key" → Verify stays green (P3-1)

## Cycle 1 findings
### P3-1 — Verify checks one phrase of B1 and B2, not their whole rule
- Evidence: M1 and M5 above stay green. The shipped text is correct, read at `tests.md:32-33` and `phase-4-review.md:48-49`.
- Why P3: a doc grep runs once and guards nothing after the run, so a fix ticket would change no file a reader uses. The gap repeats this run's own problem: the Verify guard has two keys per behaviour and tests one.
- Disposition: defer (stays in `review.md`); one line in `learnings.md`
- Resolved: —

### P3-2 — the writer rule sits in the deny-list paragraph
- Evidence: `tests.md:30-34` opens "A deny-list gets a case per form". A writer adding a keyed waiver, which matches rather than blocks, may skip that paragraph. Plan F2 chose this place on purpose to reuse the per-line sentence.
- Disposition: defer (stays in `review.md`); the trial judge in `SKILL-IMPACT.md:12` will show whether writers miss it
- Resolved: —

### P3-3 — the reviewer rule fires only after a key is found untested
- Evidence: `phase-4-review.md:48` says "If one guard key is untested". A reviewer whose one mutation hits a tested key never learns of the others. This matches B2 as agreed, and it would have caught growth-ratchets C2-1 in cycle 1.
- Disposition: defer (stays in `review.md`); the trial judge covers it
- Resolved: —

## Pre-existing / environmental
- `check-run.py --all` warns that the archived slop-guards plan has 127 lines against ~120. It predates this run.
- `~/.claude/skills/workflow` links to the installed copy `~/.agents/skills/workflow`. All three references there still differ from the repo, so readers get the change only after wrap runs `npx skills update -g` (plan F1).

## Cycle 1 verdict
Ship as-is. 0 P0 · 0 P1 · 0 P2 · 3 P3, all deferred. Next: `workflow wrap guard-keys`, which drops the C1-2 deferral from `TODO.md` (D3), marks the `MEMORY.md` guard-key entry as promoted (D4) and refreshes the installed copies.
