# CE sessions and jflow runs

3. **Detect CE sessions and run folders**
   - Check if any files under `docs/brainstorms/`, `docs/plans/`, or `docs/solutions/` were modified or created in this session.
   - If CE artifacts were touched, capture only session metadata and a short pointer to the durable CE note. Do not duplicate the full pattern write-up in active memory.
   - Separately, check for a jflow run folder, `.jflow/<slug>/` (tracked and kept as the run's record). Its `notes.md` judgement calls and open notes, and the Defects and Maybes in `receipts/check-*.md`, are the candidate list for this pass; use the run slug as the `Evidence` entry on every page it touches. A human correction during the run, which `jflow done` hands to this skill, is always a candidate.
   - A run in jflow's issue and pull request mode (`#N`, an issue URL, or a slug in a clone with `git config jflow.mode github`) has no run folder. Read its PR `jflow:notes` and `jflow:receipt` comments with `python3 <jflow skill>/scripts/jflow.py show <#N|URL|slug>`, read-only, and use `#N` as the `Evidence` entry. Skip a line that a later note already marks `[routed → ...]`. Record the routing in one new `jflow:notes` comment, never an edit of an earlier one: write each routed line with its `[routed → <destination> <YYYY-MM-DD>]` mark to a temporary file outside the repo and post it with `jflow.py note <#N> --file F`. On a public repo, show the human the text first and pass `--confirmed` on their yes.
   - A `[saved→skill] <row date> <skill> <words of the change> — <what it stopped>` line in `notes.md` records evidence for an existing `SKILL-IMPACT.md` trial, and `checkup`'s `skill-trials.py` counts it: mark it `[routed → SKILL-IMPACT <date>]` and change no file for that evidence.

7. **Optional wrap-up, when the session was a jflow run**
   - Say in one line what was routed (`routed N lines → M pages, K skill edits`). `jflow done` owns the checks, commit and push. Never delete or empty anything under `.jflow/`; run folders are kept.
   - A plain "remember this" ask has no wrap-up to do.
