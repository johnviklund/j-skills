## verify.maintain

A feature map goes stale as soon as the app changes. This pass keeps it honest. Its unit is the
**feature**: every feature file gets a source check and a live drive.

**Outcome:** exactly one, stated at the end. **clean**: every feature covered, nothing to fix, no
commit except the stamp. **changed**: one commit of proven corrections. **blocked**: coverage
could not finish, or a fix could not be proven; say exactly what blocked it.

**Edit scope:** only the `verify-APP` folder (its `SKILL.md`, `features/`, `scripts/`). Product
code is never edited here. A behaviour the map describes that the app no longer has is either
drift (fix the map) or a product bug (report it): which one is decided in step 5.

**0. Locate.** Find `.agents/skills/verify-*/`. Several → ask which. None → stop and point at
`verify.create`.

**1. Index hygiene.** Read `features/README.md` and list its sibling files. Fix missing, extra,
duplicate and dead index lines.

**2. Source wave.** One read-only sub-agent per feature file, run in parallel. Each reads the
code behind the feature and returns: a short summary, the source entry points with `file:line`,
likely drift with citations (or none), and one recipe to verify it live. Sub-agents never drive
the app and never edit. Done when every feature file has a returned summary.

**3. Reconcile.** Merge overlapping recipes into as few app states as practical. Spot-check
cited drift; leave clean claims alone. Then look for features missing from the map:
`git log --oneline SHA..HEAD` from the `Last maintained` stamp, filtered to user-facing paths. A
feature counts as missing only with a concrete source path.

**4. Live pass.** Required even when the source looks clean, because only a live drive proves
the recipe still works. This session does all the driving, using the skill's own launch model.
Drive every feature at least once, and hold three rules throughout:

1. Run `doctor` before the first drive, and again after any failed or surprising drive. When
   doctor cannot see the problem (a stuck UI on a healthy process), reset to the baseline or
   relaunch.
2. Evidence captured so far survives every cleanup: check it where the skill says it is.
3. Nothing a drive started outlives the drive: clean up after failed attempts too.

A doctor failure caused by drift in the skill is drift: fix it, restart what the fix touched,
and retry once before calling the pass blocked. A feature is `unreachable` only with the
concrete missing precondition (auth, entitlement, OS, external state) and the route tried; a
precondition the map does not mention is drift too. Every harness fix is driven live again
before it ships. Tear down after the last drive.

**5. Triage** each problem into one class:

- **Doc drift:** the map's user-side description is wrong or missing. Fix the feature file.
- **Harness gap:** the app works but the CLI cannot drive it. Fix `scripts/control`, and show
  the new command in `SKILL.md`.
- **Product gap:** the app is actually broken. Keep it out of this commit; report it to the
  human as a lettered decision with ➡️ "add a line to `TODO.md`".

**6. Ship or stop.** Re-read every changed file, update the stamp to
`Last maintained: TODAY @ HEAD-SHA`, and commit as `verify.maintain: <what changed>`. A clean pass
commits the stamp alone. A blocked pass commits nothing and says what blocked it.

**7. Report**, in plain words, at most six lines: the outcome, features covered (count), drift
fixed, harness fixes, unreachable features with their precondition, and product gaps as the
decision list.
