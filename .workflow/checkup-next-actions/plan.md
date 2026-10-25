Command: workflow plan checkup-next-actions
Created: 2026-10-25 · Claude Opus 5.5
Base:    37f7b44
Inputs:  .workflow/checkup-next-actions/brainstorm.md @ 080ecdf
Status:  complete

Docs read: none in scope (checkup and workflow skills only; no PRODUCT.md or DESIGN.md)
Size: code 0 · tests 0 · ratio n/a · largest touched checkup/SKILL.md 341 lines, 23,646 B (doc) · over 1,000: none
Decisions: 1a (tickets approved 2026-10-25) · 2a (T2 receipts taken by the agent, headless and read-only in the cx clone) · replan after T2 FAIL: 1a (T3 text fix, then one paid read-only cx retry) · 2a (tickets approved 2026-10-25)

## Execution state
Current: T3 done; T2 retry awaiting specific private-data authorization
T1 @ bc2a0e2
T3 @ 51a1e53
writer: GPT-6.1 Sol
Baseline: approved content checks; check-run 0 errors, 0 warnings
Session 1: T1, T2
Session 2: T3, T2
Uncommitted: none after receipt commit
Pending decision: approve private cx contents being sent to Anthropic for T2; receipts/t2-retry-handoff.md

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The tracked files are under `.github/skills/`; `skills/<name>` are symlinks to them | T1 writes `.github/skills/checkup/references/report.md`; the brief's `skills/checkup/…` greps still work through the link |
| F2 | On this server `~/.claude/skills/checkup` → `~/.agents/skills/checkup`, an installed copy (same as the repo today) | T2 pushes and runs `npx skills update -g` here before the cx checkup, or the receipt shows the old format |
| F3 | Reuse: the card and question shapes live in workflow `SKILL.md` §The closing card and §Talking to the human; a checkup session does not load workflow | report.md restates the checkup variant (prompt fence, no Reads field) in ≤ 15 lines and names workflow `SKILL.md` as its source; no script |
| F4 | Reuse: checkup already reads `ROUTING.md` for each seat's incumbent (SKILL.md:221) | the skill → seat table holds seat names only; model and fallback come from that same read (D3) |
| F5 | Reuse: retro's `plain` line (retro/SKILL.md:26-27) | B8's line follows its wording |
| F6 | cx-intelligence @ 24d07d68 (pulled 2026-10-25): `.agents/skills/verify-cx-intelligence` exists, no `.claude/`, no `CLAUDE.md`; SKILL.md:152-153 calls the missing link 🔴 | B6 has a live instance. report.md gets one general rule (a severity that rests on a fact no file shows is asked) with this case as its example; the check text and severities stay as they are (out of scope) |
| F7 | cx live: no tracked `.DS_Store`; the 3 plans with `## Execution state` belong to complete or parked runs, not done; the dated folders sit in `.workflow/archive/` | B7's cx example does not reproduce. B7 is checked in T1's text and by "no two cards run the same command" in T2 |
| F8 | cx WORKLOG: no non-incumbent has 2+ runs on a seat (Opus 5.5 at brainstorm: 1 run) | no live promotion candidate; B5 is checked in T1's text only |
| F9 | `claude` and `codex` are installed on this server; `claude -p --permission-mode plan` runs a fresh session that cannot write | T2's sessions run headless and read-only in the clone, which must not be edited |
| F10 | SKILL.md §Output format (lines 280-308) is 1,350 B | moving it and adding 2 pointer lines leaves about 22.4 KB; B1's `< 23646` holds |
| F12 | T2 receipt: cx `TODO.md` is 19,012 B, over the ~15 KB check (checkup SKILL.md:191, "grounding cost repeats every phase"); the report named that cost, then gave no card: "a call about your own backlog" | report.md has no home for a costed finding whose fix needs a human call, so it was dropped. T3 closes the gap: such a finding gets a card whose prompt proposes the change for approval |
| F13 | cx @ 24d07d68 still holds that `TODO.md` (19,012 B, rechecked) | the retried T2 has a live finding that must yield a card: `workflow todo` → Brainstorm partner, TODO intake row → `Sonnet 5.5 · medium` / `GPT-6 Sol · high` |
| F14 | The headless run skipped Seats (receipt: "Not examined") and said so | an honest gap, not a T2 failure; running the battery is out of scope (checks unchanged). T2's prompt stays the human's literal `checkup` |
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

### T2 — receipts: checkup on cx-intelligence, then one card's prompt in a fresh session
Delivers: B2, B3, B4, B6, B7 · Blocked by: T1, T3 · Lane: operator
Budget: code +0 · tests +0
Seam: the installed checkup run headless in `~/cx-intelligence`; the receipts
Runner: agent after approval · Risk: cheap (read-only sessions in the read-only clone; no repo writes)
Handoff: after push, `npx skills update -g` on this server (background, long timeout) and `diff -q ~/.agents/skills/checkup/references/report.md .github/skills/checkup/references/report.md` → no output; pull the clone (memory: cx-intelligence-reference); `cd ~/cx-intelligence && claude -p --permission-mode plan "checkup"` → `receipts/t2-cx-checkup-2.md`; pick the first agent card, run its prompt the same way → `receipts/t2-fresh-session.md`
Accept:
- [ ] `receipts/t2-cx-checkup-2.md` → ends with numbered questions, then 1 to 3 cards each with `Why:`, `Reset:`, `Model:`, `Fallback:` and a fenced `text` prompt, then the safe-fix line; 0 `Reads:` (B2)
- [ ] a card for the cx `TODO.md` size finding (F13) whose prompt names `workflow todo` and `TODO.md`; `Model:` `Sonnet 5.5 · medium`, `Fallback:` `GPT-6 Sol · high`; every other agent card equals its seat's `ROUTING.md` row (B3)
- [ ] the verify-link finding → a numbered question citing `.agents/skills/verify-cx-intelligence` and the missing `.claude/`; no 🔴 line for it (B6)
- [ ] no two cards in the receipt run the same command (B7)
- [ ] `receipts/t2-fresh-session.md` → its first actions read the paths the prompt names; it asks nothing about the checkup's context (B4)
Verify: receipt: `receipts/t2-cx-checkup-2.md` (the first receipt stays as the failed attempt) — questions → cards → safe-fix line, 0 `Reads:`; `receipts/t2-fresh-session.md` — named paths read, no context question (pre: no receipt)
Skills: none
Status: awaiting-human

## Coverage
- Outcome → T2 (the cx-intelligence checkup receipt shows questions, cards and the safe-fix line in that order)
- B1 → T1 · B2 → T1, T3, T2 · B3 → T1, T2 · B4 → T2 · B5 → T1 · B6 → T1, T2 · B7 → T1, T3, T2 · B8 → T1
- Out of scope: full SKILL.md trim → untouched · `ROUTING.md` → untouched · checks, severities, safe-fix allow-list → untouched (F6) · cx-intelligence → read only

## Risks
T2 is the risk: one more paid headless session (~40 s), and the model may still punt; if it does, the next replan builds a fixture repo instead. A headless checkup may differ from an interactive one (it cannot be asked the safe-fix question), and the receipt depends on what cx holds that day. If the headless run stalls on a question, the human runs `checkup` once in their own session instead.
Outside its files: `npx skills update -g` refreshes every installed j-skill on this server to current main.
Not taken: pointing report.md at workflow `SKILL.md` for the card shape (saves ~10 lines but makes every checkup read ~12 KB more).

## TODO impacts
none (the brief names no TODO item)

## Product doc impacts
- PRODUCT.md, DESIGN.md, ROADMAP.md: not present at the repo root
- `SKILL-IMPACT.md:18` (checkup trial) → still true; the rule moves to report.md unchanged (F11)

## Deviations
- T2: first paid session returned 0 cards and skipped Seats; B2 fails, B3/B7 unexercised, B4 not run. No retry. Receipts: t2-cx-checkup.md, t2-verification.md.
- T1: agent-docs requires the SKILL-IMPACT.md trial row; added it. Copilot registration initially needed network access; its T2 retry passed. No test assertions changed.
- T2 retry: automatic approval review rejected the Claude launch before execution, requiring explicit authorization to send private cx-intelligence contents to Anthropic. Installation and clone refresh passed; no paid retry or fresh session started. See receipts/t2-retry-preflight.md and receipts/t2-retry-handoff.md.
