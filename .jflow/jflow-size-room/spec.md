# jflow-size-room
Status: ready
Base: 8d10090
Serves: none

## Problem
Anyone changing jflow meets the size test in `jflow/scripts/tests/test_validate.py`. It caps all
tracked jflow files, tests excluded, at 50,000 bytes, and jflow measured 49,995 on 2026-11-17.
Three changes wait for room: the `spec-why` deferral in `TODO.md` and two check-scope ideas of about
72 words. The cap counts `jflow.py`, 26,148 bytes that sessions run but do not read. What a session
reads is `SKILL.md` plus one step's reference, 11,717 bytes at most. No one wrote down the cap's
reason.

## Goals
1. The cap measures what a session reads: `SKILL.md` plus each step's reference, at most 14,000
   bytes for any step.
2. `jflow.py` has its own cap of 30,000 bytes.
3. A comment beside the caps gives their reason: each step's session reads `SKILL.md` and one
   reference before it acts, and the script is capped separately against bloat.

## Non-goals
- Trimming, moving or rewriting any jflow text.
- Size caps in other skills.

## Constraints
- Must not break: the rest of `test_skill_size_and_agent_instruction`; standard library only.
- Ask first: nothing.
- Gate: none.

## Proof
Rows 1, 3 and 4 run the size test in a throwaway worktree of `HEAD` after padding one file:
`python3 -m unittest discover -s .github/skills/jflow/scripts/tests -k test_skill_size`.

| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | a jflow change that adds about 150 words, check-scope's budget, passes the size test with no cut elsewhere, and the limit's reason is written beside it | size test | append 1,000 bytes to `SKILL.md`, then separately to `references/check.md` | the test passes both times | new | red |
| 2 | The limit's reason is written beside it | `test_validate.py` | read the comment within 5 lines of the caps | it says a step's session reads `SKILL.md` plus one reference, and the script is capped separately | new | red |
| 3 | The cap still stops a step's read from growing | size test | one file at a time, pad `SKILL.md` and each of the four references until a step's reading, `SKILL.md` plus that step's reference, is 14,001 bytes; padding `SKILL.md` measures against the largest reference | the test fails all five times | keep | green |
| 4 | The script stays capped | size test | append 4,000 bytes of comment to `scripts/jflow.py` | the test fails | keep | green |
| 5 | No jflow text is cut | git | `git diff 8d10090 -- '.github/skills/jflow/*.md'` | empty | keep | green |

## Human checks
- none
