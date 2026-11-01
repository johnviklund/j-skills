Command: workflow plan correction-mining
Created: 2026-11-01 · Opus 5.5
Base:    83c2f24
Inputs:  .workflow/correction-mining/brainstorm.md @ 7b58235
Status:  complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md); ROADMAP.md row 3 by grep
Size: code 227 · tests 0 · ratio 0 · largest touched retro/SKILL.md 151, checkup/references/seats.md 76 · new corrections.py, tests/test_corrections.py · over 1,000: none
Decisions: 1a (tickets approved) · 2a (checkup calls the script from references/seats.md)

## Execution state
T1 @ 00623b1
writer: GPT-6.1 Sol
Session 1: T1
Baseline: workflow 126 tests OK; checkup 30 tests OK.
Current: T2 todo; no pending decision.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | This session's own tool output holds the phrases `doesn't want to proceed with this tool use` and `[Request interrupted by user`, inside `tool_result` text | Match record shapes only: a user `text` block that starts with `[Request interrupted by user`, a `tool_result` whose content starts with `The user doesn't want to proceed`; a substring match counts quotes; each fixture holds a quoting near-miss |
| F2 | Claude Code 2.1.314 writes a denial with a reason as `...the user said:\n<text>` inside the `tool_result` (string in the binary) | B3: for such a denial the text after `the user said:` is the redirect, not the next user turn |
| F3 | No human denial exists on this machine: 0 in 239 Claude files; all 4 Copilot denials are `unattended_fallback` in `/tmp` cwds | B2 and the Copilot half of B4 are checked on fixtures only; no live denial line |
| F4 | 97 of 208 Codex rollouts are subagents (`session_meta.payload.source` holds `subagent`, 96 are `guardian_review`), one with a `turn_aborted` | Skip a Codex file whose source is a subagent; skip Claude records with `isSidechain: true` |
| F5 | Codex writes an abort twice: `event_msg` `turn_aborted` with `reason` and a `developer` or `user` message starting `<turn_aborted>`; real user turns are `item_completed` items of type `UserMessage` | Count only the `event_msg`; the redirect is the next `UserMessage` item |
| F6 | Claude user turns that are not the human: `isMeta`, `tool_result` blocks, strings starting `<` (`<command-name>`, `<task-notification>`, `<bash-input>`) | A redirect is the first user `text` or string turn that is none of these |
| F7 | In this repo, the interrupted Claude turns had no `tool_use` since the last human turn (3 interrupts, 2 sessions, 3.3 and 7.0 days old) | B1 key for a text-only turn is `interrupt · no tool`; a live line in T1 expects it as a 2-session repeat with `--days 30` |
| F8 | Copilot keeps the tool on `permission.requested` (`permissionRequest.kind`, `commands[0].identifier`), joined to `permission.completed` by `requestId`; a denial's `result.kind` starts `denied` | Copilot key is `denial · <kind> · <identifier>` |
| F9 | cwd lives in Claude records (`cwd`), Codex `session_meta.payload.cwd`, Copilot `session.start` `data.context.cwd` | B6 reads the session's first cwd; repo root is the parent of `--git-common-dir`, so `.worktrees/<slug>` sessions count; a sibling `<repo>-old` must not |
| F10 | `checkup/SKILL.md` lists sections and links each to `references/`; `skill-trials.py` is run from `references/seats.md:24`, `config-scan.py` from `references/config.md:7` | B8: checkup runs the script from `references/seats.md`, not `SKILL.md` (decision 1) |
| F11 | Reuse: env homes `CLAUDE_CONFIG_DIR`/`CODEX_HOME` at `config-scan.py:19-20`; common-dir lookup at `run-worktree.py:45`; subprocess test with temp `HOME` at `test_config_scan.py:14-38`. No JSONL transcript reader exists (`trigger-test.py` only writes JSONL) | T1 copies these three patterns; no shared module, since scripts have hyphenated names and one caller each |

## Tickets

### T1 — Claude interrupts become a repeat report
Delivers: B1, B3, B5, B6, B7 · Blocked by: none · Lane: logic
Budget: code +140 · tests +180 · why: each fixture copies the real near-miss records (F1, F6) and every filter gets both sides
Seam: `python3 .github/skills/checkup/scripts/corrections.py [--days N] [--all-repos]` run as a subprocess with a temp `HOME` and repo
Accept:
- [x] Interrupt after a `Bash` tool_use → `interrupt · Bash`; after text only → `interrupt · no tool`; a `tool_result` quoting the phrase and an `isSidechain` record each → no key (B1)
- [x] First human turn after an interrupt → `- claude · interrupt · Bash: <text>`; 250 characters print as 200; later, `isMeta` and `<command-name>` turns each → no line (B3)
- [x] A key in 2 files → `- interrupt · Bash · 2 sessions · 3 times` under `repeats:`; a key twice in 1 file → absent there, counted in `once: 1 key(s)` (B7)
- [x] Defaults skip a 15-day file, a sibling `<repo>-old` cwd and another repo, and keep a 13-day `.worktrees/x` file; `--days 30` keeps a 20-day file; `--all-repos` keeps the other repo (B6)
- [x] No `~/.claude/projects` → exit 0, first line `stores: claude missing · codex missing · copilot missing` (B5)
- [x] In this repo on the real stores, `--days 30` → exit 0, a line starting `- interrupt · no tool · 2 sessions` (seen 2026-11-01, F7) (B7)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_corrections.py -k ClaudeTests && python3 .github/skills/checkup/scripts/corrections.py --days 30 | grep -q '^- interrupt · no tool · 2 sessions'` (pre: new file)
Skills: none
Status: done @ 00623b1
Writer: GPT-6.1 Sol

### T2 — Denials and the other two stores
Delivers: B2, B3, B4 · Blocked by: T1 · Lane: logic
Budget: code +65 · tests +90 · why: Codex and Copilot fixtures copy their real duplicate and unattended records (F4, F5, F8)
Seam: the same command, on Claude, Codex and Copilot fixtures; test classes end in `StoreTests` and never contain `ClaudeTests`
Accept:
- [ ] Claude denial of Bash `cd /r && git push` → `denial · Bash · git`; of Edit → `denial · Edit`; a `tool_result` quoting the phrase mid-text → no key (B2)
- [ ] A denial whose result holds `the user said:\nuse a branch` → redirect `- claude · denial · Bash · git: use a branch` (B3)
- [ ] Codex `turn_aborted` `interrupted` after `custom_tool_call` `exec` → one `interrupt · exec` despite the `<turn_aborted>` message; the next `UserMessage` is the redirect (B4)
- [ ] A Codex file whose `session_meta` source holds `subagent` → no key; the stores line counts it as read (B4)
- [ ] Copilot denial `unattended_fallback` → no key; same denial from another `decisionSource` → `denial · shell · ls` (B4)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_corrections.py -k StoreTests` (pre: new file)
Skills: none
Status: todo

### T3 — checkup and retro run the script
Delivers: B8 · Blocked by: T1 · Lane: mechanical
Budget: code +6 · tests +0
Seam: `grep` on `checkup/references/seats.md` and `retro/SKILL.md`
Accept:
- [ ] `seats.md` has a **Corrections** bullet that runs `scripts/corrections.py`, reports the first 5 `repeats:` lines, and copies no redirect line into a file (B8)
- [ ] `retro/SKILL.md` *Recurring* runs `corrections.py`, counts a matching repeat as "seen twice", and cites its key, never its redirect text (B8)
Verify: `grep -q 'corrections.py' .github/skills/checkup/references/seats.md && grep -q 'corrections.py' .github/skills/retro/SKILL.md && grep -q 'first 5' .github/skills/checkup/references/seats.md && grep -q 'no redirect line' .github/skills/checkup/references/seats.md && grep -q 'seen twice' .github/skills/retro/SKILL.md && grep -q 'never its redirect text' .github/skills/retro/SKILL.md` (pre: exit 1)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

## Coverage
- Outcome → T1 (real-store report in this repo), T3 (checkup and retro name the script)
- B1 → T1 · B2 → T2 · B3 → T1, T2 · B4 → T2 · B5 → T1 · B6 → T1 · B7 → T1 · B8 → T3
- Out of scope: phrase list or model detection → untouched · report file or committed transcript text → untouched · other ROADMAP gaps → untouched

## Risks
T1 carries the report format all later tickets and checkup read; its literals above are the contract.
The real-store line in T1 depends on transcript age: it holds until 2026-11-24, then needs a fresh observation.
Receipts quote only the stores and repeat lines, never redirect lines: transcripts are private and this repo is public.

## TODO impacts
none (the brief seeds from ROADMAP.md row 3, not TODO.md)

## Product doc impacts
- ROADMAP.md: row 3 `correction-mining` goes from `next` to done at wrap; nothing it states becomes untrue
- No PRODUCT.md or DESIGN.md

## Deviations
- Budget waived: T2 — code net +71 against +65; cwd extraction and request joins keep all three readers explicit.
