Command: workflow improve .github/skills - goal: simpler, same behaviour
Created: 2026-10-28 · claude-opus-5-5
Base:    ed2c63b
Inputs:  none
Status:  done

## Problem
Seven skill files are over the ~10 KB budget, so every load pays for text most runs never use.
workflow's hub is read by every phase, so its size costs the most; it is 13.2 KB and 218 lines
against its own ~10 KB / ~180-line budget in `MAINTAINING.md`.

## Outcome
Each target `SKILL.md` keeps only what every run of that skill needs; branch-only text sits in
the skill's `references/`, linked from `SKILL.md`. An agent following any command gets the same
instructions as before, from fewer bytes. Surface: `wc -c` of each `SKILL.md` and the installed
copies under `~/.agents/skills/`.

## Behaviours
- B1 — `wc -c` per `SKILL.md` → workflow ≤ 11.5 KB, memory.remember ≤ 12, checkup ≤ 8,
  memory.compact ≤ 10.5, verify ≤ 3.5, understand ≤ 12; agent-docs byte-identical to Base.
- B2 — the sentence ledger run over Base..HEAD → every sentence removed from a target `SKILL.md`
  is found word for word in that skill's `references/`, or listed as a duplicate with the line
  that keeps it; 0 unaccounted.
- B3 — every new reference file → linked directly from its own `SKILL.md`; one over ~100 lines
  opens with a contents list.
- B4 — grep of `.github/skills/` for each moved section name or path → every hit names a file
  and heading that exist (`Repeats escalate to enforcement`, `video.md`, checkup's six sections).
- B5 — checkup's `description`, parsed as YAML → 778 characters, holding all seven quoted
  trigger phrases of Base.
- B6 — existing test suites and `check-run.py --all` → same pass and ERROR counts as Base
  (`python3 -m unittest discover -s scripts/tests` in workflow and checkup; understand's tests).
- B7 — after landing and `npx skills update -g` → `diff -rq` of each changed skill against
  `~/.agents/skills/<name>` shows no difference. (live)

## Decisions
- D1 — agent-docs stays whole — it is shared reference other skills load; its own convention
  keeps shared text in `SKILL.md` after a measured Copilot sibling-file limit (code: agent-docs/SKILL.md:149)
- D2 — workflow hub to ≈11.2 KB with every rule kept: `references/secret-scan.md` (finding and
  no-scanner branch), slug/status lookup merged into `references/worktrees.md`, "commit after each
  verified ticket" into `phase-3-execute.md`, seat invariants and card lines that repeat
  `ROUTING.md` trimmed; the run-layout list stays — product call
- D3 — verify splits by command: `references/create.md`, `references/maintain.md` — product call
- D4 — memory.remember: `references/enforcement.md`, `references/promote-to-skill.md`,
  `references/workflow-runs.md`; Memory Layers and step 2 merged into one routing table; Rules
  lines that repeat earlier sections dropped — product call
- D5 — checkup: one reference per check section (skills, memory, docs, workspace, config,
  seats); description 883 → 778 characters, trigger phrases kept — product call
- D6 — memory.compact: steps 6–7 to `references/proposal.md`; its copy of layers and page shape
  becomes a pointer to memory.remember's `SKILL.md` — product call
- D7 — understand: `references/pictures.md` (pictures question + step 3); `video.md` moves to
  `references/video.md` with the video question's option details — product call
- D8 — one run, one ticket per skill, so each change reverts alone — product call

## Test seams
- `scripts/sentence-ledger.py <skill> <Base>` in this run folder — observes B2, B3 (new)
- `wc -c`, `grep -rn`, YAML parse of frontmatter — observe B1, B4, B5 (existing)
- the existing unittest suites and `check-run.py --all` — observe B6 (existing)
- `diff -rq` against `~/.agents/skills/` after `npx skills update -g` — observes B7 (existing)

## Out of scope
- design, evals, plain, retro — under or near budget (retro 10.5 KB)
- rewriting any moved text — a move keeps the words; only exact duplicates are cut
- agent-docs split or rewrite — D1
- TODO `checkup-next-actions C1-1` (card-line script) — unrelated guardrail, run-sized on its own
- a new Copilot probe of sibling-file reads — blocked by the session's permission check; no
  ROUTING seat runs on Copilot

Docs read: none in scope (no PRODUCT.md or DESIGN.md in this repo)
