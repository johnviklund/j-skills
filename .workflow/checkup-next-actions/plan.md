Command: workflow plan checkup-next-actions
Created: 2026-10-25 · Claude Opus 5.5
Base:    e192505
Inputs:  .workflow/checkup-next-actions/brainstorm.md @ 080ecdf
Status:  complete

Docs read: none in scope (checkup and workflow skills only; no PRODUCT.md or DESIGN.md)
Size: code 0 · tests 0 · ratio n/a · largest touched checkup/SKILL.md 314 lines (doc), report.md 89 lines · over 1,000: none
Decisions: 1a (tickets approved 2026-10-25) · 2a (T2 receipts taken by the agent, headless and read-only in the cx clone) · replan after T2 FAIL: 1a (T3 text fix, then one paid read-only cx retry) · 2a (tickets approved 2026-10-25) · replan 2: 1a (fixture repo, 2026-10-25) · 2a (T4, T5, T2 approved 2026-10-25) · 3a (two paid fixture sessions, USD 1 cap each, approved 2026-10-25)

## Execution state
Current: T5 and T4 done; next T2 (paid fixture sessions pre-approved, 3a)
T1 @ bc2a0e2 · T3 @ 51a1e53 · T5 @ ee4c44e · T4 @ bfa6d38 · writer: GPT-6.1 Sol · Baseline: approved content checks; check-run 0 errors, 0 warnings
Session 1: T1, T2 · Session 2: T3, T2
Session 3: T5, T4, T2 · Uncommitted: T2 handoff and execution state until commit
## Findings
| # | What is true | What it changes |
|---|---|---|
| F1, F2, F10 | The tracked files are under `.github/skills/`; `skills/<name>` are symlinks to them; On this server `~/.claude/skills/checkup` → `~/.agents/skills/checkup`, an installed copy (same as the repo today); SKILL.md §Output format (lines 280-308) is 1,350 B | T1 writes `.github/skills/checkup/references/report.md`; the brief's `skills/checkup/…` greps still work through the link; T2 pushes and runs `npx skills update -g` here before the cx checkup, or the receipt shows the old format; moving it and adding 2 pointer lines leaves about 22.4 KB; B1's `< 23646` holds |
| F3–F5 | Reuse: the card and question shapes live in workflow `SKILL.md` §The closing card and §Talking to the human; a checkup session does not load workflow; Reuse: checkup already reads `ROUTING.md` for each seat's incumbent (SKILL.md:221); Reuse: retro's `plain` line (retro/SKILL.md:26-27) | report.md restates the checkup variant (prompt fence, no Reads field) in ≤ 15 lines and names workflow `SKILL.md` as its source; no script; the skill → seat table holds seat names only; model and fallback come from that same read (D3); B8's line follows its wording |
| F6 | cx-intelligence @ 24d07d68 (pulled 2026-10-25): `.agents/skills/verify-cx-intelligence` exists, no `.claude/`, no `CLAUDE.md`; SKILL.md:152-153 calls the missing link 🔴 | B6 has a live instance. report.md gets one general rule (a severity that rests on a fact no file shows is asked) with this case as its example; the check text and severities stay as they are (out of scope) |
| F7–F8 | cx live: no tracked `.DS_Store`; the 3 plans with `## Execution state` belong to complete or parked runs, not done; the dated folders sit in `.workflow/archive/`; cx WORKLOG: no non-incumbent has 2+ runs on a seat (Opus 5.5 at brainstorm: 1 run) | B7's cx example does not reproduce. B7 is checked in T1's text and by "no two cards run the same command" in T2; no live promotion candidate; B5 is checked in T1's text only |
| F12–F14 | T2 receipt: cx `TODO.md` is 19,012 B, over the ~15 KB check (checkup SKILL.md:191, "grounding cost repeats every phase"); the report named that cost, then gave no card: "a call about your own backlog"; cx @ 24d07d68 still holds that `TODO.md` (19,012 B, rechecked); The headless run skipped Seats (receipt: "Not examined") and said so | report.md has no home for a costed finding whose fix needs a human call, so it was dropped. T3 closes the gap: such a finding gets a card whose prompt proposes the change for approval; the retried T2 has a live finding that must yield a card: `workflow todo` → Brainstorm partner, TODO intake row → `Sonnet 5.5 · medium` / `GPT-6 Sol · high`; an honest gap, not a T2 failure; running the battery is out of scope (checks unchanged). T2's prompt stays the human's literal `checkup` |
| F9, F15 | Retry stream: in plan mode, Claude wrote `~/.claude/plans/checkup-snug-beaver.md`, called ExitPlanMode, and the final `result` was a summary without cards; `claude` and `codex` are installed on this server; `claude -p --permission-mode plan` runs a fresh session that cannot write | the ending failure comes from plan mode, not report.md. T2 runs in default mode with Write/Edit/NotebookEdit disallowed; report.md still says nothing follows the safe-fix line; T2's sessions run headless and read-only in the clone, which must not be edited |
| F16 | Retry stream: the session found `~/.agents/skills/workflow` but only grepped ROUTING.md for `Last verified`; report.md never gives ROUTING.md's path or says the Model line must be a literal value | T4 names `../workflow/ROUTING.md` from checkup's folder and bans a seat name on the Model and Fallback lines (B3) |
| F17 | Retry receipt: Question 1 cited `.claude/` but not `.agents/skills/verify-cx-intelligence`, and the Skills line already asserted the consequence | T4: a question cites every path its finding rests on, and the section line says "see Question N" without the consequence (B6) |
| F18 | No AGENTS.md or stated cost ceiling in this repo; `claude -p` has `--max-budget-usd` | every paid session is `costly`: dry run (the fixture build), approval, receipt; each session capped at USD 1 |
| F19 | A fixture repo in `/tmp` holds no private data, so the Anthropic data gate from the retry falls away; the cx clone stays untouched | B2/B4/B6/B7 move from cx to the fixture (correction to D8, put to the human); cx stays the source the fixture copies its shape from |
| F11 | `SKILL-IMPACT.md:18` trials checkup's "each action names the cost of leaving it" rule (trialing, 3 checkups) | report.md keeps that rule word for word, so the trial goes on measuring the same thing |

## Tickets

### T1 — report.md holds the closing format; SKILL.md points to it and invokes plain
Delivers: B1, B2, B3, B5, B6, B7, B8 · Blocked by: none · Lane: logic
Budget: code +0 · tests +0
Seam: `grep` and `wc -c` over `skills/checkup/SKILL.md` and `skills/checkup/references/report.md`
Accept:
- [x] `wc -c < skills/checkup/SKILL.md` → under 23646; `grep -c '^## Output format\|Recommended next'` on it → 0; `grep -c 'references/report.md'` → ≥ 1 (B1)
- [x] `grep -n '`plain`' skills/checkup/SKILL.md` → a line telling checkup to invoke `plain` once before writing the report (B8)
- [x] report.md card template → bullets `Why:`, `Reset:`, `Model:`, `Fallback:`, then a fenced `text` prompt; `grep -c 'Reads:'` on report.md → 0 (B2)
- [x] report.md skill → seat table → `memory.*` maps to `Brainstorm partner`, model and fallback read from `ROUTING.md`; `grep -cE 'Sonnet|Opus|GPT'` on report.md → 0 (B3)
- [x] report.md question rule → ➡️ option first, a reason on every option, at most 5 questions, unknown facts asked with their evidence (the cx verify-link case); human card reads `Model: human · ` (B5, B6)
- [x] report.md order → questions, then at most 3 cards, then the safe-fix line; warnings that share one fix → one card (B7)
Verify: `wc -c < skills/checkup/SKILL.md; grep -c '^## Output format\|Recommended next' skills/checkup/SKILL.md; grep -n '`plain`' skills/checkup/SKILL.md; grep -cE 'Why:|Reset:|Model:|Fallback:|Brainstorm partner|➡️|Model: human' skills/checkup/references/report.md; grep -cE 'Reads:|Sonnet|Opus|GPT' skills/checkup/references/report.md` (pre: 23646 · 3 · no output · new file · new file)
Skills: .github/skills/agent-docs/SKILL.md, .github/skills/plain/SKILL.md
Status: done @ bc2a0e2
Writer: GPT-6.1 Sol

### T3 — a costed finding is never dropped for needing a human call
Delivers: B2, B7 · Blocked by: T1 · Lane: logic
Budget: code +0 · tests +0 · why: doc-only, 3–5 lines in report.md
Seam: `grep` over `skills/checkup/references/report.md`
Accept:
- [x] report.md §Action cards → a finding with a stated cost whose fix needs a human call gets a card whose prompt has the agent propose the change and wait for approval; `grep -c 'propose'` → ≥ 1 (B2)
- [x] report.md §Action cards → an example: `TODO.md` over ~15 KB → a `workflow todo` card that proposes what to archive; `grep -c 'TODO.md'` → ≥ 1 (B2)
- [x] report.md → a line allowing "No action earns a card" only when no ⚠️/🔴 names a cost; `grep -c 'No action earns a card'` → 1 (B7)
Verify: `grep -c 'propose' skills/checkup/references/report.md; grep -c 'TODO.md' skills/checkup/references/report.md; grep -c 'No action earns a card' skills/checkup/references/report.md` (pre: 0 · 0 · 0)
Skills: .github/skills/agent-docs/SKILL.md, .github/skills/plain/SKILL.md
Status: done @ 51a1e53
Writer: GPT-6.1 Sol

### T4 — report.md: literal models, every evidence path, nothing after the safe-fix line
Delivers: B2, B3, B6 · Blocked by: T3 · Lane: logic
Budget: code +0 · tests +0 · why: doc-only, about 6 lines in report.md
Seam: `grep` over `skills/checkup/references/report.md`
Accept:
- [x] §Skill to seat names `../workflow/ROUTING.md` as the rows to read; `grep -c 'workflow/ROUTING.md'` → ≥ 1, `grep -cE 'Sonnet|Opus|GPT'` → 0 (B3)
- [x] Model and Fallback hold a model and effort copied from those rows; `grep -c 'never a seat name'` → 1 (B3)
- [x] §Questions → a question cites every path its finding rests on, and the section line reads "see Question N" without the consequence; `grep -c 'see Question'` → ≥ 1 (B6)
- [x] §Safe-fix line → `grep -c 'Nothing follows the safe-fix line'` → 1 (B2)
Verify: `R=skills/checkup/references/report.md; grep -c 'workflow/ROUTING.md' $R; grep -c 'never a seat name' $R; grep -c 'see Question' $R; grep -c 'Nothing follows the safe-fix line' $R; grep -cE 'Sonnet|Opus|GPT' $R` (pre: 0 · 0 · 0 · 0 · 0)
Skills: .github/skills/agent-docs/SKILL.md, .github/skills/plain/SKILL.md
Status: done @ bfa6d38
Writer: GPT-6.1 Sol

### T5 — a fixture repo that holds the three live findings
Delivers: B2, B6 · Blocked by: none · Lane: logic
Budget: code +40 · tests +0 · why: the Verify run is the script's test
Seam: `.workflow/checkup-next-actions/scripts/make-fixture.sh` → `/tmp/checkup-fixture`
Accept:
- [x] run twice → a clean git repo each time, one commit; `TODO.md` over 15,360 B (copied shape, synthetic text); `.agents/skills/verify-fixture/SKILL.md` present; no `.claude/` (B6)
- [x] the fixture holds an `AGENTS.md`, a `MEMORY.md` with one page, and a done `.workflow/` run, so every report section has something to read; no file copied from cx (B2)
Verify: `S=.workflow/checkup-next-actions/scripts/make-fixture.sh; bash $S && bash $S && cd /tmp/checkup-fixture && git status --short | wc -l && git rev-list --count HEAD && wc -c < TODO.md && ls .agents/skills/verify-fixture/SKILL.md AGENTS.md MEMORY.md && ! test -e .claude` (pre: new file)
Skills: none
Status: done @ ee4c44e
Writer: GPT-6.1 Sol

### T2 — receipts: checkup on the fixture, then one card's prompt in a fresh session
Delivers: B2, B3, B4, B6, B7 · Blocked by: T1, T3, T4, T5 · Lane: operator
Budget: code +0 · tests +0
Seam: the installed checkup run headless in `/tmp/checkup-fixture`; the receipts
Runner: agent after approval · Risk: costly (two paid sessions, no stated ceiling; each capped `--max-budget-usd 1`; fixture only, no private data)
Handoff: push; `npx skills update -g` (background, long timeout); `diff -q ~/.agents/skills/checkup/references/report.md .github/skills/checkup/references/report.md` → no output. Dry run: T5's script, then its Verify. Run `cd /tmp/checkup-fixture && claude -p --permission-mode default --allowedTools "Read Grep Glob Bash Skill" --disallowedTools "Write Edit NotebookEdit" --max-budget-usd 1 --verbose --output-format stream-json "checkup"` → stream in /tmp, final `result` → `receipts/t2-fixture-checkup.md`. Pass → run the `workflow todo` card's prompt the same way → `receipts/t2-fresh-session.md`. A failed clause stops the ticket.
Accept:
- [ ] the final `result` text ends with numbered questions, then 1 to 3 cards each with `Why:`, `Reset:`, `Model:`, `Fallback:` and a fenced `text` prompt, then the safe-fix line; 0 `Reads:`; no two cards run the same command (B2, B7)
- [ ] the `TODO.md` card names `workflow todo`; `Model:` starts `Sonnet 5.5 · medium`, `Fallback:` `GPT-6 Sol · high`; every other agent card's Model equals its seat's ROUTING.md row (B3)
- [ ] a numbered question cites `.agents/skills/verify-fixture` and the missing `.claude/`; no 🔴 line for it (B6)
- [ ] `receipts/t2-fresh-session.md` → its first tool calls read `TODO.md`; it asks nothing about the checkup's context (B4)
- [ ] fixture HEAD and `git status --short` are the same before and after both sessions; `~/cx-intelligence` is not touched
Verify: receipt: `receipts/t2-fixture-checkup.md` — questions → 1–3 cards → safe-fix line, `Sonnet 5.5 · medium` on the TODO card, 0 `Reads:`; `receipts/t2-fresh-session.md` — `TODO.md` read first, no context question (pre: no receipt; cx receipts stay as the failed attempts)
Skills: none
Status: todo
## Coverage
- Outcome → T2 (the fixture checkup receipt shows questions, cards and the safe-fix line in that order)
- B1 → T1 · B2 → T1, T3, T4, T5, T2 · B3 → T1, T4, T2 · B4 → T2 · B5 → T1 · B6 → T1, T4, T5, T2 · B7 → T1, T3, T2 · B8 → T1
- Out of scope: full SKILL.md trim → untouched · `ROUTING.md` → untouched · checks, severities, safe-fix allow-list → untouched (F6) · cx-intelligence → read only
## Risks
T2 is the risk: two paid sessions (about USD 0.30 each on the cx retry), and the model may still punt on a clause; a third failure goes back to the human, not to another retry. A fixture may miss a cx-only behaviour; the cx receipts stay as the record of the live repo.
Outside its files: `npx skills update -g` refreshes every installed j-skill on this server to current main. Not taken: a third cx run (private data gate, larger repo, the same plan-mode ending); pointing report.md at workflow `SKILL.md` for the card shape (every checkup would read ~12 KB more).
## TODO impacts
none (the brief names no TODO item)

## Product doc impacts
- PRODUCT.md, DESIGN.md, ROADMAP.md: not present at the repo root; `SKILL-IMPACT.md:18` (checkup trial) → still true; the rule moves to report.md unchanged (F11)

## Deviations
- T2: first paid session returned 0 cards and skipped Seats; B2 fails, B3/B7 unexercised, B4 not run. No retry. Receipts: t2-cx-checkup.md, t2-verification.md.
- T1: agent-docs requires the SKILL-IMPACT.md trial row; added it. Copilot registration initially needed network access; its T2 retry passed. No test assertions changed.
- T2 retry: automatic approval review rejected the Claude launch before execution, requiring explicit authorization to send private cx-intelligence contents to Anthropic. Installation and clone refresh passed; no paid retry or fresh session started. See receipts/t2-retry-preflight.md and receipts/t2-retry-handoff.md. Then, after explicit user 1a: three cards appeared, including workflow todo for TODO.md, but model/fallback fields remained seat placeholders. The verify question omitted the required .agents/skills path, and a later final summary replaced the report ending. Verification failed; no fresh-session test or additional paid retry ran. See receipts/t2-verification-2.md. The earlier preflight entry records the initial rejection only.
- Replan 2 (approved 2a, 3a): T2 moves to a `/tmp` fixture (F19) in default mode with writes disallowed (F15); T4 closes the model and evidence-path gaps (F16, F17).
