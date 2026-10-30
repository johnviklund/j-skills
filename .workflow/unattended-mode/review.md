Command: workflow review unattended-mode
Created: 2026-10-30 · Claude Opus 5.5
Base:    f719a10
Inputs:  .workflow/unattended-mode/plan.md @ b02cf59
Status: complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing: `test_check_run.py:104-122` (both modes clean with `0 errors · 0 warnings`; `Mode: sometimes`, `maybe` and the 5-cell row exit 1 with an ERROR naming Mode, D2, D3); `test_next_step.py:84-105` (assumed and answered equal the no-file baseline for a todo and an awaiting-human ticket; waiting D2 gives the blocker, model None and the card line; first waiting row beats D3). Existing assertions edited: 0 (`test_check_run.py` changes only the `check()` helper, +2/−2)
- [x] T2 — acceptance 5/5 re-run: 1 · only `references/unattended.md` · 5 Always-stop bullets · 1 · 1; `Version 2.1` → 0
- [x] B1–B7 delivered; B8's README half delivered, its ROADMAP half is wrap step 5 (plan F7) · Outcome observed on `next-step.py --json` and the card in a throwaway worktree copy of this run set to `Mode: unattended`: a waiting row → `blocker {decision: D1, …}`, model null, `**Model:** human · …`; the row set to answered → JSON byte-identical to the no-file run; `Mode: sometimes` → `ERROR brainstorm.md:6` · manual CLI run, no verify skill · out of scope untouched: no conductor or T3 tool (unattended.md names only "an outside conductor"), phase-0 gains only the header line, no decision model
- [x] Shared parser swap (exam-set class): `table()` moved unchanged except its message (`check-run.py:149-171`); routing still passes a heading, so its section end is unchanged; `decisions` reads the whole headerless file
- [x] .workflow/ dependency check — hits only in the workflow skill's own state-machine scripts, which exist to read runs; the new one (`next-step.py:177`) mirrors `:141`
- [x] Escape-hatch scan — 0 hits · New dependencies — none · Ratio waived — none
- [x] Verify the verification: 19 mutations in a throwaway worktree against the two new tests: Mode key inverted, `attended` dropped, `unattended` dropped, Mode check skipped, each of `assumed`/`waiting`/`answered` dropped, status check inverted, cell count unchecked, every cell required, header exemption removed, validation call skipped, ARTIFACTS entry removed, heading-None branch removed, waiting inverted, answered also blocks, first-waiting `break` removed, blocker never set → 18 killed; deleting the `reads` append (`next-step.py:177`) survives (C1-2). Worktree removed.
- [x] Suites: workflow 111 OK · checkup 8 OK
Size: +53 code · +45 tests · ratio 0.85 · net +67 (−31, mostly the moved parser) · over 1,000: none (check-run.py 882)
Reachability: `references/unattended.md` ← `SKILL.md:24`, `README.md`; `checks.table` ← next-step `routing` and `decisions`; `decisions` ← `check_run`, `next-step.py:174` · guards shown failing: the 18 above
Independence: cross-vendor (writer GPT-6.1 Sol, reviewer Claude Opus 5.5)
Threats: conductor or human → `decisions.md` · who: anyone who can commit to the run folder (human, conductor, a phase agent) · reaches: next-step reads only ID, Status, Question (`next-step.py:172-178`); Answer reaches only the next phase, as data (`unattended.md:29`) · changes: sets or clears the card's human stop; `*.md` is a receipt, so no code or review state moves (`check-run.py:65`) · logged: the row in git history · fails open: an `answered` row clears the stop whatever its Answer (C1-3), but P0/P1 deferral and cycle 3 still need their check-run-enforced approval fields; a malformed file fails closed (next-step exits 1) · worst case: a conductor answers an always-stop row and the agent copies it into `Approved by human:` (C1-5)

## Cycle 1 findings
### P2 — An unattended UI stop has no rule for the uncommitted ticket
- Evidence: `unattended.md:21-22` tells every Always-stop case to "save and commit the phase's progress … and push", but the UI stop (`unattended.md:36`, `phase-3-execute.md:52`) must come before the ticket's commit. Nothing says the ticket's code stays uncommitted, and in the fresh session that resumes after the answer, `SKILL.md:151-153` treats dirty paths no run commit touched as the human's own work. Failing input: an unattended execute reaches a UI ticket at green → it commits and pushes unapproved UI code (to the primary branch for a primary-checkout run), or leaves it for a session told to ignore it.
- Disposition: fix now (small, Markdown only) → C1-T1
- Resolved: —

### P2 — The `decisions.md` entry in the card's Reads has no test
- Evidence: deleting `next-step.py:177` (`step["reads"].append(…decisions.md)`) keeps the suite green; `test_next_step.py:99-102` asserts the blocker, model and card Model line, not Reads. Not a guard, and no B# names Reads, so P2; one assertion closes it.
- Disposition: fix now (small, test only) → C1-T2
- Resolved: —

### P3 — An `answered` or `assumed` row with an empty Answer passes
- Evidence: `check-run.py:174-179` checks only Status; `test_check_run.py:107` treats `assumed` with an empty Answer as clean, though `unattended.md:17-18` says to write the chosen answer. `| D1 | review | Defer C1-1? | fix now | answered | |` clears the blocker. `unattended.md:28-29` (keep it waiting while approval is missing) and the approval-field checks limit the harm.
- Disposition: defer (stays here)
- Resolved: —

### P3 — A done run hides a waiting row
- Evidence: `card()` returns ✅ Done before it reads the blocker (`next-step.py:61-62`), and neither wrap nor check-run refuses `Status: done` while a row is `waiting`.
- Disposition: defer (stays here)
- Resolved: —

### P3 — An answer does not say who gave it
- Evidence: the table has no "by" column (`unattended.md:45-47`), and `:27-28` has the agent copy an answer into `Approved by human:`. Worth settling before the roadmap's decision-model step answers rows.
- Disposition: defer (stays here)
- Resolved: —

### P3 — The hub's state table has no waiting-decision row
- Evidence: `SKILL.md:46-53` routes by ticket and finding state only; a waiting decision is routed only by next-step and `unattended.md:23-24`.
- Disposition: defer (stays here)
- Resolved: —

1 more P3: a `decisions.md` with no table reports `missing None table` (`check-run.py:170`).

## Pre-existing / environmental
none

## Cycle 1 verdict
Patch cycle 1 · fix C1-1, C1-2. P0 0 · P1 0 · P2 2 (small, fix now) · P3 5 (deferred, stay here). Every acceptance line is tested and passing, 18 of 19 mutations are caught, and the Outcome shows on the real card. Neither P2 breaks a B#; both fixes are under 5 lines.
