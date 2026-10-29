Command: workflow plan next-step
Created: 2026-10-29 · Opus 5.5
Base:    19533a5
Inputs:  .workflow/next-step/brainstorm.md @ 62e8c26
Status:  complete
Docs read: none in scope (the repo has no PRODUCT.md or DESIGN.md)
Size: code 812 · tests 503 · ratio 0.62 · largest touched check-run.py 812 · over 1,000: none (new: next-step.py, test_next_step.py; skill `*.md` count as neither)
Decisions: round 1 "all defaults": 1a fix:mechanical and fix:operator rows · 2a `Fixes: C<n>-<m> (P#)` on every patch ticket · 3a `--key` for checkup · round 2: 1a approve
## Execution state
Current: T1–T5 and C1-T1–C1-T3 done. Session 4 complete; next C1-T4.
T1 @ 904f083 · writer: GPT-6.1 Sol · baseline 82 passed, final 86 passed · receipts/t1-verification.md
T2 @ 70fefa2 · writer: GPT-6.1 Sol · final workflow 89, checkup 8 passed · receipts/t2-verification.md
T3 @ 17c8020 · writer: GPT-6.1 Sol · final workflow 92, checkup 8 passed · receipts/t3-verification.md
T4 @ 53d959c · writer: GPT-6.1 Sol · final workflow 98, checkup 8 passed · receipts/t4-verification.md
T5 @ a354025 · writer: GPT-6.1 Sol · final workflow 99, checkup 8 passed · receipts/t5-verification.md
Revalidated @ 588bf2d · none: it swaps an example at checkup report.md:15; T5 edits report.md:70-80, pre counts hold
Sessions: 1 → T1 · 2 → T2, T3, T4
Session 3: T5
Session 4: C1-T1, C1-T2, C1-T3
Contract: schema_version 1; model {vendor,name,effort}; keyed routing tables. No pending decision or uncommitted files after this record commits.
## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The skill lives in `.github/skills/workflow/`; `skills/workflow` is a symlink to it | Tickets name `.github/skills/workflow/…`; the brief's path works through the link |
| F2 | `run-worktree.py:10-11` already loads `check-run.py` with `importlib` | next-step.py copies those two lines (D1); reuse hit |
| F3 | check-run.py has `Doc` (:100), `parse_tickets` (:255), `field` (:273), `SHA`/`DASH`/`RECEIPTS` (:64-72), `git_out` (:673). It has no review parser: `check_review` parses findings inline (:540-583) | next-step reuses them; T4 extracts `review_findings(doc)` and `check_review` calls it, the 82 existing tests prove no change |
| F4 | No "code changed since X" helper; `growth()` (:413) nets lines, so a net-zero edit reads as unchanged | next-step filters `git diff --name-only <Base>..HEAD` by `RECEIPTS` (the receipt-rule diff) |
| F5 | Fix tickets give severity two ways: `Fixes: C1-1 (P1)` (lean-skill-hubs, memory-patterns-and-budget, run-worktrees) and `Delivers: C1-1, B5` (retire-date-gates, run-ratio-and-retire). Finding ids are positions in `review.md`, and settled sections fold into `## Resolved` | 2a: every patch ticket carries `Fixes: C<n>-<m> (P#)`; check-run errors without it (T3) |
| F6 | ROUTING has fix rows for P0, logic and contract only; real fix tickets also use mechanical (lean-skill-hubs C1-T2, run-worktrees C6-T1) and operator (a private work repo's runs) | 1a: ROUTING gains `fix:mechanical` and `fix:operator`, copying their execute rows (T1) |
| F7 | Nothing records a handoff's path in its ticket (D7's premise). Names vary in a private work repo's runs: `t<N>-operator-handoff.md`, `t<N>-attempt2-operator-handoff.md`, `c1-t<N>-handoff.md`, `t<N>-<topic>-handoff.md` | The blocker lists every `receipts/<id>-*handoff*.md` in name order; no new field |
| F8 | An awaiting-human ticket's receipt path is in its Verify, `receipt: receipts/<file>` (check-run :327); a present receipt resumes the ticket (phase-3-execute :61-62) | next-step routes that ticket to execute |
| F9 | ROUTING cells hold prose: plan effort "high; xhigh hardest cases", contract context "standard; large if …", operator seat "… (Heavy executor if …)", approvals as sentences | D2 format: effort ∈ medium·high·xhigh, context ∈ standard·large, approval ∈ auto·human, one seat per row; the prose moves to a Notes column |
| F10 | No ticket field marks a UI ticket | The UI row becomes a note; `approval` reports the lane's row, and execute still stops before a UI commit by its own rule |
| F11 | Fallback effort disagrees: ROUTING's reviewer chain says `Sonnet 5.5 · xhigh`; checkup report.md:72 says use the phase row's effort | A chain item is `Vendor · Model` (phase effort) or `Vendor · Model · effort`; with 3a checkup's sentence goes |
| F12 | Seat-table efforts repeat the phase table ("high (review: xhigh)", "xhigh (P0 fixes: high)") | The seat table keeps vendor, model, trial and chain; effort lives only in the phase table |
| F13 | checkup report.md:70-80 maps commands to phase rows and copies Model and Fallback by hand: TODO C1-1, wrong four times | 3a: `next-step.py --key <key>` prints the two lines and checkup copies them (T5) |
| F14 | The card's command "carries the CLI's own skill prefix" (SKILL.md:19-20) | `--prefix` adds it to the card's command; JSON `command` stays bare (D6) |
| F15 | ROUTING Modes: wrap follows review in the same session | Wrap's card has `reset: false`; every other card `true` |
| F16 | SKILL.md's states also include drafting artifacts (resume that phase), parked runs (listed by `status`) and done runs | T4 covers them |
| F18 | `test_check_run.py`'s harness (:66-101) is check-run specific, and tests.md forbids a test importing a test | test_next_step.py has its own small temp-repo harness and an inline fixture routing table, so a ROUTING edit never breaks B1-B6 tests; one test parses the real file |
| F19 | Escalations (review cycle bound, wrap contradictions) wait for a chat answer, so they already end on the Decisions list with no card (SKILL.md:120-121) | Only the cycle-bound state shows in files: open fix-now findings and no current-cycle patch plan → a blocker (T4) |
## Tickets
### T1 — ROUTING.md parses, and a brief-only run gets its plan card
Delivers: B1, B7, B8 · Blocked by: none · Lane: contract
Budget: code +150 · tests +90
Seam: `next-step.py <slug> [--json] [--repo DIR] [--routing FILE] [--prefix STR]`: stdout, stderr, exit code, on fixture runs in a temp git repo
Change: ROUTING seat table `Seat · Vendor · Model · Trial · Fallback chain · Notes`; phase table `Key · Phase / work · Seat · Effort · Context · Approval · Notes` (F9, F11, F12, 1a). Load check-run per F2. JSON: `schema_version slug phase command ticket why key seat model{vendor,name,effort} trial context fallback[] approval reset reads[] blocker card`. Plain stdout is the card in SKILL.md's template.
Accept:
- [x] brief-only run, `--json` → phase `plan`, command `workflow plan x`, seat `Strict reviewer`, model Anthropic · Opus 5.5 · high, context `large`, reset true, blocker null, fallback Sonnet 5.5 · xhigh then GPT-6 Sol · xhigh (B1)
- [x] same run, no `--json` → stdout equals `card`; it holds `- **Model:** Opus 5.5 · high · large`, `- **Fallback:** Sonnet 5.5 · xhigh`, fenced `workflow plan x`; `--prefix /` fences `/workflow plan x` (B7)
- [x] fixture Trial `OpenAI · GPT-6.1 Sol` on Strict reviewer → model GPT-6.1 Sol, `trial` true, Model line ends `(trial)`, fallback[0] Anthropic · Opus 5.5, `schema_version` 1 (B7)
- [x] three bad routings (a row missing a cell; effort `max`; no `plan` row) → each exits 1, stderr names the row's key (`plan` for the missing row), stdout empty (B8)
- [x] the real ROUTING.md → both tables parse, all 13 routable keys resolve, `wc -c` ≤ 5,500 (B8)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py && wc -c ROUTING.md` (pre: new file, NO TESTS RAN exit 5 · 5407)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ 904f083
Writer: GPT-6.1 Sol
### T2 — Plan tickets route by lane, and an awaiting-human ticket names its handoff
Delivers: B2, B3 · Blocked by: T1 · Lane: logic
Budget: code +60 · tests +60
Seam: the T1 CLI on fixture `plan.md` tickets and `receipts/` files; first ready ticket by execute's rule picks `execute:<lane>`; receipts per F8, handoffs per F7 in `reads`
Accept:
- [x] T1 done, T2 `todo` with `Lane: contract` blocked by T1 → phase `execute`, ticket `T2`, seat `Heavy executor`, model OpenAI · GPT-6.1 Sol · xhigh, approval `auto` (B2)
- [x] only T3 unfinished, `awaiting-human`, `receipts/t3-operator-handoff.md` committed → blocker ticket `T3` naming that path, model null, command `workflow execute x`, card `- **Model:** human · …` (B3)
- [x] same run with T3's Verify receipt `receipts/t3.txt` present → phase `execute`, ticket `T3`, blocker null (B3)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py` (pre: new file, NO TESTS RAN exit 5)
Skills: none
Status: done @ 70fefa2
Writer: GPT-6.1 Sol
### T3 — Fix tickets route by severity and lane
Delivers: B5, B8 · Blocked by: T2 · Lane: logic
Budget: code +40 · tests +40
Seam: the T1 CLI on a fixture `patch_plan.md`; `check-run.py` on the same run
Change: `patch_plan.md` with a ticket not done is the live file; key `fix:P0` for P0, else `fix:<lane>`; Why `Patch cycle <n> · fix <ids>`. check-run: a patch ticket without `Fixes:` errors when the file is complete, warns while drafting.
Accept:
- [x] C1-T1 `todo`, `Fixes: C1-1 (P0)`, `Lane: logic` → ticket `C1-T1`, seat `Heavy executor`, model GPT-6.1 Sol · high, why `Patch cycle 1 · fix C1-1` (B5)
- [x] `Fixes: C1-1 (P1)` → `Default executor` · medium; `(P3)` with `Lane: mechanical` → `Mechanical lane` · medium (B5)
- [x] complete patch ticket with no `Fixes:` → check-run ERROR naming `C1-T1` and `Fixes: C<n>-<m> (P#)`; next-step exits 1 naming `C1-T1` (B5, B8)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests` (pre: 82 OK)
Skills: none
Status: done @ 17c8020
Writer: GPT-6.1 Sol
### T4 — Review, wrap, parked and done follow the run's files
Delivers: B4, B6, B7 · Blocked by: T3 · Lane: logic
Budget: code +70 · tests +70
Seam: the T1 CLI; `review_findings(doc)` extracted from `check_review` (F3)
Change: receipt-rule diff since review Base (F4); open `fix now` findings; a current-cycle patch plan all done → re-review, none → blocker (F19); drafting resumes its phase, parked and done per F16; wrap `reset: false` (F15).
Accept:
- [x] every plan ticket done, no `review.md` → phase `review`, seat `Strict reviewer`, model Anthropic · Opus 5.5 · xhigh, context `large` (B4)
- [x] complete `review.md`, no open finding, no later commit → phase `wrap`, seat `Brainstorm partner`, model Anthropic · Sonnet 5.5 · medium, reset false (B6)
- [x] that run plus a later commit to `tool.py` → phase `review`; plus a commit to `notes.md` only → phase `wrap` (B4, B6)
- [x] cycle 1 open `fix now` P1, every C1 patch ticket done → phase `review`; with no `patch_plan.md` → blocker naming `C1-1`, command `workflow review x` (B4)
- [x] brief `drafting` → phase `brainstorm`; brief `parked`, nothing else → phase `parked`, command `workflow plan x`; brief `done` → phase `done`, command null (B7)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests` (pre: 82 OK)
Skills: none
Status: done @ 53d959c
Writer: GPT-6.1 Sol
### T5 — Phases print the script's card, and checkup prints its model lines from it
Delivers: B7, B8 · Blocked by: T4 · Lane: logic
Budget: code +20 · tests +15
Seam: `next-step.py --key <key>` stdout; text of SKILL.md, worktrees.md, phase-4-review.md, MAINTAINING.md, checkup report.md
Change: SKILL.md's card section says run the script after the push and print its output unchanged; worktrees.md builds the status line from `phase`, `blocker`, `command`; phase-4-review's patch ticket shape gains `Fixes:`; checkup copies `--key` output (F13); MAINTAINING lists the script.
Accept:
- [x] `--key review` → stdout `- **Model:** Opus 5.5 · xhigh · large` and `- **Fallback:** Sonnet 5.5 · xhigh`; `--key nope` → exit 1 naming `nope` (B7, B8)
- [x] SKILL.md's card section names `scripts/next-step.py`, holds no `**▶ Next:` template, and `wc -c` < 11,191 (B7)
- [x] `next-step.py` named in worktrees.md and checkup report.md; `Use the phase row's effort` 0 in report.md; `Fixes: C` ≥ 1 in phase-4-review.md (B7)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py; grep -c 'next-step.py' SKILL.md references/worktrees.md ../checkup/references/report.md; grep -c "Use the phase row's effort" ../checkup/references/report.md; grep -c 'Fixes: C' references/phase-4-review.md; wc -c SKILL.md` (pre: NO TESTS RAN · 0 · 0 · 0 · 1 · 0 · 11191)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ a354025
Writer: GPT-6.1 Sol
## Coverage
- Outcome → T1 (`--json` prints the object), T5 (card, `workflow next` and `workflow status` print it)
- B1 → T1 · B2 → T2 · B3 → T2 · B4 → T4 · B5 → T3 · B6 → T4 · B7 → T1, T4, T5 · B8 → T1, T3, T5
- Out of scope: unattended mode, `decisions.md` → untouched · conductor skill → untouched · decision model → untouched · harness model IDs → untouched · PRs → none · version bump (`.claude-plugin` 2.3.0) → untouched
## Risks
- Outside its files: checkup, design (rows named *Design*), evals and agent-docs read ROUTING.md by eye; the name column stays. Installed copies lag until `npx skills update -g` after the push.
## TODO impacts
- checkup-next-actions C1-1 → completed by T5 (3a) · Worktree setup as a script → untouched
## Product doc impacts
- No PRODUCT.md or DESIGN.md. The workflow skill's ROADMAP.md: no changes (no line names the card or routing).
