Command: workflow plan model-overrides
Created: 2026-10-30 · Opus 5.5
Base:    43bd7b2
Inputs:  .workflow/model-overrides/brainstorm.md @ f27a9e3
Status:  complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md; workflow `SKILL.md` run table and provenance rule, `MAINTAINING.md` §File layout · §Run folder rules · size table, `README.md` §Trying a new model)
Size: code 1097 · tests 955 · ratio 0.87 · largest touched check-run.py 882, test_check_run.py 547, test_next_step.py 408, next-step.py 215 · over 1,000: none
Decisions: 1a approve T1, T2 as listed · 2a an override accepts any Vendor · Model

## Execution state
Current: T1 verification · writer: GPT-6.1 Sol
Baseline: workflow 112 tests OK; checkup 8 tests OK; no pre-existing failures.
Uncommitted: T1 scripts, tests and skill-impact row. Pending decision: none.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | Lightest shape: one headerless table, read by next-step and checked by check-run; no brief decision adds standing cost (no deploy, pin or per-edit approval) | none |
| F2 | `checks.table` (check-run.py:149) with `heading=None` reads a whole-file table, names `path:line: key` on a bad row, rejects duplicates and empty cells except the last | reused for routing.md; an empty Effort passes `table()` and must fail in the override parser |
| F3 | `checks.decisions` (check-run.py:174), wired at check-run.py:785 and read by next-step.py:172, is a headerless run table both scripts use | `overrides(doc, keys)` sits beside it in check-run.py; next-step calls `checks.overrides` the same way |
| F4 | `model()` and `EFFORTS` (next-step.py:14-21) already validate `Vendor · Model · effort` | both move to check-run.py; the combined cell uses that parser, plus a required parsed effort to reject a missing model name; no second parser |
| F5 | check-run.py has no ROUTING.md path or key list; next-step reads `parents[1]/ROUTING.md` (next-step.py:191) with the phase columns at next-step.py:27 | the phase-column list moves to check-run.py as a constant; check-run reads keys from the skill's own ROUTING.md with `table()` |
| F6 | Headers: check_run exempts learnings.md and decisions.md (check-run.py:782); SKILL.md:142 and MAINTAINING.md:51 state the same rule | routing.md is headerless like decisions.md (the human writes it by hand); all three places name it |
| F7 | Writer seats also fill `fix:*` keys (fix:P0 … fix:operator, ROUTING.md phase table) | B5 compares the plan and review vendors with every `execute:*` and `fix:*` vendor (D3's writer-vs-reviewer intent); the brief names only `execute:*` |
| F8 | JSON has no `override` or `warning` key today; `test_unattended_decision_states` compares whole JSON objects | `override: true` appears only on an overridden key, `warning` only on a same-vendor run; other runs' JSON stays unchanged (Outcome) |
| F9 | A trial seat puts the primary first in `fallback` and prints `(trial)` (next-step.py:43-45, :55) | an overridden key sets `trial: false` and keeps the ROUTING.md fallback list unchanged (D6) |
| F10 | A blocked step nulls model and fallback (next-step.py:179-180) | it also drops `override`, so the card prints `human · …` without `(override)` |
| F11 | SKILL.md is 180 lines and 11,258 B: at its line budget and over ~10 KB (MAINTAINING.md size table) | the routing.md row is offset by a cut or a shared row; SKILL.md stays ≤ 180 lines |
| F12 | Only the human writes routing.md (D4) and looks for model changes in README.md §Trying a new model (README.md:208-212) | T2 adds one README line there |
| F13 | ROUTING.md is 5,453 B; test_next_step.py:408 caps it at 5,500 and only the human edits it | no ROUTING.md edit in this run |

## Tickets

### T1 — A run's routing.md sets its card and JSON model, checked by both scripts
Delivers: B1, B2, B3, B4, B5, B6 · Blocked by: none · Lane: logic
Budget: code +35 · tests +50 · why: two CLIs observe the same override rows
Seam: `next-step.py x --json` and its card; `check-run.py x` on a fixture run (shape: F2–F5, F7–F10)
Accept:
- [ ] routing.md row `| execute:logic | OpenAI · GPT-6 Sol | xhigh |`, logic ticket ready → JSON `model` `{"vendor": "OpenAI", "name": "GPT-6 Sol", "effort": "xhigh"}`, `context` `standard`, `approval` `auto` (B1)
- [ ] same run → JSON `fallback` equals the run's without routing.md, `override` is `true`, card has `- **Model:** GPT-6 Sol · xhigh · standard (override)` (B4)
- [ ] no routing.md, and a routing.md with only a `review` row → the plan step's card equals one literal card byte for byte, and the two JSONs are equal (B2, B3)
- [ ] routing.md row `| review | OpenAI · GPT-6 Sol | xhigh |` → exit 0, card has `- **Warning:** same vendor writes and reviews: OpenAI`; B1's routing.md → no `Warning` line (B5)
- [ ] each bad row (key `execute:nope`; cell `OpenAI`; effort `max`) → next-step exits 1, stdout empty, stderr names the row's key, no `Traceback` (B6)
- [ ] the same three rows → check-run exits 1 with an `ERROR` line naming the key; B1's routing.md → `0 errors · 0 warnings` (B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_next_step.py' && python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_check_run.py'` (pre: 26 OK · 52 OK)
Skills: none
Status: todo

### T2 — The skill docs name routing.md for the human and the agent
Delivers: D5 (docs half) · Blocked by: T1 · Lane: mechanical
Budget: code +0 · tests +0
Seam: `SKILL.md`, `MAINTAINING.md`, `README.md` in `.github/skills/workflow/`
Accept:
- [ ] SKILL.md's run table gains a `routing.md` row (written by the human) and its provenance rule names it headerless → `grep -o 'routing\.md' SKILL.md | wc -l` = 2
- [ ] MAINTAINING.md's header rule and README's *Trying a new model* list each name it → `grep -c 'routing\.md'` = 1 in each file
- [ ] SKILL.md stays in its line budget → `wc -l < SKILL.md` ≤ 180 (now 180)
Verify: `cd .github/skills/workflow && grep -c 'routing\.md' SKILL.md MAINTAINING.md README.md; wc -l < SKILL.md` (pre: 0 · 0 · 0 · 180)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

## Coverage
- Outcome → T1 (lines 1–4 observe next-step's card and JSON for the overridden run; line 3 the unchanged one)
- B1 → T1 · B2 → T1 · B3 → T1 · B4 → T1 · B5 → T1 · B6 → T1 · D5 docs → T2
- Out of scope: per-ticket overrides → untouched · `workflow route` command → untouched · overrides in `status` → untouched · overriding fallback, context or approval → untouched (T1 line 2 asserts fallback) · blocking same-vendor runs → untouched (T1 line 4 asserts exit 0) · conductor → untouched

## Risks
- T1: `override` and `warning` exist only when they apply (F8); a JSON consumer reads a missing key as false. Line 3's literal card guards today's output.
- A mistyped vendor (`Antropic`) passes B6 and silently skips the B5 warning; accepted with decision 2a.
- Option not taken: skipping routing.md checks on done runs. Wrap archives runs, so a later ROUTING.md key rename rarely reaches one.

## TODO impacts
none (the brief names no TODO item)

## Product doc impacts
- PRODUCT.md, DESIGN.md: none exist.
- ROADMAP.md: no changes; step 3's conductor reads the JSON, where an override changes only that run's `model` values.

## Deviations
- T1: F4 needed a required parsed-effort guard. A one-part model cell plus effort otherwise passes the shared optional-effort parser. Acceptance lines unchanged.
