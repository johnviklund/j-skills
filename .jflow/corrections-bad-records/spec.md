# corrections-bad-records
Status: done
Base: f51994c
Review: decide after prove

## Problem
`checkup` and `retro` run `corrections.py` on real session transcripts. One transcript with an odd record shape, seen in the review of its first run, ends the whole report with a traceback, so the human gets no report at all.

## Goals
1. One malformed transcript no longer stops the report: it exits 0 with no traceback.
2. Readable transcripts next to the malformed one are still counted.

## Non-goals
- Reporting which file was malformed.
- Changing what counts as a denial, interrupt or redirect.

## Constraints
- Must not break: the existing report output for well-formed transcripts.
- Ask first: nothing

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goals 1, 2: a null `message` | CLI | `python3 .jflow/corrections-bad-records/check.py null-message` | prints PASS, exit 0 | new | red |
| 2 | Goals 1, 2: a string content block | CLI | `python3 .jflow/corrections-bad-records/check.py string-block` | prints PASS, exit 0 | new | red |
| 3 | Goals 1, 2: a null Bash `command` | CLI | `python3 .jflow/corrections-bad-records/check.py null-command` | prints PASS, exit 0 | new | red |
| 4 | Well-formed output unchanged | test suite | `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p 'test_corrections.py'` | ends `OK` | keep | green |

## Human checks
- none
