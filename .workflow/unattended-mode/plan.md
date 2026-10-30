Command: workflow plan unattended-mode
Created: 2026-10-30 · Opus 5.5
Base:    b02cf59
Inputs:  .workflow/unattended-mode/brainstorm.md @ 59d3763
Status:  complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md)
Size: code 1073 · tests 911 · ratio 0.85 · largest touched check-run.py 840, test_check_run.py 527 · over 1,000: none
Decisions: 1a (decisions.md has no header) · 2a (a waiting decision replaces a ticket or finding blocker) · 3a (tickets approved as listed)

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | `Doc.header()` reads lines 1–5 only (`check-run.py:138`); the brief's `Mode:` is line 6 | T1 reads line 6 with `Doc._field(5)`; the five-line header rule stays |
| F2 | `decisions.md` is not in `ARTIFACTS` (`check-run.py:47`): `check_layout` warns on it, and every listed artifact but `learnings.md` must carry the provenance header (`:741`) | T1 adds it to `ARTIFACTS` and exempts it from the header like `learnings.md` (decision 1) |
| F3 | Reuse: `table()` in `next-step.py:17` already parses a headed table, rejects wrong columns, short rows and duplicate IDs | T1 moves it into `check-run.py`; both scripts call the one copy. Its message "only Notes allowed empty" becomes "only the last column" |
| F4 | Blockers today are `{ticket, action}` (`next-step.py:118`) and `{findings, action}` (`:181`); any blocker nulls the model and the card prints `human · <action>` (`:77`, `:197`) | The decision blocker reuses that path; no new card code |
| F5 | `RECEIPTS` (`check-run.py:65`) counts every `*.md` as a receipt | Answering a row is never a code change and never reopens review |
| F6 | The version line is the workflow `README.md:5`, `Version 2.1.`; the root `README.md` has none | B8 edits `.github/skills/workflow/README.md` |
| F7 | Wrap step 5 moves a finished roadmap step to `ROADMAP_ARCHIVE.md` (`wrap.md:71-75`) | B8's ROADMAP half is wrap's normal step, not a ticket |
| F8 | The brief header template (`phase-0-brainstorm.md:164-168`) has no `Mode:` line, though D4 sets mode at brainstorm | T2 adds it there |
| F9 | Always-stop sources hold: P0/P1 defer and the cycle bound `phase-4-review.md:185-193`; UI stop `phase-3-execute.md:51-54`; operator handoff `:78-84` | T2 lists them once in `unattended.md` and points back |
| F10 | Lightest shape: one script ticket and one doc ticket; no brief decision adds a deploy, pin or per-edit approval | No standing cost to raise |

## Tickets

### T1 — decisions.md and Mode: checked, and a waiting row blocks the card
Delivers: B1, B3, B4, B5, B6, B7 · Blocked by: none · Lane: logic
Budget: code +30 · tests +45 · why: six states across two existing seams, one parametrized case each
Seam: `check-run.py <slug>` exit code and output; `next-step.py <slug> --json` and its card
Accept:
- [ ] Brief line 6 `Mode: unattended`, and separately `Mode: attended`, with a well-formed `decisions.md` → check-run exits 0 and prints no line naming `Mode`, and none naming `decisions.md` (B1, B6)
- [ ] Brief line 6 `Mode: sometimes` → check-run exits 1 with an ERROR naming `Mode` (B1)
- [ ] A `decisions.md` row with Status `maybe`, and separately a row with 5 cells → check-run exits 1 with an ERROR naming that row's ID (B6)
- [ ] Row `D1` `assumed`, and separately `answered` → `next-step.py --json` equals the same run's output without `decisions.md`; `blocker` is null (B3, B5)
- [ ] Row `D2` `waiting`, Question `Which port?` → `blocker == {"decision": "D2", "action": "Which port?"}`, `model` null, card contains `**Model:** human · Which port?` (B4)
- [ ] Existing `test_next_step.py` and `test_check_run.py` cases → pass with no assertion edited (B7)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests` (pre: 109 OK · 8 OK)
Skills: none
Status: todo

### T2 — unattended.md holds the rules; the hub points to it; version 3.0.0
Delivers: B2, B8 · Blocked by: T1 · Lane: logic
Budget: code +0 · tests +0
Seam: `grep` of `SKILL.md`, `references/unattended.md`, `references/phase-0-brainstorm.md`, `README.md` under `.github/skills/workflow/`
Accept:
- [ ] `SKILL.md` → `grep -c 'references/unattended.md'` returns 1 (B2)
- [ ] `grep -rl '^## Always stop'` over the skill → prints only `references/unattended.md`; that section has exactly 5 bullets, one per D3 case (B2)
- [ ] `unattended.md` → `grep -c '^| ID | Phase | Question | Default | Status | Answer |$'` returns 1, the columns T1 accepts (B2)
- [ ] `phase-0-brainstorm.md` → `grep -c '^Mode:'` returns 1, in the brief header template (B2)
- [ ] `README.md` → `grep -c 'Version 3.0.0'` returns 1 and `grep -c 'Version 2.1'` returns 0 (B8)
Verify: `W=.github/skills/workflow; grep -c 'references/unattended.md' $W/SKILL.md; grep -rl '^## Always stop' $W; grep -c '^| ID | Phase | Question | Default | Status | Answer |$' $W/references/unattended.md; grep -c '^Mode:' $W/references/phase-0-brainstorm.md; grep -c 'Version 3.0.0' $W/README.md` (pre: new file — 0 · none · not found · 0 · 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

## Coverage
- Outcome → T1 (the blocker on `next-step.py --json`) · T2 (the never-wait rules, version)
- B1 → T1 · B2 → T2 · B3 → T1 · B4 → T1 · B5 → T1 · B6 → T1 · B7 → T1 · B8 → T2, wrap step 5 (ROADMAP, F7)
- Out of scope: the conductor → untouched · an unattended brainstorm → untouched (phase-0 gains only the header line) · a decision model → untouched

## Risks
- T1 moves the routing table parser that every card uses; the existing routing tests cover it.
- A waiting decision replaces a ticket or finding blocker on the same step (decision 2).
- Not taken: gating the blocker on `Mode: unattended`; `decisions.md` is read whenever it exists.

## TODO impacts
none named in the brief

## Product doc impacts
- `ROADMAP.md`: step 2 `unattended-mode` moves to `ROADMAP_ARCHIVE.md` at wrap.
- No `PRODUCT.md` or `DESIGN.md` in this repo.
