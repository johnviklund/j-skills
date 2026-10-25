Command: workflow execute checkup-next-actions
Created: 2026-10-25
Base: 20682e7
Inputs: plan.md @ 37f7b44
Status: complete

Exact report emitted by the approved paid retry. A later final summary omitted the cards; see t2-verification-2.md.

## Workspace checkup: cx-intelligence (2026-10-25)

Nothing is broken. Most findings are small, and three have a cost if left.

**Skills**
- ✅ All 9 repo skills have a folder name that matches the frontmatter name. No other install shadows them. Every description is under 900 characters.
- ⚠️ `.claude/skills/` does not exist, so Claude Code cannot see `verify-cx-intelligence` or the `cx-*` skills. Question 1 asks whether that matters.
- ⚠️ None of the repo skills are linked into `~/.codex/skills/`. Codex does not see them. AGENTS.md calls Codex secondary.

**Memory**
- ✅ 37 pages, and all of them are indexed. Every page has the standard footer. None is stale, since the oldest `Last confirmed` is 2026-09-09. `MEMORY.md` is 11 KB.
- ⚠️ Two pages say `Enforced by: pending` but their TODO lines now sit in `TODO_ARCHIVE.md`. They are `human-gate-evidence-integrity` ("catalog approval identity") and `friction-score-backfill-throughput` (`daily-update --dry-run`). Either the guardrail shipped and the page should record it, or the ticket was dropped.
- ⚠️ Five pages have `Occurrences` of 2 or more and `Enforced by: judgement` or `pending`. These are `local-validation-and-final-gates` (6), `deny-list-guards-need-a-case-per-real-form` (12), `acceptance-check-provenance-is-not-usefulness` (8), `check-rewrite-diff-assertions-not-file` and `step-check-must-assert-presence-not-absence`.
- ⚠️ `deny-list-guards-need-a-case-per-real-form` is at 12 occurrences with a pending guardrail. That is a strong promotion or enforcement signal.
- ⚠️ `local-validation-and-final-gates` points at a TODO line for `pythonpath = foundry tests` in `pytest.ini`. That line is still open.

**Docs**
- ✅ AGENTS.md, PRODUCT.md, DESIGN.md, README.md and ROADMAP.md all changed between 2026-10-20 and 10-25. No staleness signal.
- ⚠️ `TODO.md` is 19 KB, over the ~15 KB limit. Its Review deferrals list has 14 items, including some dated 2026-10-01 to 10-11. Every phase that grounds on it pays that read.
- ✅ The verify feature map is stamped 2026-10-20, which is 5 days old. 87 code commits have landed since, but the stamp is under the 30-day warning threshold.

**Workspace**
- ✅ The tree is clean and nothing is unpushed. `check-run.py --all` reports 0 errors. 40 runs are done, 1 is complete (`topics-page`, touched today), and there are no `proto/*` branches. `.workflow/` is tracked.
- ⚠️ 3 runs are parked. They are `decision-model-evaluation` (last touched 10-17), `topic-catalog-quality` (10-17) and `gpt6-classifier-cutover` (10-13). None is old enough to be stale.
- ⚠️ `.workflow/topic-summary-agent/data/t8-backfill-scope.json` is 156 KB, over the ~100 KB warning.
- ⚠️ `WORKLOG.md` is 18 KB with 165 lines.

**Config**
- ✅ `.gitignore` covers `.DS_Store`, venvs, `.local/`, build output and `.workflow/archive/`. No tracked `.env`, `.pyc` or virtualenv files.

**Seats**
- ✅ Evidence is present. Every recent `WORKLOG.md` entry has `Run:` and `Seats:` lines. Review cycles run 1 to 3, with 0 findings overturned.
- ✅ The table below is too thin to judge a promotion.

| Seat | Model | Runs | Notes |
|---|---|---|---|
| 2 | Claude Opus 5.5 | most | steady |
| 2 | Claude Sonnet 5.5 | 2 | trial, little evidence |
| 3 | GPT-6.1 Sol | most | one run used Opus 5.5 |
| 4 | Claude Opus 5.5 | most | one run used GPT-6.1 Sol |

- ⚠️ Test growth: across the last 8 entries that carry it, net code is +1,625 lines and net tests are +1,630. Tests grew slightly faster than code. No run paid code down.
- ⚠️ 4 of the last 12 `Seats:` lines record seat 0 or 2 as `model unrecorded`.
- ✅ `ROUTING.md` was last verified 2026-09-30, which is 25 days ago.
- ⚠️ The strict-reviewer exam set at `~/.agents/j-skills-evals/strict-reviewer` has 10 cases and a passing latest result. A leftover per-repo `evals/reviewer/` directory with 16+ older cases should move into the exam set or be pruned. That is a human decision.

### Questions

**1. Is Claude Code used in this repo?** `.claude/` does not exist, so the verify and `cx-*` skills are invisible to Claude Code. AGENTS.md also says Claude Code is blocked by IT.
- ➡️ **a) Yes, link the skills** — recommended: this session is running in Claude Code, so the skills are missing right now.
- b) No, leave it — it costs nothing, but the verify skill stays invisible here.

**2. What should happen to the two dropped guardrail tickets?** `human-gate-evidence-integrity` and `friction-score-backfill-throughput` point at TODO lines that were archived.
- ➡️ **a) Check git history and update both pages** — recommended: it settles whether the guardrails shipped.
- b) Restore the TODO lines — it keeps the guardrails open without checking if they are done.

### Action cards

**▶ Next: Trim TODO.md and settle the memory enforcement flags**

- **Why:** `TODO.md` is 19 KB against a ~15 KB budget, so every phase pays that read. Two memory pages cite archived TODO lines, and a page at 12 occurrences has no enforcement.
- **Reset:** yes
- **Model:** Brainstorm partner seat (see `ROUTING.md`)
- **Fallback:** the seat's fallback from `ROUTING.md`

**Run:**

```text
Repo /home/john/cx-intelligence. Run `workflow todo`. TODO.md is 19 KB over the ~15 KB budget, with 14 Review deferrals dated 2026-10-01 to 10-25 (lines 31-46). Propose which to fold into runs or archive to TODO_ARCHIVE.md with the original wording. Do not archive without approval. Also check memory/human-gate-evidence-integrity.md and memory/friction-score-backfill-throughput.md. Both say "Enforced by: pending" but their TODO lines are in TODO_ARCHIVE.md. Report whether each guardrail shipped. Then run `memory.remember` for memory/deny-list-guards-need-a-case-per-real-form.md (12 occurrences, pending guardrail) and propose an enforcement or promotion.
```

**▶ Next: Reduce test growth**

- **Why:** Net tests (+1,630) exceed net code (+1,625) over the last 8 runs, and no run paid code down. Every run pays for the extra test maintenance.
- **Reset:** yes
- **Model:** Brainstorm partner seat (see `ROUTING.md`)
- **Fallback:** the seat's fallback from `ROUTING.md`

**Run:**

```text
Repo /home/john/cx-intelligence. Run `workflow improve tests - goal: fewer tests, same coverage`. Evidence: WORKLOG.md Run lines show net tests +1,630 against net code +1,625 over the last 8 entries. Preserve the AGENTS.md rules on approved evaluation samples and frozen labels. Propose the cuts and wait for approval.
```

**▶ Next: Link skills for Claude Code and Codex**

- **Why:** The repo skills are invisible to both tools until they are linked. This is a safe fix, subject to Question 1.
- **Reset:** no
- **Model:** human · create the symlinks
- **Fallback:** none

**Run:**

```text
Run `checkup workspace` and apply the safe fix: link .agents/skills/<name> into ~/.codex/skills/ and .claude/skills/ for each of the 9 repo skills. Do this only after the user's answer to Question 1.
```

**Safe fixes: none applied.** Plan mode is active and this checkup is read-only. Say so if you want the symlink fixes offered one at a time.
