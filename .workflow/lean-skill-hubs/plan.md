Command: workflow plan lean-skill-hubs
Created: 2026-10-28 · claude-opus-5-5
Base:    2bc4427
Inputs:  .workflow/lean-skill-hubs/brainstorm.md @ ed2c63b
Status:  complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md in this repo)
Size: code 2822 · tests 0 · ratio 0 · largest touched build-video.py 776, memory.remember/SKILL.md 306 lines · over 1,000: none
Decisions: 1a · 2a · 3a · 4a · 5a · 6a (approved 2026-10-28)
Split declined by human: 2026-10-28 (135 lines; D8 keeps one ticket per skill)

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The brief's KB is 1,000 bytes: 13,238 bytes is its "13.2 KB" | Byte targets in tickets are `wc -c` values: 11,500, 8,000, 12,000, 3,500 |
| F2 | agent-docs/SKILL.md:149 keeps text other skills rely on in `SKILL.md`, never a sibling file; checkup:128, retro:100 and learning-worklog.md:64 point at memory.remember's *Repeats escalate to enforcement* | D4's `references/enforcement.md` breaks that rule; the section stays (decision 1) |
| F3 | memory.remember by section: promote bullets 3,144 · steps 3+7 1,486 · Rules repeats 2,018 · Layers 2,718 · enforcement 2,107 bytes | D4 alone ends near 16.9 KB, 19 KB with F2; 12 KB is out of reach without moving every-run text (decision 2) |
| F4 | D4's merged routing table rewrites words, while Out of scope says a move keeps the words | Layers stays word for word; step 2's lines that repeat it are cut as duplicates (decision 3) |
| F5 | memory.compact steps 6–7 (3,982 bytes) run on every pass: the output is always a proposal | Moving them saves no bytes per run; without the move compact ends near 14 KB (decision 4) |
| F6 | Reuse: check-explainer.py:177 already splits prose into sentences; no ledger helper exists. `growth()` in check-run.py counts `.md` as zero | The ledger copies that regex with a pointer comment; doc-ticket Budgets are added lines, for review only |
| F7 | `video.md` is named at understand/SKILL.md:166,174 and build-video.py:78,158; checkup/SKILL.md:103 says "`understand`'s `video.md`", still true after the move | T6 updates the first four; checkup:103 stays as written |
| F8 | understand's only tests are live CLI trigger runs that read the description, which D7 leaves alone; `diff -rq` to `~/.agents/skills` shows `__pycache__` noise at Base | B6 for understand is "frontmatter byte-identical to Base"; B7 uses `diff -rq -x __pycache__` |
| F9 | agent-docs/SKILL.md:154: every skill change gets a row in `workflow/SKILL-IMPACT.md` (Mode: autonomous) | T7 adds one row naming the six skills |
| F10 | Baseline: workflow unittest 81 OK, checkup 8 OK, `check-run.py --all` 0 ERRORs. B5's "778 characters" read as exact would force padding | B6's literal values; T5 asserts at most 778 |

## Tickets

### T1 — The sentence ledger accounts for every removed sentence
Delivers: B2, B3 · Blocked by: none · Lane: logic
Budget: code +90 · tests +70
Seam: `python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py <skill-dir> <base>`, reading duplicates from `notes/dups-<skill>.txt` (tab-separated: removed sentence · kept path · kept phrase); tests drive it on a temp git repo
Accept:
- [ ] fixture SKILL.md loses three sentences: one re-wrapped into references/a.md, one listed in dups with its phrase present, one dropped → prints `moved 1 · duplicate 1 · unaccounted 1`, exit 1, names the dropped one (B2)
- [ ] fixture adds references/b.md unlinked from SKILL.md and a 101-line references/c.md with no contents list → exit 1, one line naming each file (B3)
Verify: `cd .workflow/lean-skill-hubs/scripts && python3 -m unittest test_sentence_ledger` (pre: new file)
Skills: none
Status: todo

### T2 — memory.remember keeps the shared rules and moves the branches
Delivers: B1, B2, B3, B4 · Blocked by: T1 · Lane: logic
Budget: code +140 · tests +0
Seam: `wc -c` and the ledger on `.github/skills/memory.remember`. New: `references/promote-to-skill.md` (step 2 skill bullets, step 1 plugin-name listing), `references/workflow-runs.md` (steps 3, 7), `references/limits.md` (*The AGENTS.md cost test*, *Keeping memory bounded*, headings kept). Rules lines that repeat earlier sections are cut as duplicates
Accept:
- [ ] `wc -c` SKILL.md → at most 15,500, and `grep -c '^## Repeats escalate to enforcement$'` → 1 (B1, B4)
- [ ] ledger vs ed2c63b → `unaccounted 0`, exit 0, three new reference files each linked from SKILL.md (B2, B3)
Verify: `wc -c .github/skills/memory.remember/SKILL.md && grep -c '^## Repeats escalate to enforcement$' .github/skills/memory.remember/SKILL.md && python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/memory.remember ed2c63b` (pre: 27506 · 1 · new file)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T3 — memory.compact points at memory.remember for layers and page shape
Delivers: B1, B2 · Blocked by: T2 · Lane: logic
Budget: code +10 · tests +0
Seam: `wc -c` and the ledger on `.github/skills/memory.compact`; its Rules lines that repeat steps 1–6 are cut as duplicates
Accept:
- [ ] `wc -c` SKILL.md → at most 14,500, and `## Memory Layers` names `memory.remember` and is under 6 lines (B1)
- [ ] ledger vs ed2c63b → `unaccounted 0`, exit 0 (B2)
Verify: `wc -c .github/skills/memory.compact/SKILL.md && python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/memory.compact ed2c63b` (pre: 17119 · new file)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T4 — The workflow hub fits its own budget with every rule kept
Delivers: B1, B2, B3, B6 · Blocked by: T1 · Lane: logic
Budget: code +30 · tests +0
Seam: `wc -c`, the ledger and the existing suite on `.github/skills/workflow`, moves per D2
Accept:
- [ ] `wc -c` SKILL.md → at most 11,500, and `references/secret-scan.md` is linked from SKILL.md (B1, B3)
- [ ] ledger vs ed2c63b → `unaccounted 0`, exit 0, and `python3 -m unittest discover -s scripts/tests` → `Ran 81 tests` OK (B2, B6)
Verify: `wc -c .github/skills/workflow/SKILL.md && python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/workflow ed2c63b && (cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests)` (pre: 13238 · new file)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T5 — checkup loads only the section a scope word asks for
Delivers: B1, B2, B3, B5 · Blocked by: T1 · Lane: logic
Budget: code +260 · tests +0
Seam: `wc -c`, the ledger and `yaml.safe_load` of the frontmatter on `.github/skills/checkup`; one `references/<scope>.md` per section, named for its scope word
Accept:
- [ ] `wc -c` SKILL.md → at most 8,000; six files `references/{skills,memory,docs,workspace,config,seats}.md`, each linked from SKILL.md (B1, B3)
- [ ] ledger vs ed2c63b → `unaccounted 0`, exit 0 (B2)
- [ ] parsed `description` → at most 778 characters, containing all seven quoted trigger phrases of Base (B5)
Verify: `wc -c .github/skills/checkup/SKILL.md && python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/checkup ed2c63b && (cd .github/skills/checkup && python3 -m unittest discover -s scripts/tests)` (pre: 23975 · new file)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T6 — understand moves pictures and video detail to references
Delivers: B1, B2, B3, B4 · Blocked by: T1 · Lane: logic
Budget: code +60 · tests +0
Seam: `wc -c`, the ledger and `grep` on `.github/skills/understand`; `git mv video.md references/video.md`
Accept:
- [ ] `wc -c` SKILL.md → at most 12,000; `references/pictures.md` and `references/video.md` linked from it; frontmatter byte-identical to Base (B1, B3)
- [ ] `grep -rn '<skill>/video.md\|in video.md' .github/skills` → 0 hits; build-video.py:158 names `references/video.md` (B4)
- [ ] ledger vs ed2c63b → `unaccounted 0`, exit 0 (B2)
Verify: `wc -c .github/skills/understand/SKILL.md && python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/understand ed2c63b && grep -rn '<skill>/video.md\|in video.md' .github/skills` (pre: 15230 · new file · 3 hits)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T7 — verify splits by command, and the change is logged
Delivers: B1, B2, B3 · Blocked by: T2, T3, T4, T5, T6 · Lane: logic
Budget: code +215 · tests +0
Seam: `wc -c` and the ledger on `.github/skills/verify`; `workflow/SKILL-IMPACT.md`
Accept:
- [ ] `wc -c` SKILL.md → at most 3,500; `references/create.md` and `references/maintain.md` linked from it; ledger `unaccounted 0`, exit 0 (B1, B2, B3)
- [ ] `SKILL-IMPACT.md` → 5 rows dated 2026-10-28 (4 at Base); the new one names all six skills, outcome `trialing` (F9)
Verify: `wc -c .github/skills/verify/SKILL.md && python3 .workflow/lean-skill-hubs/scripts/sentence-ledger.py .github/skills/verify ed2c63b && grep -c '^| 2026-10-28 ' .github/skills/workflow/SKILL-IMPACT.md` (pre: 14934 · new file · 4)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T8 — The installed copies match the repo
Delivers: B1, B6, B7 · Blocked by: T7 · Lane: operator
Budget: code +0 · tests +0
Risk: cheap · Runner: agent after approval (standing: memory page j-skills-install-layout, "run `npx skills update -g` after every push")
Seam: receipts/t8-install.txt. Handoff: with main pushed, run `npx skills update -g` in the background; then write to `receipts/t8-install.txt` the output of `diff -rq -x __pycache__ .github/skills/$s ~/.agents/skills/$s` for the six skills and agent-docs, both unittest suites, `check-run.py --all | grep -c ERROR`, and `git diff --quiet ed2c63b -- .github/skills/agent-docs; echo $?`
Accept:
- [ ] receipt → no `diff` output for any of the seven skills (B7)
- [ ] receipt → workflow `Ran 81 tests` OK · checkup `Ran 8 tests` OK · ERROR count 0 · agent-docs exit 0 (B6, B1)
Verify: receipt: receipts/t8-install.txt — diff lines 0 · 81 OK · 8 OK · ERROR 0 · agent-docs 0 (pre: no receipt)
Skills: none
Status: todo

## Coverage
- Outcome → T2–T7 (`wc -c` per SKILL.md) and T8 (installed copies)
- B1 → T2–T8 · B2 → T1–T7 · B3 → T1, T2, T4–T7 · B4 → T2, T6 · B5 → T5 · B6 → T4, T8 · B7 → T8
- Out of scope: design, evals, plain, retro → untouched · moved text rewritten → untouched · agent-docs → untouched (T8 proves it) · TODO checkup-next-actions C1-1 → untouched · Copilot sibling-file probe → untouched

## Risks
- T2 is riskiest: deciding which memory.remember lines repeat others is judgement, and a wrong cut drops a rule; the ledger's dups rows are what review checks.
- An isolated worktree run lands only at wrap, so T8 then waits for wrap's land step before `npx skills update -g` can see the change.
- Not taken: one reference per memory.remember section, which would put every-run text out of `SKILL.md`.

## TODO impacts
`checkup-next-actions C1-1` → untouched (out of scope). No other item named.

## Product doc impacts
No PRODUCT.md, DESIGN.md or root ROADMAP.md; `workflow/ROADMAP.md` → no changes.
