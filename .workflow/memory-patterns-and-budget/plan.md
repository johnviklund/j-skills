Command: workflow plan memory-patterns-and-budget
Created: 2026-10-26 · claude-opus-5-5
Base:    2d3a44a
Inputs:  .workflow/memory-patterns-and-budget/brainstorm.md @ 068776c
Status:  done

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
Size: code 0 · tests 0 · ratio n/a (doc run) · largest touched memory.remember/SKILL.md 296 (26,820 B), memory.compact/SKILL.md 250 (16,246 B), SKILL-IMPACT.md 34 · over 1,000: none
Decisions: 1a (a run missing from a matching page is added to its proposed copy, count bumped) · 2a (T2 desk-check receipt) · 3a ticket list approved 2026-10-26

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | compact step 1 reads done runs' `review.md`/`learnings.md` only "for content that contradicts or confirms a page" (memory.compact/SKILL.md:76-78); nothing compares one run with another | T1 adds the cross-run comparison to step 1 and a class to step 3 |
| F2 | compact already writes a full mirror to `memory.proposed/` (:170-173) and a fixed summary block (:180-189) | a repeat page is one more file there; the summary gains one count; no new output file |
| F3 | Data: 9 done runs, 7 with `learnings.md`, 47 lines; 3 of them have no header (retire-date-gates, run-ratio-and-retire, slop-guards); mark forms vary (`[routed → none: …]` at line end, `[routed → …]` first) | "every line" means every bullet, header or not, mark anywhere on the line |
| F4 | Real data, by hand: the guard-key lines of growth-ratchets, guard-keys, run-ratio-and-retire and retire-date-gates all match the legacy entry `A new guard needs one test per key` (skills/workflow/MEMORY.md); its Source lists 3 of the 4, not retire-date-gates. The grep-proof pair (checkup-next-actions, guard-keys) shares a topic, not a fix. slop-guards' two lines are one run | real data proposes 0 new pages, so B1's positive branch has no live instance: T1 proves it on a planted pair in scratch copies |
| F5 | Neither skill covers a lesson that matches a page whose `Evidence` lacks the run: B1 excludes it (a page exists), B3 covers only runs already listed | decision 1 |
| F6 | j-skills memory is legacy inline (2 `###` entries in skills/workflow/MEMORY.md, no `memory/` folder) | the dry run reads them as pages-to-be, per compact step 3 *Legacy inline* |
| F7 | remember sends rules to `AGENTS.md` at step 2 (memory.remember/SKILL.md:173), step 4 *Promote* (:202) and step 6 (:218), with no cost check; the admission test (:127-143) gates memory pages only | T2 adds one `## The AGENTS.md cost test` section beside the admission test and points step 2's `AGENTS.md` bullet at it |
| F8 | j-skills has no `AGENTS.md`; the other repo in use has a 135-line one with no stated cap | B5's cap branch fires nowhere today: checked on a fixture, not live |
| F9 | Reuse: agent-docs defines *Context load* (agent-docs/SKILL.md:29); the admission test is the shape for a gate; SKILL-IMPACT.md row 13 is the row pattern. No script or helper is implied | T2 points to agent-docs instead of restating; no new code |
| F10 | checkup-next-actions learned that a grep proves the words exist, not that an agent follows them | each ticket adds a by-hand receipt beside its greps |
| F11 | Lightest shape: two doc edits, no script, no standing cost; no brief decision adds a deploy, pin or approval | none to put to the human |

## Tickets

### T1 — compact proposes a page for a lesson two runs repeat
Delivers: B1, B2, B3, B6 · Blocked by: none · Lane: logic
Budget: code +0 · tests +0 · why: doc-only, about 12 lines in memory.compact/SKILL.md
Seam: `skills/memory.compact/SKILL.md` steps 1, 3, 6; `skills/workflow/SKILL-IMPACT.md`
Accept:
- [x] Step 1 reads `learnings.md` of the `10 most recent done runs`, every line, `` `[drop]` and `routed → none` `` lines included → 1 match each (B1)
- [x] Step 3 defines `**Unpaged repeat**`: 2+ runs with the `same cause and the same fix`, no page yet → 1 match each (B1)
- [x] Proposed page: `Occurrences: 2`, `one entry per run`, admission test applied; skill-owned match `named in the duplication report, not paged`; summary `Unpaged repeats: U` → 1 match each (B2)
- [x] A page that `already lists the run` → not proposed again; one that `does not list the run yet` → the run is added to its proposed copy and `Occurrences` bumped → 1 match each (B3)
- [x] `receipts/t1-compact-dry-run.md`: 7 real files → `new pages: 0`, `retire-date-gates → added to A new guard needs one test per key`, grep pair `different fix`; planted pair → `new pages: 1`, `Occurrences: 2` (B1, B2, B3)
- [x] SKILL-IMPACT.md gains `| memory.compact | … | 3 runs | trialing |`, judge "a proposed repeat page in the next 3 runs", in one commit with the SKILL.md edit only (`git show --stat --format= <sha>`); `wc -c` ≤ 17,446 (B6)
Verify: `C=skills/memory.compact/SKILL.md; grep -c '10 most recent done runs' $C; grep -c 'routed → none' $C; grep -c '\*\*Unpaged repeat\*\*' $C; grep -c 'same cause and the same fix' $C; grep -c 'one entry per run' $C; grep -c 'named in the duplication report, not paged' $C; grep -c 'Unpaged repeats: U' $C; grep -c 'already lists the run' $C; grep -c 'does not list the run yet' $C; grep -c '| memory.compact | .*| 3 runs | trialing |' skills/workflow/SKILL-IMPACT.md; test $(wc -c < $C) -le 17446 && test -f .workflow/memory-patterns-and-budget/receipts/t1-compact-dry-run.md` (pre: 0 on every grep; size passes; receipt missing, exit 1)
Skills: skills/agent-docs/SKILL.md · skills/plain/SKILL.md
Status: done @ 94f353b
Writer: GPT-6.1 Sol

### T2 — remember routes a low-value AGENTS.md rule elsewhere
Delivers: B4, B5, B6 · Blocked by: none · Lane: logic
Budget: code +0 · tests +0 · why: doc-only, about 10 lines in memory.remember/SKILL.md
Seam: `skills/memory.remember/SKILL.md` new section and step 2; `skills/workflow/SKILL-IMPACT.md`
Accept:
- [x] `## The AGENTS.md cost test` sits after the admission test and step 2's `AGENTS.md` bullet names it → `grep -c 'AGENTS.md cost test'` = 2 (B4)
- [x] The test asks `cause a mistake on a typical task in this repo`; a no routes the rule to its owner, leaving `at most a one-line pointer` in `AGENTS.md` → 1 match each (B4)
- [x] A stated cap with the file `within 10% of` it → remember `names one existing line to remove or move`; `no stated cap` → only the removal test runs → 1 match each (B5)
- [x] The section points to agent-docs for `Context load` instead of defining it → 1 match (B4)
- [x] `receipts/t2-remember-desk-check.md`: live-run-finder rule → `routed to a memory page`; `npx skills update -g` rule → `kept in AGENTS.md`; fixture capped at 40 holding 37 lines → `names 1 line to move` (B4, B5)
- [x] SKILL-IMPACT.md gains `| memory.remember | … | 3 runs | trialing |`, judge "a routed-away rule in the next 3 runs", in one commit with the SKILL.md edit only; `wc -c` ≤ 27,720 (B6)
Verify: `R=skills/memory.remember/SKILL.md; grep -c 'AGENTS.md cost test' $R; grep -c 'cause a mistake on a typical task in this repo' $R; grep -c 'at most a one-line pointer' $R; grep -c 'within 10% of' $R; grep -c 'names one existing line to remove or move' $R; grep -c 'no stated cap' $R; grep -c 'Context load' $R; grep -c '| memory.remember | .*| 3 runs | trialing |' skills/workflow/SKILL-IMPACT.md; test $(wc -c < $R) -le 27720 && test -f .workflow/memory-patterns-and-budget/receipts/t2-remember-desk-check.md` (pre: 0 on every grep; size passes; receipt missing, exit 1)
Skills: skills/agent-docs/SKILL.md · skills/plain/SKILL.md
Status: done @ 43588b3
Writer: GPT-6.1 Sol

## Coverage
- Outcome → T1 (compact text + dry-run receipt) · T2 (remember text + desk-check receipt)
- B1 → T1 · B2 → T1 · B3 → T1 · B4 → T2 · B5 → T2 · B6 → T1, T2
- Out of scope: repeat-finding script → none added · `README.md`/skill line caps → untouched · ~40-page ceiling → untouched · agent-docs → untouched

## Risks
- T1 is the riskier: "same cause and the same fix" is a judgement call, and a loose reading pages topic matches (F4's grep-proof pair is the test of it).
- Both receipts are written by the same model that writes the text (F10); review should rerun one by hand.
- Not taken: a paid `claude -p` fixture run of remember; the desk check costs nothing and the cap branch has no live repo (F8).

## TODO impacts
none — the brief names no TODO.md item

## Product doc impacts
No PRODUCT.md, DESIGN.md or root ROADMAP.md in this repo; skills/workflow/ROADMAP.md is not touched by these edits.
