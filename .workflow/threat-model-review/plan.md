Command: workflow plan threat-model-review
Created: 2026-10-22 · Claude Opus 5.5
Base:    4486102
Inputs:  .workflow/threat-model-review/brainstorm.md @ 6aa7823
Status: complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md in this repo)
Decisions: 1a (trigger list in both references) · 2a (`Threats: none` line on runs with no trigger) · 3a (no reviewer exam; the trial judges) · 4a ticket list approved 2026-10-22
Size: code 0 · tests 495 · ratio n/a (doc run) · largest touched test_check_run.py 495, phase-0-brainstorm.md 215 (13,294 B), phase-4-review.md 179 (13,053 B), README.md 220 · over 1,000: none

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | B6 already holds: `require_sections` checks only the six `BRIEF_SECTIONS` (check-run.py:66, 183) and ignores other headings; `_match` (check-run.py:116) gives `Trust boundaries` no prefix clash with `Test seams`. Probe with the test fixtures: brief with and without the section → `0 errors · 0 warnings` both | T1 adds one pinning test, no check-run.py change |
| F2 | `check_review` reads only the `Independence:` and `Size:` lines of `## Coverage` (check-run.py:498-507) | a new `Threats:` Coverage line needs no checker change |
| F3 | Both step references are already over the ~10 KB budget (MAINTAINING.md §Context budget): phase-0 13,294 B, phase-4 13,053 B | each ticket caps its growth in bytes (+700, +900) |
| F4 | `SKILL.md` is 212 lines, past its ~180 cap; MAINTAINING.md asks that a rule every step reads displace another | the trigger list stays out of `SKILL.md` (decision 1) |
| F5 | The severity table has four rows and P0 already lists "security hole" (phase-4-review.md:62-67) | B4 maps onto those rows; T2 asserts the row count stays 4 |
| F6 | Reuse: the dependency check (phase-4-review.md:40-43) is the existing pattern for a security pass inside *Defects*; the `SKILL-IMPACT.md` 2026-10-22 rows are the trial pattern | T2 adds the threat pass beside it, same shape; no new section in the review |
| F7 | README.md:59-65 lists what the workflow guards, the secret scan included | T2 adds one line there for people |
| F8 | `evals` exists for "changes to the review instructions" (evals/SKILL.md:5); the exam set holds guard and privacy cases whose clean twins would fire the pass | decision 3 |

## Tickets

### T1 — The brief names its trust boundaries
Delivers: B1, B2, B6 · Blocked by: none · Lane: logic
Budget: code +0 · tests +8 · why: B6 is pinned by a test; the rest is reference text
Seam: `references/phase-0-brainstorm.md` §4 and §5; `check-run.py` through `scripts/tests/test_check_run.py`
Accept:
- [ ] §5 brief template has an optional `## Trust boundaries` section, one line per boundary → `grep -c '^## Trust boundaries'` = 1 (B1)
- [ ] §4 names the triggers verbatim: `outside input, auth or credentials, file or network writes, shell execution, new permissions` → 1 match (B1)
- [ ] §4 says `touches none has no `## Trust boundaries`` → 1 match (B2)
- [ ] fixture brief with `## Trust boundaries` and the plain fixture brief, each with `plan()` → `0 errors · 0 warnings` (B6)
- [ ] `wc -c references/phase-0-brainstorm.md` ≤ 13,994, the baseline plus 700 (B1)
Verify: `python3 -m unittest discover -s skills/workflow/scripts/tests && f=skills/workflow/references/phase-0-brainstorm.md && grep -c '^## Trust boundaries' $f && grep -c 'outside input, auth or credentials, file or network writes, shell execution, new permissions' $f && grep -c 'touches none has no `## Trust boundaries`' $f && test $(wc -c < $f) -le 13994` (pre: fails — 50 tests pass, then 0 `## Trust boundaries` lines, exit 1)
Skills: skills/agent-docs/SKILL.md
Status: todo

### T2 — Review runs the threat pass on each boundary
Delivers: B2, B3, B4, B5 · Blocked by: T1 · Lane: logic
Budget: code +0 · tests +0
Seam: `references/phase-4-review.md` *Defects* and the `review.md` template; `SKILL-IMPACT.md`; `README.md`
Accept:
- [ ] phase-4-review.md holds the T1 trigger string and `who can send input, what it can reach, what it can change, what is logged, what fails open, what is the worst case` → 1 match each (B3)
- [ ] the review.md template's Coverage holds `Threats: none — the brief and the diff add no boundary`, and the pass fires on `a trigger the brief does not list` → 1 match each (B2, B3)
- [ ] severity: `grep -c '^| \*\*P'` = 4 (no second table) and `unmitigated plausible threat` → 1 match (B4)
- [ ] SKILL-IMPACT.md line 13 is the new row: `Trust boundaries` … `| 3 runs | trialing |`, its judge naming boundaries on trigger runs and no false alarm otherwise → 1 match (B5)
- [ ] README.md's guard list names the pass → `grep -ci 'trust boundar'` = 1 (B3)
- [ ] `wc -c references/phase-4-review.md` ≤ 13,953, the baseline plus 900 (B3)
Verify: `f=skills/workflow/references/phase-4-review.md && grep -c 'outside input, auth or credentials, file or network writes, shell execution, new permissions' $f && grep -c 'who can send input, what it can reach, what it can change, what is logged, what fails open, what is the worst case' $f && grep -c '^Threats: none — the brief and the diff add no boundary' $f && grep -c 'a trigger the brief does not list' $f && test $(grep -c '^| \*\*P' $f) -eq 4 && grep -c 'unmitigated plausible threat' $f && sed -n 13p skills/workflow/SKILL-IMPACT.md | grep -c 'Trust boundaries.*| 3 runs | trialing |' && grep -ci 'trust boundar' skills/workflow/README.md && test $(wc -c < $f) -le 13953` (pre: fails — 0 trigger-string matches, exit 1; severity rows already 4)
Skills: skills/agent-docs/SKILL.md
Status: todo

## Coverage
- Outcome → T1 (the brief names boundaries) · T2 (review.md checks each, on the reference docs)
- B1 → T1 · B2 → T1, T2 · B3 → T2 · B4 → T2 · B5 → T2 · B6 → T1
- Out of scope: full STRIDE, data-flow diagrams, threat register → untouched · `workflow threat-model` command → none added · plan-phase threat step → phase-2-plan.md untouched · check-run gate on the section → check-run.py untouched · TODO.md → untouched

## Risks
- T2 is the risk: a vague pass raises false alarms on every run that touches a file write; the six questions and the `none` line keep it bounded, and the trial measures it.
- Both references grow further past ~10 KB (F3); trimming them is a separate `workflow improve`.
- Option not taken: trigger list in `SKILL.md` (F4). After push, the installed workflow copy needs `npx skills update -g`.

## TODO impacts
none (the brief names no TODO.md item)

## Product doc impacts
- PRODUCT.md, DESIGN.md: absent in this repo.
- ROADMAP.md (skills/workflow/ROADMAP.md): no changes; it names no security or threat item.
