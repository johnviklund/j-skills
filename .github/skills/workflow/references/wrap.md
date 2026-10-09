# Final check & wrap-up — `workflow wrap`

> ⚠️ Read through the `workflow` skill; the command ends with its closing card.

Seat: wrap runs on a mid-tier seat at medium effort, auto-approve — mapping
and the after-review model swap in `ROUTING.md`. Wrap is procedural; its only judgment calls are
commit messages that read as worklog lines and `memory.remember`'s routing.

**Precondition — review evidence.** Before anything else, confirm `.workflow/<slug>/review.md`
exists with `Status: complete` and **no open finding** (read the `## Resolved` table and the last
cycle only): every `fix now` carries `Resolved: @ <sha>` from a later review cycle, every `defer` on a P0/P1 carries `Approved by human:`, and `wontfix`
carries a reason. A `fix now` without `Resolved:` is intended work, not done work — stop and route
to `workflow execute <slug>` (patch plan) or `workflow review <slug>`. Then confirm **no code changed
since the reviewed `Base`** per `SKILL.md`'s receipt rule (the receipt-rule diff `<Base>..HEAD`
is empty) — receipt commits such as the review itself are
fine, and so is step 5b's delete commit once its sha is ticked in `wrap.md`'s `## Steps`; any other
code commit is not. If it's missing or stale, don't lecture that review "hasn't run" —
say the evidence is missing/stale and print the closing card routing to `workflow review`.

**Precondition — the run checks out.** `python3 <skill>/scripts/check-run.py <slug>` (`<skill>` is the workflow skill's folder) reports no ERROR and no open `fix now` finding
(its note on `review.md` says which). An ERROR names the artifact to fix and the phase that owns it.

**Precondition — clean code tree.** Then run `git status --porcelain`. Every modified or untracked
path must be a receipt (per `SKILL.md`'s receipt rule) or `.gitignore`; a script, config, or data file
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
already-archived folder. Step 9a replaces the checklist with the run summary and sets `Status: done` in
the same edit, so a `wrap.md` with no `## Steps` is a finished wrap.

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
3a. **Capture gate** — if `review.md`/`plan.md` or the run folder records two or more failed
   receipts (failed attempts, reruns, repair tickets), and `learnings.md` is missing, write
   `[durable→memory]` lines for the cause of each before step 4; "nothing to route" is valid only
   with no failed receipt.
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
   roadmap step moved to `<repo>/ROADMAP_ARCHIVE.md` with a pointer to the run or commit
   (`ROADMAP.md` keeps only open and next steps). Read these docs by heading, opening the sections
   the plan's impacts and the shipped surface touch — not whole files. **Include the decisions nobody listed**: shipping is how most product
   decisions actually get made, and one settled in passing and never written down is the commonest
   way `PRODUCT.md` goes stale. If this run fixed how something works, that answer belongs in
   `PRODUCT.md` whether or not anyone had thought to ask the question first.
   **Never rewrite a settled principle or a stated boundary to match the
   code**: that inverts the source of truth. Stop, name the contradiction, and print the card
   routing it to the human as a product decision — the code may be the thing that's wrong. Commit
   doc edits before step 6 so `TODO.md` points at truth rather than duplicating a stale claim.
5a. **Feature-map truth** — only when the repo has `.agents/skills/verify-*/features/`. For
   each user-facing feature this run added or changed, update its feature file (or add one and
   its index line in `features/README.md`) so it says how a user reaches the feature now and what
   proves it, and drive the new recipe once with the skill's control CLI. Feature files are
   receipts; a fix the control CLI itself needs is code, so it becomes one `TODO.md` line
   ("`verify.maintain`: <gap>"), never a wrap edit. Leave the `Last maintained` stamp alone:
   only `verify.maintain` checks every feature. No user-facing change → "no feature changed".
5b. **Retire** what this run made obsolete in the product tree (the run folder is history and
   stays): code paths it replaced, flags now always on, shims, harnesses whose campaign ended,
   tests that cover only those, and tests of run scripts. Check each before listing it: `git log -S`
   for why it exists, and a grep for live importers. Ask once, as one lettered decision (➡️ a
   delete all · b keep some: say which). On approval, delete in one commit that only deletes
   files, tick its sha here, then run the full suite again; red → revert that commit and escalate
   like step 1. A removal that needs an edit to a kept file is code review never saw: it becomes
   one `TODO.md` line, not a wrap change. A test outside `.workflow/` that reads a run's files is
   a P1 for the next run, named here (`check-run.py --all` lists them). Nothing obsolete →
   `none` with a reason.
6. **TODO hygiene** — `TODO.md` is a small scratch pad (one line per idea) and its full history lives
   in `<repo>/TODO_ARCHIVE.md`; both are read by `grep` and section, never whole-file by default.
   Update `TODO.md` (if present) from the plan's `## TODO impacts` plus anything done in passing:

   - **Completed, subsumed or brainstormed items move to `<repo>/TODO_ARCHIVE.md`** — the original
     wording verbatim, plus `— archived <date> · <commit sha, or the run/initiative that subsumed it>`
     (create the file with a one-line header if missing). `TODO.md` keeps a single `## Archived`
     line: `Archived items: see TODO_ARCHIVE.md (grep it).` Nothing is deleted.
   - Rewrite items whose scope this run changed so they match the code that now exists; check off
     small UI changes shipped along the way. Roadmap status belongs to step 5, not here.

   Then reconcile the lists so intake and committed direction can't drift apart: no open `TODO.md`
   item may duplicate an active `ROADMAP.md` item — point it at the roadmap item or archive it;
   every roadmap step step 5 just archived has its `TODO.md` entries archived with a pointer to
   `ROADMAP_ARCHIVE.md`; and a roadmap step this run descoped or abandoned lands back in `TODO.md` as
   one deferred line naming what it was and why it stopped. A committed item may leave the roadmap,
   but it never simply disappears. A `TODO.md` item that a parked `.workflow/<slug>/` already
   brainstormed is archived with a pointer to the slug (the folder is the item now); a parked run
   this run shipped or made moot is set `done` with one line saying so. One home per idea: TODO
   (not yet brainstormed) → parked run (brainstormed) → live run.

   **Size check.** Flag `TODO.md` over ~15 KB or `ROADMAP.md` over ~12 KB (`wc -c`) in the receipt
   and propose what to archive (oldest completed, then stale ideas) as a lettered decision —
   propose only; never auto-delete or auto-archive beyond the rules above.

   Boundaries: don't add ideas on your own initiative (it's the human's scratch pad — only items the
   human explicitly deferred during this run, one line each in the right section, and every P2
   finding `review.md` left as `defer`, under one `## Review deferrals` section as
   `- <slug> C#-# (P2, <date>) — <one line>`; deferred P3s stay in `review.md`); and entries point
   at the product docs step 5 just corrected, never duplicate them.
7. **Eval deposit** — usually nothing. For each `[durable→eval] code-review` line in
   `.workflow/<slug>/learnings.md` that passes the admission test in `references/learning-worklog.md`
   (a P0/P1 missed by the writer or by the reviewer), write one `Kind: missed` case to
   the exam set (`~/.agents/j-skills-evals/strict-reviewer/`, a clone of the private `j-skills-evals` repo; the `evals` skill gives the clone command), as `missed-<topic>.md` in the shape the `evals` skill defines: context, the diff
   copied in (never a `.workflow/` path), the fixed diff as its clean twin when there is one, the
   P0/P1 a pass must name, and provenance (date, repo, run, sha range, which model missed it).
   **Cap 10, rolling:** a full set drops its oldest seeded case first, then the weakest missed
   one; never append past the cap. Commit and push in `~/.agents/j-skills-evals`, which is private because
   cases copy code: never write a case into this repo or any public one.
8. Append this run's entry to `WORKLOG.md` (see `references/learning-worklog.md`): one capped,
   git-pointing entry, rolling the oldest off if over ~15; commit and push it with the rest.
   Take the models from the run, not from `ROUTING.md`: the writer from `plan.md`'s `Writer:`
   lines, the reviewer from `review.md`'s `Independence:` line. The `Run:` line's sessions count
   the `Session N:` lines in `plan.md`'s `## Execution state`, before 9a strips it; the count
   includes patch sessions, which execute records there too. Write `Seats:`
   and `Skills:`;
   `check-run.py` errors on a done run whose entry lacks them.
9. **Archive the run — nothing leaves `.workflow/<slug>/`; beyond 9a's transient files, nothing is deleted from the run folder.** Once
   `memory.remember` confirms every line is routed and step 7's cases are deposited:

   **9a. Drop the transient, keep the record, leave a summary.** In the run folder: delete
   `patch_plan.md` (its content is in `review.md`); strip the `## Execution state` block from
   `plan.md`; keep `brainstorm.md`, `plan.md` (with `## Deviations`), `review.md`, `learnings.md`
   (fully routed — the record of *what* was learned) as **history only**. Rewrite `wrap.md` last into
   the run's **summary, ≤ ~40 lines**: outcome (one paragraph), what shipped (ticket → commit sha),
   deferred items and where they went, receipts that exist and where, the review verdict and
   cycle count, and a `Retired: <files, -lines> @ <sha>` or `Retired: none — <reason>` line from
   step 5b (`check-run.py` errors without it) — dropping the step checklist. **Later phases read a done run's `wrap.md` alone**;
   its `plan.md`/`review.md` are searched with `grep` on demand, never loaded. Set `Status: done` in
   `brainstorm.md` (the run's status of record) and in the kept artifacts, `wrap.md` last.

   **9b. Anything else the run left** — receipts, verification output, one-off scripts, live
   harnesses — stays in the run folder as evidence, listed in `wrap.md` and never read by later
   runs. **Tidy the top level** to `SKILL.md`'s *Layout*: a stray receipt (`*.md`, `*.txt`, an
   image) moves into its subfolder, and the run's own artifacts that name it get the new path. A
   stray script or data file stays put and is named in `wrap.md`: moving it is a code change the
   review never saw. Flag any file over ~100 KB to the human as a lettered decision (move it out of git, or keep
   it); never move it unasked. Before moving or renaming any file, grep
   the repo *outside* `.workflow/` for its filename and bare module stem (`grep -rn -F '<stem>'
   --exclude-dir=.workflow --exclude-dir=.git .`); a hit means it is load-bearing — leave it exactly where it is and tell
   the human. A run folder is history: it is never emptied, never renamed, never reused.

   Rerun the checker after 9a (the run is now `done`): no ERROR, and its warnings named in the
   receipt. Commit the archive and push it, so the tree the next run re-grounds from is the tree that's
   in git. `.workflow/` is tracked — if this repo ignores it, stop and say so; a run archive that
   lives on one machine is not an archive.

**Why this order:** code → learnings routed, evals deposited, committed → **push** → archive the run.
Archiving is last because it is the only step that removes anything from the run folder (the transient files), and by
then everything worth keeping is in git, the exam set, `memory/` or the kept artifacts. Open a PR only
if not committing straight to `main`.

**Wrap's chat receipt is fixed, one line per step:** final checks (pass / known-environmental);
shortcut grep (clean / what was found); commits + push (shas); learnings routed (count → where);
product-doc truth (per doc: no changes, or the edit — one line each, ESCALATE items as a lettered
decision list); feature map (files updated, `no feature changed`, or `no verify skill`); retired
(files and lines @ sha, or none); TODO hygiene (items archived/rewritten, or none); eval cases deposited (count);
worklog entry (yes); run archived (`<slug>` · done); size flags (`TODO.md`/`ROADMAP.md` over budget, or
none); parked runs still open (slugs, or none). Anything that needs a decision is a lettered item
with a recommended default. Then the ✅ done card, not a next-phase card: what shipped (one line);
product-doc truth (edited what, or none); recommended next (`workflow brainstorm <next ROADMAP
item>`, `memory.compact` if `MEMORY.md` grew, PR if not on `main`), plus one optional line:
`understand <slug>` for a cited HTML explainer of this run.
