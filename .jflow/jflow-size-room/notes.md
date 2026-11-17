# Builder notes

Assignment: builder · claude-opus-5-5 · medium · fresh session.
This build uses gpt-6.1-sol · high · fresh session, on the wrong vendor for the assigned seat.

The size guard names all four step references so a missing reference fails the test.
It includes exactly 14,000 and 30,000 bytes because the goals say "at most".
The instruction assertions below the guard stay unchanged, as does all jflow prose.
The existing size test covers the new caps; padding checks exercise the Proof rows without adding another test.
Trigger and model trials do not apply because the skill's instructions and invocation stay unchanged.

## Spec conflict, resolved

The original build stopped because Proof row 3 conflicted with Goal 1's 14,000-byte cap.
At implementation commit `0abe6bd`, the readings after adding 3,000 bytes are 12,060 for build and 12,773 for done.
Both must pass Goal 1 and therefore cannot meet row 3's required failure.
The spec revision in `b2169fd` pads each reading to 14,001 bytes, one file at a time.
Check 1 in `18fdf49` proves all five corrected rows, with no defects or Maybes. This conflict is closed.

## Verification

The padding checks ran in a throwaway worktree of implementation commit `0abe6bd`.

| Proof | Check | Result |
|---|---|---|
| 1 | Add 1,000 bytes separately to SKILL.md and check.md | Both pass |
| 2 | Read the comment beside both caps | It states the reading and separate script rationale |
| 3 | Add 3,000 bytes separately to SKILL.md and all four references | SKILL.md, spec.md and check.md fail; build.md and done.md pass |
| 4 | Add 4,000 comment bytes to jflow.py | Fails at 30,148 bytes |
| 5 | Diff jflow Markdown against 8d10090 | Empty |

The baseline suites pass: workflow 137 tests, checkup 41, jflow 29, roadmap 18; all end with OK, exit 0.
The final suites pass with the same counts and exit 0. `git diff --check` also passes.

## Check 1 seat

Assignment: checker · claude-opus-5-5 · high · fresh session.
Check 1 ran in a fresh gpt-6.2-sol session at high effort. The builder and checker both used OpenAI.

## Done

This step resumes the original gpt-6.1-sol builder session at high effort; the assigned seat remains claude-opus-5-5 at medium effort.
No product code changed after the newest check. Neither PRODUCT.md nor DESIGN.md needs an edit.
There are no Human checks, Maybes or open implementation items. The driver has no reusable app controls.
The done commit removes the driver; its source remains in the check receipt's commit, `18fdf49`.
The finished roadmap item and size deferral are archived.
The human's correction requires an exact next command and its session in the closing handoff.
The existing closing-card rule already covers that correction, so its SKILL-IMPACT row records this missed application.

Done verification: workflow 137 tests OK; checkup 41 tests OK; jflow 29 tests OK; roadmap 18 tests OK; exit 0.
Roadmap check has no errors; its existing missing PRODUCT.md notice remains unchanged.
The summary counts the required separate roadmap archival commit as one fix round; the implementation did not change after check 1.
