# Final check & wrap-up — `workflow wrap`

> ⚠️ Read through the `workflow` skill; the command ends with its closing card.

Seat: wrap runs on a mid-tier seat at medium effort, auto-approve — mapping
and the practical after-review model swap in `ROUTING.md`. Rationale: wrap is procedural — the
only judgment calls are commit messages that read as worklog lines and `memory.remember`'s
routing decisions, which rules out the mechanical lane but doesn't justify a heavy or reviewer
seat; the hard reasoning already happened in review.

**Precondition — review evidence.** Before anything else, confirm `.workflow/<slug>/review.md`
exists with `Status: complete` and **no open finding**: every `fix now` carries `Resolved: @ <sha>`
from a later review cycle, every `defer` on a P0/P1 carries `Approved by human:`, and `wontfix`
carries a reason. A `fix now` without `Resolved:` is intended work, not done work — stop and route
to `workflow execute <slug>` (patch plan) or `workflow review <slug>`. Then confirm **no code changed
since the reviewed `Base`** per `SKILL.md`'s receipt rule (`git diff --stat <Base>..HEAD --
. ':(exclude)*.md' ':(exclude)*.txt'` is empty) — receipt commits such as the review itself are
fine, any code commit is not. If it's missing or stale, don't lecture that review "hasn't run" —
say the evidence is missing/stale and print the closing card routing to `workflow review`.

**Precondition — clean code tree.** Then run `git status --porcelain`. Every modified or untracked
path must be a receipt file (`*.md`, `*.txt`) or `.gitignore`; a script, config, or data file
anywhere — `.workflow/`, `docs/`, `evals/` included — is code the review verdict never saw: stop,
name the paths, and route to `workflow review`. Wrap does not launder unreviewed code through its
own commit. Receipt dirt is wrap's normal input and gets committed in step 3.

**Checkpoint — `wrap.md`.** Wrap makes several commits and can be interrupted between them, so it
keeps its own artifact: on first entry create `.workflow/<slug>/wrap.md` with the provenance header
(`Inputs: review.md @ <its Base>`, `Base:` = that reviewed sha, `Status: drafting`) and a `## Steps`
checklist of the nine steps below; tick each step as it lands (with the commit sha where one was
made). On re-entry with a `wrap.md` present, re-run the preconditions against *its* `Base`, then
resume at the first unticked step — never redo a ticked one. Steps are written to be safe to
repeat if a tick was lost: step 3 commits only what is dirty, step 4 skips lines already marked
routed, step 8 skips if `WORKLOG.md` already has an entry for this slug, step 9 is a no-op on an
already-archived folder.

**Escalate on failure, don't fix in wrap:** if step 1's final checks surface a regression, stop —
that's a mini review→patch cycle (route it through the patch-cycle rows in `ROUTING.md`), not
something to patch inline at wrap's effort/approval settings.

Commit, push, curate, and clean up — in one go:

1. Run final checks: build, type-check, full test suite (call out known-environmental failures,
   don't treat them as regressions). If the receipt-rule diff since the plan's `Base` is empty,
   the run changed no code — record the empty diff as the proof and skip the suite. A check
   command that is not found is a failure, not a pass.
2. Grep for leftover shortcuts: `TODO: Implement`, `NotImplementedError`, `...`, `placeholder`,
   `real implementation`, and any old contract version literal — nothing should still pin it.
3. Commit the remaining changes — which the entry gate has already narrowed to allowlisted
   doc/scratch paths. **Commit discipline:** use session-level messages that read as a
   worklog line on their own (what shipped + why), not terse "fix" stubs — the commit log is the
   portable backtrack record, so make it carry the narrative.
4. Invoke `memory.remember` to route every tagged line in `.workflow/<slug>/learnings.md` not yet
   marked `[routed → …]` to its destination (a `memory/` page, `AGENTS.md`, `README.md`, an
   existing or new skill, `DESIGN.md`); it marks each routed line and never counts a run twice.
   Commit those changes, and push.
5. **Product-doc truth** — answer this explicitly; silence is not an answer. Start from the plan's
   `## Product doc impacts`, then re-derive it from what actually shipped: deviations and patch
   cycles change scope after planning, so the plan's list is the starting point, not the verdict.
   For each of `PRODUCT.md`, `DESIGN.md` and `ROADMAP.md` that exists, state either "no statement
   changed" or the edit made — a stale statement of current state/scope/stack corrected, an open
   decision this run resolved moved out of the open list and recorded as decided, a completed
   roadmap item checked off. **Include the decisions nobody listed**: shipping is how most product
   decisions actually get made, and one settled in passing and never written down is the commonest
   way `PRODUCT.md` goes stale. If this run fixed how something works, that answer belongs in
   `PRODUCT.md` whether or not anyone had thought to ask the question first.
   **Never rewrite a settled principle or a stated boundary to match the
   code**: that inverts the source of truth. Stop, name the contradiction, and print the card
   routing it to the human as a product decision — the code may be the thing that's wrong. Commit
   doc edits before step 6 so `TODO.md` points at truth rather than duplicating a stale claim.
6. **TODO hygiene** — update repo-root `TODO.md` (if present) from the plan's `## TODO impacts`
   list plus anything done in passing: move completed/subsumed items to Archived with a one-line
   pointer (commit sha or the initiative that subsumed them); rewrite items whose scope this run
   changed so they match the code that now exists; check off Small UI Changes shipped along the
   way. Roadmap status belongs to step 5, not here.

   Then reconcile the two, so intake and committed direction can't drift apart: no open `TODO.md`
   item may duplicate an active `ROADMAP.md` item — point it at the roadmap item or archive it;
   every roadmap item step 5 just checked off has its `TODO.md` entries archived with a pointer to
   that item; and a roadmap item this run descoped or abandoned lands back in `TODO.md` as a
   deferred entry, naming what it was and why it stopped. A committed item may leave the roadmap,
   but it never simply disappears. Parked runs are the third list: a `TODO.md` item that a parked
   `.workflow/<slug>/` already brainstormed is archived with a pointer to the slug (the folder is
   the item now); a parked run this run shipped or made moot is set `done` with one line saying
   so. One home per idea: TODO (not yet brainstormed) → parked run (brainstormed) → live run.

   Boundaries: don't add new ideas on your own initiative (it's the human's scratchpad —
   only add items the human explicitly deferred during this run, in the right section, and every
   P2 finding `review.md` left as `defer`, under one `## Review deferrals` section as
   `- <slug> C#-# (P2, <date>) — <one line>`; deferred P3s stay in `review.md`); and the
   TODO entry points at the product docs step 5 just corrected, it never duplicates them.
7. **Eval deposit** — usually nothing. For each `[durable→eval] code-review` line in
   `.workflow/<slug>/learnings.md` that passes the admission test in `references/learning-worklog.md`
   (a P0/P1 missed by the writer or by the reviewer), write one self-contained case to
   `evals/strict-reviewer/code-review-<YYYY-MM-DD>-<slug>.md` — the diff copied in (never a
   `.workflow/` path), the P0/P1 findings a pass must name (one line each), and provenance (date,
   sha, which model missed it). **Cap 8, rolling:** if the set is full, replace the weakest case
   or skip — never append past the cap. Commit with the rest.
8. Append this run's entry to `WORKLOG.md` (see `references/learning-worklog.md`): one capped,
   git-pointing entry, rolling the oldest off if over ~15; commit and push it with the rest.
9. **Archive the run — nothing leaves `.workflow/<slug>/`, nothing is deleted from the repo.** Once
   `memory.remember` confirms every line is routed and step 7's cases are deposited:

   **9a. Drop the transient, keep the record.** In the run folder: delete `patch_plan.md`
   (its content is in `review.md`); strip the `## Execution state`
   block from `plan.md`; keep `brainstorm.md`, `plan.md` (with `## Deviations`), `review.md`,
   `learnings.md` (now fully routed — it stays as the record of *what* was learned here), and
   `wrap.md`. Set `Status: done` in `brainstorm.md` (the run's status of record) and in the kept
   artifacts, `wrap.md` last.

   **9b. Anything else the run left** — receipts, verification JSON, one-off scripts, live
   harnesses — stays in the run folder as evidence. Before moving or renaming any such file, grep
   the repo *outside* `.workflow/` for its filename and bare module stem (`grep -rn -F '<stem>'
   --exclude-dir=.workflow --exclude-dir=.git .`); a hit means it is load-bearing — leave it exactly where it is and tell
   the human. A run folder is history: it is never emptied, never renamed, never reused.

   Commit the archive and push it, so the tree the next run re-grounds from is the tree that's
   in git. `.workflow/` is tracked — if this repo ignores it, stop and say so; a run archive that
   lives on one machine is not an archive.

**Why this order:** commits are local — nothing leaves the machine until push. Code → learnings
routed, evals deposited, and committed → **push** → archive the run. Archiving comes last because
it is the only step that removes anything (the transient files), and by then everything worth
keeping is already in git, in `evals/`, in `memory/`, or in the kept artifacts. Open a PR only if not committing straight to
`main`.

**Wrap's chat receipt is fixed, one line per step:** final checks (pass / known-environmental);
shortcut grep (clean / what was found); commits + push (shas); learnings routed (count → where);
product-doc truth (per doc: no changes, or the edit — one line each, ESCALATE items as a lettered
decision list); TODO hygiene (items archived/rewritten, or none); eval cases deposited (count);
worklog entry (yes); run archived (`<slug>` · done); parked runs still open (slugs, or none). Anything that needs
a decision is a lettered item with a recommended default. Then the ✅ done card from `SKILL.md`,
not a next-phase card.
