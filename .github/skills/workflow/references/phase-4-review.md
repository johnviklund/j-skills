# Review — `workflow review` (+ patch cycle)

> ⚠️ Read through the `workflow` skill; the phase ends with its closing card.

Seat: **strict reviewer** (`ROUTING.md`), a different vendor from the code's writer. Read the
`writer:` field and per-ticket `Writer:` lines in `plan.md` and look up each model's vendor in
`ROUTING.md`; if one matches yours, this is a
degraded same-vendor review and `review.md` says so. Read-only sub-agents may split a wide diff.

**Blind first.** Read the brief, the tickets' acceptance lines and the diff, and draft findings.
Only then read the writer's reports, `## Deviations` and `learnings.md`, so the writer's framing
does not set yours.

Review answers two questions, kept apart so one can't hide the other:

- **Acceptance** — does the code do what the brief and tickets agreed? For every ticket, each
  acceptance line has a test (or receipt) that exists, passes, and asserts the literal the line
  names; every behaviour (B#) is delivered; every out-of-scope item is untouched; nothing was built
  that no ticket asked for. Then check the **Outcome** where the brief says the user reaches it —
  the rendered page, the served snapshot, a live read-only query. Passing acceptance lines are not
  proof of it: a bar can pass on provenance while the user sees nothing useful. When the repo
  has a verify skill (`.agents/skills/verify-*/`), drive the Outcome with it along every entry
  point its feature file lists, evidence in `receipts/`. A run with a user surface and no verify
  skill notes `no verify skill` on the Outcome coverage line and recommends `verify.create` in
  the verdict.
- **Defects** — does it break anything? Verify empirically: run the tests, trace producer →
  consumer, run live queries. Look for missing error handling, data loss, resource leaks, security
  flaws, and logic that defeats the feature's own guarantee (a gate that can never fire). In any
  test the run didn't create, count assertions before and after; an unexplained drop is a P1.
  **Escape hatches are design evidence:** a new `any`, forced cast, non-null assertion or
  suppressed type or lint check, the same workaround at two or more unrelated call sites, or an
  optional field that is always set in practice says the design is wrong where the code is
  merely awkward. Report it as a P2 naming the design flaw, not the line (the type that should
  carry the fact, the boundary that should parse it); P1 when it breaks a behaviour. A hatch at a
  boundary that parses outside data is fine.
  **Simplicity** is part of Defects, with three checks:
  - **Same-run waste.** A copy of an existing helper, a pass-through wrapper, an unused
    parameter or branch, or a test that asserts nothing a sibling test doesn't. P1 when this run's
    diff added it; P2 when it was there before.
  - **Reachability.** Every new module, export or file has a live importer from an entry point,
    and every new guard or check is shown failing once. Unreachable new code is P1.
  - **Verify the verification.** Pick the riskiest acceptance line, invert one condition the
    change adds, and run its test in a throwaway `git worktree`, never committed. A test that
    stays green is a P1 missing assertion.

  Each such finding proposes its remedy: collapse the duplicate branches, delete the wrapper,
  split orchestration from logic, or reuse the existing helper.

## Severity — the bar that keeps cycles short

| | Means | Default disposition |
|---|---|---|
| **P0** | data loss, security hole, crash on a normal path, a behaviour inverted, wrong or misleading data shown to users as correct | fix now |
| **P1** | an acceptance line or behaviour missing or wrong; the Outcome false on its surface; an out-of-scope item touched; a defect with a concrete failing input; same-run waste, unreachable new code, a surviving mutation | fix now |
| **P2** | real but outside what was agreed: scope creep, an edge case no behaviour covers, a design concern, waste older than the run | defer → `TODO.md` |
| **P3** | minor; at most five reported, the rest as a count | defer (stays in `review.md`) |

A P0/P1 names its evidence: the B# or acceptance line it breaks, the Outcome and what its surface
actually shows, the input that fails, or, for waste, the added lines and the existing
equivalent, both file:line. A finding that can't name one is P2 at most. Style,
naming, generated paths and anything lint/CI enforces are not findings. When a reproduction the
plan prescribed doesn't reproduce, suspect the finding rather than the harness, and re-price it.

**A repeat is memory.** Before recording a P0–P2, check `MEMORY.md` and the `## Must name` lines
of the exam set (`j-skills-evals/strict-reviewer/`, a private repo cloned beside j-skills; the `evals` skill says how to find it) for the same class of mistake; a second occurrence adds `[durable→memory]` to `learnings.md`.

## `review.md` — open it first, grow it as you go

The file is the only evidence review happened. Create it before reviewing anything, with the
provenance header (`Base:` = the HEAD sha reviewed, `Inputs: plan.md @ <its Base>`,
`Status: drafting`), and append each finding the moment it is confirmed. Budget ≤ ~100 lines: evidence
is a pointer plus the number that proves it (`file:line`, command, count) — never pasted output.

```markdown
## Coverage
- [x] T1 — acceptance 2/2 tested and passing
- [ ] T2 — …
- [x] B1…B6 delivered · Outcome observed on <surface> via <verify-APP | manual, no verify skill> · out of scope untouched
- [x] .workflow/ dependency check
Size: +<code> code · +<tests> tests · ratio <tests/code> · net +<n> · over 1,000: <files | none>
Reachability: <each new file → its live importer | none new> · guards shown failing: <ids | none>
Independence: cross-vendor | same-vendor (degraded)

## Resolved                    ← from cycle 2: a finding moves here once stamped or settled
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | <title> | fix now | @ <sha> (cycle 2) |

## Cycle 1 findings
### P1 — <title>
- Evidence: <B# / acceptance line / failing input> · <file:line> · <command output>
- Disposition: fix now | defer — Approved by human: <when, required for P0/P1> | wontfix — <reason>
- Resolved: — | @ <sha> (cycle N)

## Pre-existing / environmental

## Cycle 1 verdict              ← written last; sets Status: complete
```

After setting `Status: complete` (and after writing a `patch_plan.md`), run `python3 <skill>/scripts/check-run.py <slug>` (`<skill>` is the workflow skill's folder) and fix every
ERROR: dispositions, P0/P1 deferral approvals, the verdict and the patch tickets are all checked
there.

Coverage ticks as each area is done, so a reset resumes at the first unticked entry. Four
mechanical checks always run. The size count fills Coverage's `Size:` line (check-run ERRORs
without it): `git diff --numstat <plan Base>..HEAD -- . ':(exclude).workflow'`, split into code
and test files (a `tests/` folder, `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`; `*.md` and
`*.txt` count as neither), plus any touched file now over 1,000 lines. The escape-hatch scan
lists every hatch the diff adds; read each hit against the rule under *Defects*:
`git diff <plan Base>..HEAD -U0 -- . ':(exclude).workflow' | grep -nE '^\+[^+].*(: any\b|<any>|as any\b|as unknown as|@ts-(ignore|expect-error|nocheck)|eslint-disable|# type: ignore|# noqa|\bcast\(|\bunsafe\b|\.unwrap\(\)|//\s*nolint|[A-Za-z0-9_)\]]!\.)'`.
Third, nothing outside `.workflow/` references it
(`grep -rn --exclude-dir=.workflow --exclude-dir=understand --exclude='*.md' --exclude='*.txt' '\.workflow/' .` — a hit is
P1), and the full test suite — unless the receipt-rule diff `<plan Base>..HEAD` (`SKILL.md`) is
empty, in which case that empty diff is the regression proof.

In chat: the verdict, a count per severity, one line per P0/P1, and any disposition the human
owes as a lettered decision list. Verdict "ship as-is" when nothing needs acting on.

## After the verdict

**Clean** → `workflow wrap <slug>`.

**Only P2/P3** → their default dispositions stand unless the human picks "fix now" for one; the
deferred P2s become `TODO.md` lines at wrap, and deferred P3s stay in `review.md`. No patch cycle
is needed for defers.

**Any "fix now"** → write `patch_plan.md`: one fix ticket per finding, same ticket shape and
rules as `plan.md` (lane, seam, acceptance, verify with `pre:`, skills), numbered `C<cycle>-T#`
so their `@ <sha>` lines never collide with the plan's. The lane decides seat and approval: a fix
that touches a contract is a contract ticket whatever its severity. A behavioural bug is two
tickets: first a test that reproduces it, run and seen to fail, committed alone; then the fix,
which leaves every test file untouched. When the finding is a class that can recur (a field read
in several places, a call site pattern), the fix ticket's acceptance names every site — list them
with a search at planning time. The card routes to `workflow execute <slug>`, naming the
cycle and finding ids (`Patch cycle 1 · fix C1-1, C1-2`); P0 tickets go to the heavy executor.

**Re-review (cycle N ≥ 2)** — `workflow review <slug>` once every fix ticket is done. Set `Status: drafting`,
append `## Cycle N findings` and `## Cycle N verdict`, and move `Base` to the sha reviewed. As each
earlier finding is stamped (or its defer/wontfix is settled) it folds into `## Resolved` as one row —
the full text stays in git; a finding still open keeps its section. Read only `## Resolved`, open
findings and the current cycle, never settled older sections. Its scope is the
fix diff plus each finding's class: re-verify each finding at every site of its class, not only
the lines the fix touched (stamp `Resolved: @ <sha> (cycle N)` or reopen it — an incomplete fix
reopens the finding at its original severity), confirm each bug fix left the tests untouched and
its reproducing test passes, and look for regressions the fix diff introduced. Something new
outside that scope is recorded at P2, except a P0 (fix now) or a P1, which goes to the human as a
decision: a) fix now ➡️ when it breaks a B# or the Outcome · b) defer to `TODO.md`.

**Cycle bound — three.** Stop and escalate after the third cycle, or as soon as a P0 survives a
cycle. The escalation states the unresolved finding verbatim, each attempt and why it failed, and
one answerable question; the card routes to the human (`**Model:** human · <the one action>`).

A finding stays open until a later cycle stamps it. P0/P1 deferral needs the human's explicit
approval, recorded as `Approved by human:`. Wrap refuses any open "fix now" and any unapproved
P0/P1 deferral. A confirmed P0/P1 the writer missed may become a reviewer exam case if it passes
the admission test in `references/learning-worklog.md`: tag it `[durable→eval] code-review — …`
in `learnings.md`.

Optional before merging: for code the human doesn't fully understand yet, quiz them one question
at a time on intent, what changed, and the existing behaviour it now leans on.
