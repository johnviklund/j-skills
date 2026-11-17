# Builder notes

Assignment: builder · claude-opus-5-5 · medium · fresh session.
This build uses gpt-6.1-sol · high · fresh session, on the wrong vendor for the assigned seat.

The size guard names all four step references so a missing reference fails the test.
It includes exactly 14,000 and 30,000 bytes because the goals say "at most".
The instruction assertions below the guard stay unchanged, as does all jflow prose.
The existing size test covers the new caps; padding checks exercise the Proof rows without adding another test.
Trigger and model trials do not apply because the skill's instructions and invocation stay unchanged.

## Spec conflict

Build is incomplete. Proof row 3 conflicts with Goal 1's 14,000-byte cap.
At implementation commit `0abe6bd`, the readings after adding 3,000 bytes are 12,060 for build and 12,773 for done.
Both must pass Goal 1 and therefore cannot meet row 3's required failure.
Only `jflow spec` can revise this row. Suggested check: pad each reading to 14,001 bytes, one file at a time.
The spec stays unchanged, and no completed build step is recorded.

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
