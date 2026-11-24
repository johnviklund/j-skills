# CE sessions and jflow runs

3. **Detect CE sessions and run folders**
   - Check if any files under `docs/brainstorms/`, `docs/plans/`, or `docs/solutions/` were modified or created in this session.
   - If CE artifacts were touched, capture only session metadata and a short pointer to the durable CE note. Do not duplicate the full pattern write-up in active memory.
   - Separately, check for a jflow run folder, `.jflow/<slug>/` (tracked and kept as the run's record). Its `notes.md` judgement calls and open notes, and the Defects and Maybes in `receipts/check-*.md`, are the candidate list for this pass; use the run slug as the `Evidence` entry on every page it touches. A human correction during the run, which `jflow done` hands to this skill, is always a candidate.
   - A `[saved→skill] <row date> <skill> <words of the change> — <what it stopped>` line in `notes.md` records evidence for an existing `SKILL-IMPACT.md` trial, and `checkup`'s `skill-trials.py` counts it: mark it `[routed → SKILL-IMPACT <date>]` and change no file for that evidence.

7. **Optional wrap-up, when the session was a jflow run**
   - Say in one line what was routed (`routed N lines → M pages, K skill edits`). `jflow done` owns the checks, commit and push. Never delete or empty anything under `.jflow/`; run folders are kept.
   - A plain "remember this" ask has no wrap-up to do.
