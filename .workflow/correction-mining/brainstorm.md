Command: workflow brainstorm correction-mining
Created: 2026-11-01 · Sonnet 5.5
Base:    7b58235
Inputs:  none
Status:  complete
Mode: attended

## Problem
A correction the human gives an agent becomes a rule only if the agent logs it or the human runs `retro` on that session. Most corrections are never mined.

## Outcome
`python3 corrections.py` prints a plain-text report to the terminal: top repeated denials and interrupts, and redirect turns verbatim. `checkup` shows the top 5 keys seen in at least 2 sessions; `retro` cites a match in its *Recurring* test.

## Behaviours
- B1 — a Claude transcript with an interrupt turn → one interrupt, keyed by the tool that ran just before it
- B2 — a Claude `tool_result` saying the user doesn't want to proceed → one denial, keyed by tool and command head
- B3 — the first user text turn after an interrupt or denial → listed as a redirect, cut to 200 characters; other user turns are not listed
- B4 — a Codex `turn_aborted` with reason `interrupted` → an interrupt; a Copilot denial with `decisionSource` `unattended_fallback` → not counted, any other denial → counted
- B5 — a missing store → skipped without error; the report names the stores it read
- B6 — no flags → only files from the last 14 days whose cwd matches the current repo; `--days 30` widens the window, `--all-repos` drops the cwd filter
- B7 — a key seen in at least 2 sessions → shown as a repeat with its session count; a key seen in one session → not
- B8 — the checkup and retro skill files name the script → `checkup/SKILL.md` runs it and reports the top 5 repeats; `retro/SKILL.md` runs it for the repo and cites a repeat as "seen twice"

## Decisions
- D1 — a redirect is mechanical only: an interrupt, a human denial, and the first user turn after either; no phrase list, no model — the results stay testable (product call)
- D2 — read all three stores, skip any that is missing: Claude `~/.claude/projects/*/*.jsonl`, Codex `~/.codex/sessions/*/*/*/rollout-*.jsonl`, Copilot `~/.copilot/session-state/*/events.jsonl` (code: retro/SKILL.md)
- D3 — the script counts only mechanical keys (denials by tool and command head, interrupts by the tool running just before) and lists redirect text verbatim, truncated; the reading agent clusters it (product call)
- D4 — `checkup` and `retro` run the script and read stdout; no report file, because transcripts hold private text and this repo is public (product call)
- D5 — defaults: 14 days, current repo only (cwd match); `--days N` and `--all-repos` override (product call)
- D6 — the script lives at `checkup/scripts/corrections.py` with tests beside `config-scan.py`; `retro` points to the checkup skill's folder (code: .github/skills/checkup/scripts)

## Test seams
- `corrections.py` as a command on fixture transcripts in a temp directory — observes B1 to B7 (new)
- `grep` on `checkup/SKILL.md` and `retro/SKILL.md` for the script call — observes B8 (new)

## Trust boundaries
- Transcripts in `~/.claude`, `~/.codex`, `~/.copilot` → stdout only; the script writes no file and makes no network call

## Out of scope
- phrase list or model-based redirect detection — not testable, breaks the deterministic design (D1)
- a report file or committed transcript text — transcripts are private, this repo is public (D4)
- the other ROADMAP gaps (ground rules enforced by code, reverting no-signal trials) — separate runs

Docs read: none in scope (no PRODUCT.md or DESIGN.md); ROADMAP.md step 3; retro/SKILL.md transcript stores
