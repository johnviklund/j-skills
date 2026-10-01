# workflow v2.02 → v2.1 — review against Matt Pocock's skills

## Verdict

Your workflow's skeleton is stronger than Matt's for how you work: persisted run folders, the state
machine, cross-vendor review, bounded patch cycles, wrap and the learning loop. Matt's set has little
of that. What Matt does better is **defining "done" before any code exists** — the grilling session
closes every open decision, the spec pins behaviour and test seams, and tickets are vertical slices
whose acceptance criteria are tests. v2.1 keeps your skeleton and moves Matt's definition of done
into it. The spec phase is gone: its useful half (seams, verified decisions) now lives in the brief.

## Why planning led to endless coding cycles

Five causes, each visible in your v2.02 files:

1. **Checks proved text landed, not that behaviour works.** Plan steps verified with `grep` counts
   (`pre: 0`). The skill spends a paragraph debugging its own checks — presence over absence,
   `grep -o | wc -l` instead of `grep -c`, and "a check that stops a correct edit costs a whole
   cycle". A step could pass its check with the feature still broken, so review was the first
   place real behaviour got tested.
2. **The executor was barred from writing tests.** "No extra tests beyond the `Check:`." With grep
   checks, that meant behavioural tests appeared only in patch cycles, as the reproduce-then-fix
   pair. Bugs were found after the fact instead of prevented.
3. **Steps were horizontal.** "Core interfaces before consumers" builds layer by layer, so nothing
   works end to end until the last step and integration mistakes surface at review.
4. **Review had no fixed bar.** Requirements of record were brainstorm scope items in prose, with
   open questions allowed. With no acceptance lines to check against, an Opus-at-max reviewer judged
   against its own standard — and it rarely comes back empty.
5. **Every re-review could open new ground.** Cycle 2 re-verified fixes *and* could raise new
   findings anywhere, so the three-cycle bound was often reached by new findings, not failed fixes.

## What changed

**Brainstorm is a grill** (Matt's `grilling`, in your reporting shape). Rounds over the decision
frontier, up to 5 questions each, every question with lettered options and a ➡️ recommended answer,
so "all defaults except 2b" answers a round from your phone. Facts come from the code, never from
you. Fuzzy terms get pinned to one meaning (the useful part of `grill-with-docs`). Decisions are
appended to the file as they settle. It ends only when you confirm the **behaviours** (B1…Bn, each
checkable by one test) and **test seams**. The brief has no "open questions" section: an open
question means the grill isn't finished.

**Plan writes tracer-bullet tickets** (Matt's `to-tickets` + `to-spec` seams). Every ticket is
vertical, delivers a behaviour, has one seam, 1–4 acceptance lines with literal expected values, a
verify command that already runs, blocked-by edges and a lane that picks the executor seat. A
prefactor ticket comes first when it makes the rest easy; wide refactors use expand–contract. You
approve the ticket list in one decision (approve / split / merge). Cap: 8 tickets.

**Execute runs one ticket at a time, red → green** (Matt's `tdd`, distilled into
`references/tests.md`: test at the seam, literal expected values, mock only at boundaries). An
acceptance line that can't pass as written stops the ticket; the test isn't bent to fit.

**Review checks acceptance first, then defects**, against a written severity bar (Matt's
two-axis `code-review`). P0/P1 must cite the behaviour or acceptance line broken, or a failing
input. P2/P3 default to defer → `TODO.md`, so they no longer trigger patch cycles. Re-reviews are
scoped to the fix diff. Those two rules are the cycle breakers.

## Worked example — same work, both plans

The brief (v2.1): *B1 — provider answer with float token counts → answer stored, usage stored as
ints. B2 — provider answer that fails normalization → raw response text persisted before the
error is raised.*

v2.02 plan step:

```
- [ ] Step 2 — persist raw response before normalization in complete() (adapter.py) (F2)
  - Check: grep -o "write_raw_provider_result(" adapter.py | wc -l (pre: 1)
  - Skills: none
```

The check passes as soon as a second call site appears, even one placed after the raise.

v2.1 ticket:

```
### T1 — A normalization failure keeps the provider's answer
Delivers: B2 · Blocked by: none · Lane: logic
Seam: run_paired_evaluation()
Accept:
- [ ] stubbed provider returns a completion with no text → raw file holds the stub's response JSON (B2)
- [ ] same run → failure record has error_type "NormalizationError" and a raw_result path (B2)
Verify: `pytest tests/test_evaluation_runner.py -q` (pre: 14 passed)
Skills: none
Status: todo
```

This test fails if the persist call is in the wrong place, which is exactly the bug that became
one of your reviewer exam cases.

## Simplification — `writing-for-agents` applied

| | v2.02 | v2.1 |
|---|---|---|
| Hub `SKILL.md` | 207 lines, 14.1K chars | 157 lines, 8.8K chars |
| Hub + phase files | 57.8K chars | 31.9K chars (−45%) |
| Loaded per phase (hub + routing + phase) | 31–35K chars | ~23K chars (−27 to −36%) |
| Negation words in hub + phases | 198 | 42 |
| Phases | 5 (one optional) | 4 |
| Closing card | ~14 lines | 5 lines |

How: **duplication** — each phase file restated its rules a second time as a paste block (35–40%
of the file); the blocks are gone and the card's command line is the handoff. **Relevance** —
"Keeping this skill alive" moved to the README (a running agent never needs it); stale sediment
removed (the worklog reference still said wrap deletes `review.md`, which v2 stopped doing).
**Negation** — rules rewritten as the behaviour wanted. **Leading words** — *grill, frontier, brief,
tracer bullet, seam, acceptance, red → green* carry what used to take sentences.

## Decisions for you

1. **Brainstorm seat effort.** The brief now defines "done", so the grill does more work than the
   old dialogue.
   a) Sonnet 5 at high ➡️ (set in `ROUTING.md`)   b) keep medium   c) move the seat to Opus 5
2. **Logic-ticket approval.** v2.02 approved logic edits diff by diff.
   a) Approve each ticket's diff ➡️ (fewer, meaningful stops; set in `ROUTING.md`)
   b) Auto for logic, approve contract tickets only
3. **Ticket file layout.** Matt writes one file per ticket.
   a) All tickets in `plan.md` ➡️ (one file for the state machine and your phone)
   b) `tickets/NN-slug.md` per ticket, `plan.md` as the index
4. **Domain docs from `grill-with-docs`.** Your zip calls a `domain-modeling` skill that isn't in
   it; as I understand Matt's version, it keeps a `CONTEXT.md` glossary and ADRs.
   a) Pin terms inside the grill, record decisions in the brief, let wrap promote durable ones to
      `PRODUCT.md` ➡️ (no new docs)   b) add `CONTEXT.md` + `docs/adr/`

## Trialing it

`SKILL-IMPACT.md` has a `trialing` row for 3 runs. The numbers to watch in `checkup seats`:
review cycles per run (target: most runs clean at cycle 1) and deviations. A good early sign is a
ticket stopping at "acceptance line can't pass as written" — that's a planning miss caught in
minutes instead of in review. Existing runs keep working: a v2.02 brief without behaviours makes
plan derive them and put them to you in the ticket round.

## Noticed, not changed

- `ROUTING.md` (8K, read every phase) mixes the seat tables the card needs with human-facing
  maintenance text; moving "How a model earns a seat" and "Maintaining this file" to the README
  would cut another ~3K per phase.
- `memory.remember` (22K) and `checkup` (17K) are the largest files in the repo and get the same
  paste-block and negation treatment well; they load only when invoked, so they're a lower priority.
- Skill descriptions are always loaded. The `workflow` one is shorter now; `checkup` and
  `memory.remember` carry long trigger lists. Matt's `disable-model-invocation` would zero them, but
  the README notes Copilot invokes skills by description match, so shortening is the portable fix.
- v2.1 builds the "plan → testable work units, implement one ticket" shape now.

## Amendments after a history review (2026-09-28)

v2.1 was checked against the cx-intelligence runs it was written without. Its grep-check diagnosis
holds (`foundry-semantic-boundaries` C1-1), but the costliest run, `five-topic-live-delivery`
(12 steps, 4 cycles, stakeholder-rejected), failed on a different axis: checks never observed the
surface the user reaches or the consumer contract, and its two P0s cited no acceptance line — under
the draft bar they would have been P2 and deferred. Changes made:

- **Outcome is checked where the user reaches it** (review Acceptance) and is valid P0/P1
  evidence; "wrong or misleading data shown as correct" is a P0.
- **Operator lane** for live/irreversible/hosted steps: handoff → human runs → receipt with
  literal values; ticket status `awaiting-human`; status shows it as the blocker; `(live)` behaviours.
- **Acceptance-line rules** (plan + `tests.md`): one expected result (no "or"), at least one
  positive assertion, observed at the reached surface; contract fields round-trip through the
  consumer model; suppressed values checked at every read. The approval round shows the lines.
- **Existing tests keep their assertions**: changes are deviations with before/after counts;
  review counts them.
- **Re-review covers each finding's class**, not only the fix diff; an incomplete fix reopens at
  its original severity; a new P1 outside scope is a human decision (➡️ fix when it breaks a B#
  or the Outcome). Patch tickets are `C<cycle>-T#`.
- **Lane decides fix-ticket seat and approval** — contract fixes go heavy + reviewed (the cycle-3
  contract break came from an auto-approved fix).
- **Deferrals**: only P2s reach `TODO.md`, in one `## Review deferrals` section; P3s stay in
  `review.md`; `checkup` ages them. (cx `TODO.md` is 929 lines.)
- Brief budget ~80 lines (history: 54 · 67 · 88 under a 40 cap); `pre: new file` allowed for
  test files a ticket creates; data preconditions verified by read-only query; blind-spot,
  reference and playback openings restored; description regains its casual-mention guard;
  `workflow spec` routes to plan; CLI skill prefixes noted for the card line.
- Housekeeping: stale Phase-N/spec wording (README, wrap, bootstrap, ROUTING, evals), `rg` → `grep`
  in wrap, skill `MEMORY.md` clone path, `checkup` compares Run numbers only like-for-like across
  v2.02/v2.1, and the four 2026-09-12 `SKILL-IMPACT.md` trials marked `superseded` so the v2.1
  trial is attributable.

Still open for the human: the reviewer exam set holds 9 cases against its cap of 8 (pick one to
retire); the j-skills root `README.md` still describes the five-phase spec workflow and `evals`
seats (edit at deploy); `ROUTING.md` *Last verified* is 2026-09-11 — confirm picker IDs at deploy.
