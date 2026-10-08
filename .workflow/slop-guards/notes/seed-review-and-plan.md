# Workflow slop review and implementation plan

Date: 2026-10-07
Scope: the `workflow` skill in j-skills, checked against what it produced in cx-intelligence and
against `addyosmani/agent-skills` at commit `1401c8b8`, which is MIT licensed.

Inputs:
- `/Users/JVIKLUN1/Documents/projects/docs/architecture-review-20261007-073901.html`
- `cx-intelligence/.workflow/` runs from 2026-09-28 to 2026-10-07, plus their commits
- `j-skills/.github/skills/workflow/` covering `SKILL.md`, `references/*`, `scripts/check-run.py`
- `addyosmani/agent-skills`, all 25 skills, `references/`, `hooks/`, `evals/` and `docs/skill-anatomy.md`

---

## 1. Summary

The workflow is strict about whether code is correct. It says nothing about how much code is
written. No rule pushes toward less code, fewer tests, reusing a helper or deleting anything.
Wrap even says "nothing is deleted from the repo". Some of the workflow's own rules make each run
bigger:
- every acceptance line needs a literal value
- tests must go through the surface the user reaches
- operator tickets need a dry run, receipts, offline replay checks and a fresh approval

Each rule is sensible on its own. Together, with no counterweight, a 12-line fix turns into a
178-line end-to-end test, and a call costing half a cent turns into about 600 lines of script,
test and receipts.

agent-skills has the counterweight we lack:
- an explicit simplicity rule
- change-size thresholds in review
- a test pyramid and test-size model
- a "check the test can fail" step
- a deletion skill that treats code as a liability
- limits that only tighten, recorded mechanically

The plan below adds these to the workflow, mostly as small edits plus new checks in
`check-run.py`. It adds no new phases.

---

## 2. Evidence

### 2.1 Architecture review of cx-intelligence

| Finding | Size | Workflow cause |
|---|---|---|
| 01 Unreachable A2UI module | 4.9k lines | No dead-code or live-importer check at review or wrap. A guard scanned an empty folder and passed vacuously |
| 02 Tracked trees with no callers | 17k lines, 5,214 files, 31 MB | Wrap keeps everything, and "nothing is deleted" |
| 03 Each campaign rebuilds the harness | 17.9k lines in `operations/`, sha256 helpers 6×, 29 tests pinned to `.workflow/archive/` | No "reuse first" rule. Operator tickets require a bespoke preflight, authorization and receipt each time |
| 04 13k-line `repository.py`, 17k-line test | | No file-size signal. Prefactor exists but nothing triggers it |
| 05 SQL tests assert source text | 9.5k lines, 3,684 asserts, top churn | `tests.md` names "breaks on refactor" as a sign but does not ban asserting source text |
| 06 Hand-walked contract validators ×8 | 8.8k lines | Duplication across runs is never seen. Each run reviews only its own diff |
| 07 Percent formatting with 6+ copies | | Same as 06 |

Growth was 81k lines on Jul 1 and 296k today. September alone added 95k lines.

### 2.2 Recent runs, from `git show --stat`

| Commit | What | Product code | Tests | Run scripts, tests, receipts |
|---|---|---|---|---|
| `51e984f3` | Invalid citations become source errors | +12 / -8 | +178, a new file | +71 |
| `44a0a880` | Relevance verdicts before citing | +61 | +275 | +74 |
| `8319d1b4` | Separate customer question from search query | about +64 | +183 | +55 |
| `64587578` | Prepare one Global retry costing about $0.005 | 0 | 0 | +609: script 218, its test 168, 3 receipts |
| `8f0bae5a` | Prepare a Global probe | 0 | 0 | +769: script 266, its test 285 |
| `bf8818cd` | Prepare a Sweden probe | 0 | 0 | +643: script 206, its test 271 |
| `4f73f28d` | Prepare agent v3 | +23 | +17 | +473: script 150, its test 153 |

Repo totals: tracked `tests/` is 98.7k lines, and non-test backend Python under `foundry/` is
73.6k lines. Tests now outweigh the code they test.

**The 178-line test for a 12-line fix**, `tests/test_self_service_invalid_citations.py`, shows
the pattern:
- each test builds the agent runner, the coverage service, the SQLite cache and a FastAPI
  TestClient
- assertions pin full computed strings such as `"16 of 20 market-question checks completed (10
  evidence found, 6 gap candidates, 4 source errors)"`, prompt JSON layout and call counts
- one test makes 15 or more assertions that span four behaviours
- it imports fixtures from two other test modules, `test_self_service_agent_tool` and
  `test_self_service_relevance`. Test modules depend on each other

The plan's acceptance lines ask for exactly this. Each one is a paragraph that packs several
outcomes and literal strings together. See the T1 lines in
`.workflow/self-service-invalid-citations/plan.md`.

**Operator ceremony.** Each paid call gets a one-off script, a test of that one-off script, a
handoff, a preflight, a preparation-verification and an approval receipt. The test of the
retry script even loads another run's test file as a helper module. Tests of code that runs once
are pure cost: when the script runs, the receipt already proves it worked.

### 2.3 Where the workflow allows or causes this

| Workflow location | What it says | Effect |
|---|---|---|
| `references/phase-2-plan.md` §3 "Testable" | Literal expected value, observed at the reached surface, with positive assertion and inherited semantics | Each acceptance line becomes a full-stack test with many literal assertions. Nothing asks for the smallest seam that still proves it |
| `references/tests.md` "Test the surface that is actually reached", "Round-trip contracts" | Drive the page, or validate against the consumer | Correct for one test per behaviour. With no pyramid guidance, every test becomes end to end |
| `references/phase-3-execute.md` "Green" | "Write the least code that passes" | Good, but nothing measures it. No diff budget and no reuse check |
| `references/phase-3-execute.md` "Extra tests are welcome" | Extra tests welcome when the acceptance lines imply them | Lets test volume grow without limit |
| `references/phase-2-plan.md` "Operator tickets" | Handoff, dry run first, receipt | Has no scale for proportion. A $0.005 call gets the same ceremony as a production deploy |
| `references/phase-4-review.md` severity table | Scope creep and design concerns are P2, deferred to `TODO.md` | Bloat the run itself added is always deferred and never paid back |
| `references/phase-4-review.md` Defects | Escape-hatch scan only | No check on diff size, duplication, dead code or test-to-code ratio |
| `references/wrap.md` step 9 | "Nothing leaves `.workflow/<slug>/`, nothing is deleted from the repo" | Scripts, harnesses and their tests live forever, and some get pinned by tests outside `.workflow/` |
| `SKILL.md` Budgets | Line caps for the brief, plan and review documents | Caps exist for prose, not for code or tests |

Note: `SKILL.md` already says "Code outside `.workflow/` never reads anything inside it", yet
29 tests in `tests/` are pinned to `.workflow/archive/`. Review's `.workflow/` grep only scans the
current diff, so older violations persist.

---

## 3. What agent-skills offers

Only the parts that bear on slop are listed. Paths are in `addyosmani/agent-skills`.

| Idea | Source | Value here |
|---|---|---|
| **Enforce simplicity.** "If you build 1000 lines and 100 would suffice, you have failed." Ask what a staff engineer would cut | `skills/using-agent-skills/SKILL.md:77-95`, `skills/incremental-implementation/SKILL.md` Rule 0 | Missing entirely |
| **Scope discipline.** "Noticed but not touching" list, no orthogonal cleanups | `skills/incremental-implementation/SKILL.md` Rule 0.5 | We already have `## Deviations`. Keep ours |
| **Change sizing.** About 100 lines is good, 300 is acceptable, 1000 means split. A file near 1000 lines is a signal | `skills/code-review-and-quality/SKILL.md:103-124` | A mechanical signal we lack |
| **Readability and simplicity as a review axis**, plus named structural remedies: collapse duplicate branches, delete pass-through wrappers, separate orchestration from logic | `skills/code-review-and-quality/SKILL.md:66-78` | Gives the reviewer words for bloat findings |
| **Verify the verification.** Invert one condition the change adds and run the suite. A mutation that stays green is a finding | `skills/code-review-and-quality/SKILL.md`, about line 210 | Better proof than adding more tests |
| **Test pyramid of 80/15/5 and test sizes** Small, Medium and Large by resource use | `skills/test-driven-development/SKILL.md:140-173` | Counterweight to "reached surface" |
| **One assertion per concept**, DAMP over DRY but no shared mega-setup, mock hierarchy real > fake > stub > mock, anti-pattern table | `skills/test-driven-development/SKILL.md:198-282` | Sharpens `tests.md` |
| **The Beyonce Rule**: tests must catch real regressions, not mirror internals | same, :161 | Supports banning source-text tests |
| **Limits that only tighten.** "Record where you are, then refuse to get worse." Guard the bar itself: a threshold moved, a test weakened, a checker silenced | `skills/constraint-driven-development/SKILL.md:195-249`, `references/floor-guard.md` | Fits `check-run.py` directly |
| **Code is a liability.** Zombie-code signals, the churn rule, expand–contract | `skills/deprecation-and-migration/SKILL.md` | Gives wrap a deletion step |
| **Chesterton's Fence** before deleting. Above 500 lines, use automation | `skills/code-simplification/SKILL.md:109,171` | A safe deletion procedure |
| **Neutral is a revert.** Code that does not clear its bar is reverted, because "code you keep, you maintain forever" | `skills/performance-optimization/SKILL.md` | Good principle for experiment and campaign code |
| **Dead-code hygiene.** List it, then ask before deleting | `skills/code-review-and-quality/SKILL.md` | Review and wrap behaviour |
| **Doubt-driven review.** Give the reviewer the artifact and its contract, never your conclusion. "Doubt theater" means many findings and none actionable | `skills/doubt-driven-development/SKILL.md` | Small tweak to our cross-vendor review input |
| **Pressure-case evals.** Prompts built to argue the skill out of its own rules | `evals/plugin/`, `evals/fixtures/*-pressure/` | Extends our `evals` exam to slop cases |
| **Write the procedure, not the workaround.** Model-specific workarounds can make stronger models worse | `docs/skill-anatomy.md:150-163` | Supports our existing rule that only `ROUTING*.md` names models |
| **Three outcomes.** Every call ends in success, failure or unknown, and the idempotency key comes from intent | `skills/api-and-interface-design/SKILL.md` | Shape of the shared governed-run module in cx-intelligence |

**Not bringing over:**
- the lifecycle and slash commands, since we have them
- personas, which `MAINTAINING.md` forbids
- `/ship`, CI/CD, observability, shipping-and-launch and the error-budget gate, which are not the
  problem here
- the frontend aesthetic table, which `hallmark` covers
- the sdd-cache hook, which is too narrow
- the simplify-ignore hook. It is interesting, but nothing protected is being harmed

---

## 4. Recommendations, ranked

Each one gives the problem, the change, and how to tell it worked.

### R1. Size limits that only tighten, recorded and checked mechanically. Highest leverage

**Problem.** Nothing measures how much a run adds, so judgement alone has to resist the pull of
the other rules, and it loses.

**Change.**
- Plan records a `Size:` baseline in `plan.md` with five numbers:
  - product lines, excluding tests and `.workflow`
  - test lines
  - the test-to-code ratio
  - the three largest files the plan touches
  - the files over a threshold of 1,000 lines
- Each ticket gets a `Budget:` field estimating net lines for code and tests, for example
  `Budget: code +40 · tests +60`.
- Execute records the actual net lines next to `Status: done`.
- `check-run.py` reads `git diff --numstat` per ticket commit:
  - WARN when a ticket goes more than 2× over budget without a `## Deviations` line
  - ERROR when tests added exceed code added by more than 3× on a logic ticket with no stated reason
  - WARN when a touched file grows past 1,000 lines
- Review gets a `Size` line in Coverage with total added lines, the ratio, and whether net lines
  are negative.
- The limit only tightens. The run may not raise the repo's test-to-code ratio or any touched
  file above 1,000 lines without a `Deviations` line that review accepts.

**Done when.** The next three cx-intelligence runs show a budget per ticket and a size line in
review, and `check-run.py` catches a planted 4× overrun in a fixture run.

### R2. Simplicity and reuse rules in plan and execute

**Problem.** The 6× sha256 helpers and 6+ copies of `formatPercent` mean nobody searched for
existing helpers.

**Change.**
- Add a short **Simplicity** block to `SKILL.md` Ground rules, about 4 lines, saying three things:
  - the smallest diff that passes is the target
  - search the repo for an existing helper before writing one, and record the search in the ticket report
  - new abstractions need two live callers
- In `phase-2-plan.md` §1, add **Reuse findings** as a finding row type: for each new helper,
  harness or format function a ticket implies, run the search and record the existing equivalent.
- Change §2 Prefactor: when the search finds two or more near-copies, the prefactor ticket
  consolidates them first, which is "make the change easy".
- In `phase-3-execute.md` Green, after "least code", add that a new function duplicating an
  existing one is a deviation.
- The report's `Noticed:` line names any helper written despite a search hit.

**Done when.** A plan touching formatting or hashing shows a reuse finding row, and review never
finds a same-run duplicate as P2.

### R3. Proportional tests: smallest seam, fewest assertions, prove each test can fail

**Problem.** "Literal at the reached surface" makes every acceptance line an end-to-end test with
a dozen literals.

**Change to `references/tests.md`:**
- **Pick the smallest seam that proves the line.** A pure rule gets a unit test of the function.
  The reached surface gets **one** end-to-end test per behaviour, not per acceptance line. Add
  the pyramid wording: most tests small, few through the API or UI.
- **One concept per test, few literals.** Assert the value the line names. Do not also assert
  unrelated derived strings, call counts or prompt layout. Exact long strings only when the
  string is the product, such as user-facing copy.
- **Parametrize over variants instead of new tests.** The citation test already does this well
  for four invalid shapes. Make it the default.
- **No test-module imports of other test modules.** Shared fixtures go in `conftest.py` or a
  fixtures module.
- **Never assert source text.** That covers SQL text, file contents of code and CTE aliases.
  Assert the schema contract or the output. A deny-list of forbidden tokens is the one exception.
- **Prove it can fail, cheaply.** For each new test, revert or invert one line of the change and
  see it go red. Record that in the ticket report as `Mutation: <line> → red`. This replaces
  "extra tests are welcome".
- **Test budget.** A logic ticket's test lines should be the same order as its code lines. Above
  3×, the report says why.

**Change to `phase-2-plan.md` §3 Testable:**
- An acceptance line names **one** outcome, at most about 25 words. The current T1 lines run 40
  to 60 words each.
- The `Seam:` field names the smallest seam, and the outcome line names the one surface-level check.

**Change to `phase-3-execute.md`:** strike "Extra tests are welcome where they pin behaviour the
acceptance lines already imply". Replace it with "Add a test beyond the acceptance lines only
when a mutation survives".

**Done when.** On the next three runs, the median ratio of test lines to code lines per logic
ticket is at most 2×, and each ticket report has a `Mutation:` line.

### R4. Operator tickets scaled to risk, not a fixed ceremony

**Problem.** A $0.005 reversible call gets roughly 600 lines: a one-off script, a test of that
script, and 3 to 6 receipts. The harness pattern then spreads into `foundry/operations/`.

**Change to the operator section of `phase-2-plan.md`.** Add a **Risk class** to every operator ticket:

| Class | Example | Ceremony |
|---|---|---|
| `cheap` | Reversible, under about $1, read-only or writes a cache row | One handoff, under 20 lines, with the command and the scope. One receipt with the literal values. **No bespoke script test.** Reuse the repo's run harness or an existing CLI command |
| `costly` | Paid above a ceiling, or writes shared data | The current flow: dry run, approval, receipt |
| `irreversible` | Deploys, deletes, production schema changes | The current flow plus a rollback line |

Also:
- A run script in `scripts/` gets a test only when two or more tickets run it, or its class is not `cheap`.
- When the repo has a governed-run module, which after R8 cx-intelligence should, an operator
  ticket calls it with a spec and writes no harness.
- `check-run.py` WARNs when a `cheap` operator ticket's commit adds a `test_*.py` under the run's `scripts/`.

**Done when.** The next cheap probe ticket in cx-intelligence adds fewer than 100 lines in total.

### R5. Review treats bloat the run itself added as P1, and checks that new code is reachable

**Problem.** Bloat is always P2, so it is deferred. The A2UI module and the vacuous guard went
through review.

**Change to `references/phase-4-review.md`:**
- Add **Simplicity** to the Defects question, next to the escape hatches, with three checks:
  1. **Same-run waste**: duplication of an existing helper, a pass-through wrapper, an unused
     parameter or branch, or a test that asserts nothing a sibling test doesn't. It is **P1 when
     the run's own diff added it**, because it is cheap to fix now. It stays P2 when it was there
     before.
  2. **Reachability**: every new module, export or file in the diff has a live importer from an
     entry point, and every new guard or check is shown failing once. Unreachable new code is P1.
  3. **Verify the verification**: pick the riskiest acceptance line, invert one condition in the
     code, and run its test. If it stays green, that is P1, a missing assertion.
- Add a fourth mechanical check: `git diff --numstat <plan Base>..HEAD`, giving added and deleted
  lines for code and tests, the ratio, and any file crossing 1,000 lines. These go in
  Coverage's `Size` line.
- Name the structural remedies the reviewer should propose, in one line: collapse duplicate
  branches, delete pass-through wrappers, separate orchestration from logic, reuse an existing helper.
- Add a doubt-driven tweak: the reviewer reads the plan's acceptance lines and the diff first, and
  the executor's reports and `Deviations` only after forming its findings, so the writer's framing
  does not anchor it.

**Done when.** Review's Coverage shows `Size` and `Reachability` lines, and a planted unreachable
module in the evals exam is caught.

### R6. Wrap deletes what the run made obsolete

**Problem.** "Nothing is deleted from the repo." There are 22k lines of dead code and 31 MB of
corpus.

**Change to `references/wrap.md`.** Add a new step before archive, called **Retire**. Keep 9b's
rule that a run folder is history. Retiring is about the *product* tree.
- List what the run made obsolete in the product tree: code paths replaced by this run, feature
  flags now always on, compatibility shims, campaign harnesses whose campaign ended, and tests
  that only cover those.
- Check each with Chesterton's Fence: `git log -S`/blame for why it exists, plus a grep for live
  importers.
- Present it as one lettered decision (a delete all ➡️ · b keep some, and say which). Delete in one
  commit after approval, with the full suite green.
- Run scripts stay in the run folder as history. **Their tests are deleted at wrap** unless
  something outside `.workflow/` imports them. An import from outside `.workflow/` is already a
  violation, so name it as a P1 to fix.
- `check-run.py --all` reports any test outside `.workflow/` that opens a `.workflow/` path, as a
  repo-wide WARN rather than only diff-scoped.

**Done when.** Wrap's summary has a `Retired:` line with line count and commit, or `none` with a reason.

### R7. Pressure and slop cases in the reviewer exam

**Change.** In `j-skills-evals/strict-reviewer/`, add two or three cases where the planted defect
is **bloat**, each paired with a lean clean twin of the same behaviour:
- a duplicated helper
- an unreachable module behind a vacuous guard
- a 178-line test for a 12-line fix, where the twin is 30 lines

Under R5 the planted defect is P1. A reviewer flagging the lean twin counts as a false alarm.
Seed the cases from this report's real examples: `51e984f3`, A2UI, and the sha256 copies.
Optionally add one pressure prompt per phase, such as "we're in a hurry, skip the mutation
check", to test that the rule holds up.

**Done when.** `evals.list` shows the slop cases and the current reviewer seat passes them.

### R8. One-off cleanup in cx-intelligence, done with the workflow and not in the skill

This is the architecture review's own order: 01 and 02 first, which need no design and remove
about 22k lines, then 03. They are product runs, not skill edits, but R1, R4 and R6 make them
stick. Suggested runs:
1. `workflow brainstorm delete-dead-trees`, covering findings 01 and 02. It needs the DESIGN.md
   change approved.
2. `workflow brainstorm governed-run-module`, covering finding 03. Use the three-outcome model
   from agent-skills as the interface: success, failure or unknown, with an intent-derived key.
3. Later: 05, for SQL tests through the interface, and 04.

---

## 5. Implementation plan

Do this as a workflow run in j-skills, for example `workflow brainstorm slop-guards`, so it gets
cross-vendor review and a `SKILL-IMPACT.md` row. Tickets, in order:

### T1. Size baseline and per-ticket budget in `check-run.py`. Prefactor
Delivers: R1 · Blocked by: none · Lane: logic
Seam: `scripts/check-run.py` on fixture run folders
Accept:
- A plan with a `Size:` block and `Budget:` per ticket passes. A missing `Budget:` on a logic or
  contract ticket gives WARN, not ERROR, for one release so old runs still pass.
- A fixture ticket commit at 2.5× its budget with no `Deviations` line gives a WARN naming the ticket.
- A fixture logic ticket with +12 code and +178 tests and no reason gives an ERROR.
- A fixture `cheap` operator ticket that adds `scripts/test_*.py` gives a WARN.
Verify: a new test file for `check-run.py` with fixtures under `scripts/tests/`. Check whether
one exists first, and if not add a small one.

### T2. Simplicity and reuse rules
Delivers: R2 · Blocked by: none · Lane: doc
Files: `SKILL.md` Ground rules, about 4 lines, keeping the hub under 180 lines.
`references/phase-2-plan.md` §1 for reuse findings and §2 for prefactor consolidation.
`references/phase-3-execute.md` Green and the report's `Noticed:` line.
Accept: grep for "Reuse:" in plan §1 gives 1. The hub stays at 180 lines or fewer.

### T3. Test proportionality
Delivers: R3 · Blocked by: none · Lane: doc
Files: `references/tests.md` gets new rules on smallest seam, one concept, parametrize, no
test-module imports, no source-text asserts, the mutation check and the test budget.
`references/phase-2-plan.md` §3 caps an acceptance line at one outcome and about 25 words.
`references/phase-3-execute.md` replaces "extra tests are welcome" and adds `Mutation:` to the report.
Accept: `tests.md` stays under about 70 lines. The report template has a `Mutation:` line.
`check-run.py` WARNs on an acceptance line over 40 words, added to T1 or here.

### T4. Operator risk classes
Delivers: R4 · Blocked by: T1 · Lane: doc and logic
Files: `references/phase-2-plan.md` operator section adds `Risk: cheap|costly|irreversible` and
the class table. `phase-3-execute.md` scales the operator flow by class. `check-run.py` requires
`Risk:` on operator tickets, WARN for one release.
Accept: a fixture operator ticket without `Risk:` gives a WARN. A `cheap` handoff template is
20 lines or fewer.

### T5. Review simplicity axis, reachability, mutation and size line
Delivers: R5 · Blocked by: T1, T3 · Lane: doc and logic
Files: `references/phase-4-review.md` changes Defects, the severity table row for same-run waste
at P1, the mechanical checks with numstat, the Coverage template with `Size:` and
`Reachability:`, and reading order. `check-run.py` requires the `Size:` line in Coverage.
Accept: a fixture review without a `Size:` line gives an ERROR. The severity table has a
"same-run waste" row.

### T6. Wrap retire step and a repo-wide `.workflow` pin check
Delivers: R6 · Blocked by: T5 · Lane: doc and logic
Files: `references/wrap.md` gets a new Retire step before 9, and the "nothing is deleted from the
repo" wording is reworded to "nothing is deleted from the run folder". `check-run.py --all`
gets a repo-wide grep for `.workflow/` paths in tests outside `.workflow/`. `checkup` reports it.
Accept: a wrap summary without `Retired:` gives an ERROR. A fixture repo with a test opening
`.workflow/x` gives a WARN under `--all`.

### T7. Exam slop cases
Delivers: R7 · Blocked by: T5 · Lane: logic, in the private `j-skills-evals` repo
Accept: three slop cases with clean twins, and `evals.list` shows them.

### T8. Docs, attribution, impact log and trigger tests
Delivers: all · Blocked by: T2 to T7 · Lane: mechanical
Files:
- `workflow/README.md` gets a short "Keeping runs lean" section
- `j-skills/README.md` gets a one-line workflow table tweak if needed
- `THIRD-PARTY-NOTICES.md` gets an addyosmani/agent-skills MIT notice, since wording is adapted
  from `code-review-and-quality`, `test-driven-development`, `constraint-driven-development`,
  `deprecation-and-migration` and `code-simplification`
- `SKILL-IMPACT.md` gets a row with the hypothesis "test-to-code ratio and lines per ticket drop
  on the next 3 cx-intelligence runs" and the baseline numbers from §2.2
Accept: the notice is present, and the `SKILL-IMPACT.md` row has the baseline values.

That is 8 tickets, within the plan limit. T2 and T3 are prose-only and can land first if you want
quick wins. T1 is what makes the rest hold.

### Measuring it

Record the baseline now, from §2.2, in `SKILL-IMPACT.md`:
- per logic ticket, tests are about 3× to 15× the code
- each operator preparation commit is 470 to 770 lines
- in the repo, `tests/` is 98.7k lines against 73.6k of code, a ratio of 1.34

Re-measure after three runs. Target:
- the median ratio of test lines to code lines per logic ticket is 2× or less
- a cheap operator ticket is under 100 lines
- the repo ratio stops rising
- at least one run wraps with a non-empty `Retired:` line

---

## 6. Risks and open decisions

1. **Weaker tests.** Cutting volume could drop real coverage. The mutation check in R3 and R5 is
   the safeguard: it proves each kept test can fail. Keep the existing rule that existing tests
   keep their assertions. Deletion happens only through wrap's Retire step, with approval.
2. **More ceremony to fight ceremony.** New fields like `Budget:`, `Risk:`, `Size:` and
   `Mutation:` add process. Keep them one line each and checked by script, so judgement stays
   for design. Start them as WARN, not ERROR.
3. **Same-run waste as P1 lengthens patch cycles.** The three-cycle bound still holds. If it
   causes churn, move it back to "P2, fix now by default".
4. **Thresholds.** The 1,000-line file, 3× test ratio and 25-word acceptance line are starting
   guesses taken from agent-skills' sizing. Tune them after three runs.
5. **DESIGN.md and AGENTS.md in cx-intelligence** protect some of what R8 deletes, such as the
   A2UI line and `.workflow/archive/` pinning. Those need your explicit approval in their runs.
6. **Decision needed:** apply R5's reading-order change, where the reviewer sees the executor's
   reports after its own pass, or keep the current order. ➡️ Apply it. It is cheap and removes
   anchoring.
