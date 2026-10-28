# CE sessions and workflow runs

3. **Detect CE sessions and workflow scratch**
   - Check if any files under `docs/brainstorms/`, `docs/plans/`, or `docs/solutions/` were modified or created in this session.
   - If CE artifacts were touched, capture only session metadata and a short pointer to the durable CE note. Do not duplicate the full pattern write-up in active memory.
   - Separately, check for a `workflow` run folder, `.workflow/<slug>/` (tracked, kept after wrap as the run's record — not the CE `docs/plans/`/`docs/brainstorms/` convention). If its `learnings.md` exists, treat its `[durable→skill]` / `[durable→memory]` / `[durable→design]` / `[drop]` tagged lines as the primary candidate list for this pass — they've already been pre-classified by the session that wrote them — and use the run slug as the `Evidence` entry on every page it touches. A `[used→memory]` line names a page the run relied on: it goes to *Used, not repeated* in step 4 and adds no `Evidence`.

7. **Optional wrap-up, when finishing a workflow pass**
   - If `.workflow/<slug>/learnings.md` exists and every tagged line in it has now been routed, say so in one line (`routed N lines → M pages, K skill edits`) — the `workflow` wrap step owns the checks, commit, push, and archiving of the run folder. Never delete or empty anything under `.workflow/`; run folders are kept.
   - This step is optional and only relevant when the session was a `workflow` run; a plain "remember this" ask has no wrap-up to do.

