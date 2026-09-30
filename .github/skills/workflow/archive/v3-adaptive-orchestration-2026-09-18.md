# Archived v3 proposal: adaptive development with agent orchestration

Archived on 2026-09-18. Superseded by the active v3 direction in
[ROADMAP.md](../ROADMAP.md). This file is historical design context, not current
requirements or execution instructions. Read it only when investigating the prior
proposal; do not combine its commitments with the active roadmap.

The former v3 section is preserved verbatim below.

---

## v3 — Adaptive development with agent orchestration

The user provides intent, priorities, and direction through one conversation.
A coordinator running `jflow` organizes discovery, planning, implementation,
verification, independent review, delivery, and compound learning as the work needs.
The user can steer, pause, or resume without managing routine handoffs.
The user chooses one supported desktop app or CLI and works within it. Switching
hosts is a portability benefit, not the primary workflow or a requirement.

Success means returning in the same thread or a fresh supported session and
continuing with the objective, decisions, evidence, and unfinished work intact.
Small work stays small; complex work receives the coordination and scrutiny it needs.

### Product commitments

- **Adaptive work:** Scale discussion, documentation, decomposition, and verification
  to uncertainty and consequence. Entry directly at planning or implementation uses
  existing decisions and fills only material gaps.
- **Durable continuity:** Carry inspectable state with the project. Recover through
  saved records and Git evidence without relying on the original conversation.
- **Independent scrutiny:** Preserve independent model review as a core capability,
  with timing, perspectives, and depth matched to the work.
- **Compound learning:** Capture validated lessons, develop reusable methods, and
  evaluate improvements to skills and routing through actual use.
- **Provider and host flexibility:** Make desktop and CLI-only use first-class
  experiences in the user's chosen host, using its available models and integrations.
- **User direction:** Honor authorization, project policy, priorities, and budgets.
  Challenge weak assumptions with evidence and respect informed user decisions.

A fixed phase sequence, a separate manual mode, and standalone commands for every
helper are outside v3's scope. Preserve v2's useful capabilities and accumulated
knowledge through migration; its phase structure does not define v3's architecture.

### Guarantees at every task size

Adaptive effort must preserve these observable requirements:

- Settled decisions and actionable progress survive loss of the conversation.
- Scope and authorization changes are explicit; coordination grants no new permissions.
- Verification and review evidence identify the changes they cover.
- Self-review is never presented as independent review.
- Completion claims match evidence, with unresolved findings and limitations recorded.
- Retained lessons include applicability and supporting evidence.

Use observable signals such as contract or schema changes, authorization boundaries,
data-loss exposure, and failed checks alongside uncertainty to choose depth. File
count alone is a poor risk measure. A request for speed reduces ceremony while
preserving these guarantees. Validate routing choices against actual outcomes.

### Coordinator responsibilities

The coordinator owns the active task agreement and shared progress state. Workers
receive bounded assignments and return evidence and proposed state updates; they
must not independently rewrite shared scope or completion records. A resumed
coordinator recovers ownership without allowing competing writers to the same state.
The host supplies worker execution and permission mechanisms; jflow owns assignments,
acceptance criteria, evidence, and integration decisions. Task ownership alone does
not resolve concurrent updates to shared project knowledge.

| Responsibility | Expected behavior |
| --- | --- |
| Understand intent | Investigate facts, resolve consequential uncertainty, preserve the agreement. |
| Prepare work | Inspect current code, select helpers, size work units, establish dependencies and checks. |
| Coordinate execution | Assign work or execute directly, arrange isolation, handle discoveries and handoffs. |
| Arrange scrutiny | Supply independent reviewers with the relevant agreement, changes, and evidence. |
| Resolve and deliver | Assess findings, coordinate fixes, reconcile progress, and deliver under project policy. |
| Preserve and learn | Save recoverable state, retain validated lessons, and evaluate reusable improvements. |

Keep helpers focused. External specialist skills can supply methods such as UX/UI
review; jflow chooses them, supplies context, and integrates their results. Add
integration code where needed for reliable orchestration without depending on one
particular harness. Limited delegation can mean the coordinator executes locally.
Apply independent judgment to the coordinator's own plans and proposed helpers:
prefer a simpler approach or no change when the benefit does not justify the cost.

Workers return questions and blockers to the coordinator. It retrieves available
facts, supplies recorded answers, and resolves routine choices within authority.
When the user must decide, it presents the concrete choice, evidence, and recommendation,
records the answer, and informs affected workers. Dependent work waits while eligible
independent work can continue. Tool approvals remain enforced by the host; coordinator
ownership does not grant new permissions or bypass approval prompts.

### Discovery and the task agreement

Every request gets enough discovery and durable context. Clear changes can proceed
without questions; ambiguity warrants focused questions; consequential choices
warrant alternatives, concrete scenarios, and deeper investigation.

- Investigate facts available from code, documentation, history, and tools. Ask the
  user about goals, preferences, and consequential tradeoffs outside settled authority.
- Ask questions in dependency order: one difficult question or a small group of
  independent, easy questions, with recommendations and tradeoffs where useful.
- Stop when the next action is sufficiently defined and authorized. Do not exhaust
  hypothetical branches, repeat settled interviews, or add unnecessary approvals.
- Record settled decisions and remaining blockers as they emerge. Distinguish facts,
  assumptions, proposals, accepted decisions, and deliberate exclusions.

Default to **one compact task record** containing the intended outcome, relevant
constraints and exclusions, and observable acceptance criteria. Add contracts,
failure behavior, dependencies, and execution details only when useful. No mandatory
story inventory, empty sections, separate technical spec, or document per phase.

The agreement owns intent; execution details describe how to deliver it. These may
share a file. Refresh paths, symbols, and commands against current code without
silently changing scope. Preserve exact schemas or contracts when prose is ambiguous.
When new facts change the agreement, update it deliberately and preserve prior
rationale in history. Consequential changes beyond authorization require the user's
decision. A completed document or tracker label does not authorize execution.

### Durable state and project knowledge

Save the objective, constraints, decisions, priorities, progress, verification and
review evidence, pending work, and next actions. Checkpoint at meaningful changes
and before handoffs, including partial and uncommitted work. Persist settled decisions
before dependent work and save verification, review, and completion outcomes when
established. Context management and commit cadence follow host capabilities and
repository policy; recovery must not depend on detecting a compaction event.

Distinguish task-specific agreement and evidence, shared project knowledge, and
temporary host/session information. Validate ownership and merge behavior across
branches and worktrees, including separate tasks updating memory, routing, or skill
trial records. Preserve contributions and surface conflicting decisions. Choose
the storage and conflict strategy through trials before expanding orchestration.

Keep the entry record compact, with current intent, constraints, decisions, progress,
next action, and links to detail. Measure recovery accuracy and context cost before
setting size limits. Reconcile relevant state and current work at action boundaries
such as delegation, review, and completion; routine user-facing restatements are
unnecessary. The working tree shows current files, Git records committed history,
and the agreement records intent. Investigate discrepancies before relying on them.

Resume must retrieve enough evidence to reconstruct the task, check current
applicability, and continue accurately. This includes recovery from stale references
or truncated tracker responses through the authoritative project record. Do not
promise cross-tool or cross-machine resume without access to the required state.

Use one authoritative home for each kind of knowledge:

| Home | Owns |
| --- | --- |
| Task record | Current agreement, execution progress, blockers, and links to evidence. |
| `PRODUCT.md` | Product purpose, direction, and boundaries. |
| `DESIGN.md` | Design guidelines, patterns, and visual language. |
| `CONTEXT.md` | Project glossary only. |
| ADRs | Consequential, non-obvious decisions and their rationale. |
| `MEMORY.md` and `memory/` | Reusable operational lessons, applicability, and evidence. |
| Git and linked tracker history | Changes, previous decisions, reviews, and work history. |

Create glossary entries only for project-specific or easily confused terms. Keep
definitions to one or two sentences, adding distinctions or discouraged synonyms
when useful. Exclude implementation details, plans, progress, and general programming
vocabulary. Resolve ambiguity through concrete scenarios and distinguish intended
behavior from what current code does. Move vocabulary ownership from `PRODUCT.md`
to `CONTEXT.md` with links and preserved definitions. Start with one glossary; split
only for genuinely distinct domains, not an arbitrary line limit.

Short ADRs can state context, decision, and rationale in one paragraph. Smaller
scope decisions remain in task state. Link knowledge rather than duplicate it.

Use targeted Git searches, commits, diffs, and archived runs to recover what changed
and what was tried. Never invent rationale absent from the evidence. Consult relevant
GitHub issues, PRs, and discussions when available; those are not automatically part
of a clone. GitHub is a first-class integration, while local Git and other remotes
remain possible. Check current branch and working-tree applicability before reuse.

Local continuity must work without tracker setup. Publish or synchronize under
project policy and authorization, retaining one requirements authority. Check related
work before creating tracked items when overlap is plausible.

### Decomposition and execution

Keep a small coherent change as one unit. Use a short checklist for several outcomes,
and separately addressable units when independent tracking or handoffs help. Each
unit should be understandable, verifiable, reviewable, and recoverable with focused
context. Context capacity constrains size but does not determine it alone.

- Prefer narrow, complete outcomes across the layers actually needed. Avoid layer
  splits that postpone integration evidence. Preparatory work is justified when it
  makes the requested change safer or simpler.
- Record real prerequisites and the evidence needed to satisfy them. Check for
  interference in files, shared contracts, and environments before parallel execution;
  dependency readiness alone does not establish safe concurrency.
- For broad migrations, consider introducing a replacement alongside the old form,
  migrating consumers, and removing the old form. Make final integration dependencies
  explicit and use compatibility stages only when needed.
- Give workers the agreement and relevant context, not just an edit checklist.
  Permit necessary checks, routine implementation adjustments, and small refactoring
  that supports the outcome. Record meaningful deviations; return consequential
  scope or contract decisions to the coordinator.

Establish a relevant baseline, make a coherent change, run focused checks, inspect
the result, and continue. Use test-first development where useful for behavioral
changes and bug fixes. Tests should observe behavior at suitable public boundaries
and use independently justified expectations. New-behavior checks must distinguish
incomplete from completed work; regression checks may pass before and after a refactor.
Text presence or occurrence counts alone do not establish functional correctness.

Choose evidence appropriate to code, documentation, configuration, and visual work.
If verification metadata is missing, inspect scripts, CI, and existing tests before
asking the user. Distinguish existing failures, environmental blockers, and new
regressions. Run broader checks required by the change and project policy, repeating
checks when later edits, failures, or unresolved concerns warrant it.
Carry acceptance criteria and relevant testing boundaries through planning,
implementation, and review. Record changes and reasons; consequential reductions
in agreed coverage require the user's decision.

### Independent model review

Use a focused independent result review for small work. Review the proposed approach
before implementing ambiguous or consequential designs; review both approach and
result for complex or risky work. Add integration review when separately completed
units interact through shared state, behavior, or contracts.

Provide a fresh reviewer context with user constraints, the agreement, applicable
project rules, and verification evidence. Pin the baseline and exact changes under
review, including uncommitted edits where needed or a checkpoint under repository
policy. Do not direct reviewers to defend the author's conclusions.

Prefer a separate model where available and useful, including across providers.
Every phase need not switch model or vendor. Where independent review is unavailable,
state the limitation and use the best available check within the user's constraints;
self-review must not be reported as independent review.

**Select perspectives before deciding reviewer count:**

- Start with **Standards** and **Spec**, covering project conventions, maintainability,
  agreed outcomes, scope, and acceptance criteria. Explicitly examine correctness
  and regressions, not only compliance with documentation.
- Add perspectives for concrete risks, such as security, data integrity, or UX/UI.
  One reviewer can cover several perspectives. Separate reviewers need a specific
  question, bounded scope, and a benefit that justifies their cost. Prevent recursive
  review delegation.
- Use **`DESIGN.md` as the design authority**. Prefer suitable external skills for
  UX/UI methods. Supply project guidance and the intended experience; inspect the
  actual interface through screenshots and interaction checks as appropriate.
  UX covers task completion, navigation, feedback, errors, and recovery. UI covers
  hierarchy, layout, typography, consistency, responsiveness, and accessibility.
- Distinguish observed usability problems, documented-rule violations, and subjective
  suggestions. Stylistic preference alone does not block completion. Surface missing
  guidance or consequential design conflicts; record accepted guideline changes in
  `DESIGN.md`. State missing visual or interaction verification honestly.

Validate findings against code, requirements, and observed behavior before fixing.
Use reproductions or traces where practical; failed reproduction challenges the
finding. The coordinator deduplicates and prioritizes by consequence while retaining
perspective and evidence. Record fixes, justified deferrals, and rejected findings.
Recheck affected behavior and invalidate review conclusions when later changes require
it. Review having run does not establish that its findings were resolved.

### Progress, completion, and recovery

Keep these milestones distinguishable without requiring a separate file for each:

| Milestone | Evidence needed |
| --- | --- |
| Ready to execute | Sufficiently defined work, satisfied prerequisites, and authorization. |
| Prerequisite available | The required outcome is verified and accessible to its consumer, with any required review satisfied. |
| Unit complete | Acceptance criteria and required review are reconciled; findings are resolved or explicitly dispositioned. |
| Integrated result verified | Relevant checks and review establish that the combined work satisfies the agreement. |
| Delivered | The requested commit, push, PR, or other delivery action is completed under project policy. |

The coordinator advances dependencies against their stated prerequisites. Unit
completion does not automatically prove integration or delivery. Preserve distinct
implemented, verified, reviewed, committed, and pushed progress, including partial
work. Report conclusions with evidence and remaining limitations.

**Retries must make progress.** Each retry tests a new explanation or responds to
new evidence. Repeated failure without progress triggers diagnosis, a different
approach, or escalation within the user's budget. Do not replace a failed method
with an indefinite review loop. Stop review when actionable findings are resolved
or explicitly dispositioned, relevant checks pass, and uncertainty is recorded;
subjective suggestions do not need to reach zero. User decisions are required for
risk acceptance or scope changes beyond existing authority.

### Compound learning and skill evolution

Preserve the learning loop as a core capability across the whole task, including
small work. Capture candidates when useful discoveries occur, validate them, and
retain only knowledge likely to help future work. An unverified reviewer assertion
is not a lesson. Do not manufacture learning to complete a template.

At task entry, consult the memory index and retrieve lessons matching the work;
reassess relevance when the affected area or problem changes. Check applicability
against current evidence. This baseline must work without hooks; host hooks may
accelerate it. Verify that a later task applies a relevant lesson and avoids the
documented mistake, and that stale or irrelevant lessons do not misdirect the work.

- Route terminology, design guidance, rationale, and operational lessons to their
  authoritative homes. Preserve applicability and links to run artifacts and commits.
- Recognize recurring methods; refine an existing skill or create a focused skill
  when the benefit justifies maintenance. Recurrence is evidence, not an automatic
  skill-creation trigger. A particularly consequential failure can also justify a trial.
- Make learned skills discoverable in later sessions. Keep them project-local by
  default; promote to a shared toolkit or public package deliberately.
- Evaluate skill and routing changes through real runs and retained evidence. Use
  confirmed reviewer misses and false positives for focused evaluation cases. Keep,
  adjust, merge, retire, or revert improvements according to observed results.
- Preserve distinct occurrence counts and idempotent capture. Keep the user's choice
  of autonomous or approval-based skill changes. Memory cleanup remains an explicit,
  proposal-based operation; orchestration does not make it automatic.

The proposed `keep` capability coordinates existing memory and learning behavior.
It must preserve evidence, promotion history, and accepted, reverted, or rejected
trials rather than introduce a duplicate memory system. This improves how agents
use skills and the host; it does not require changing the underlying model runtime.

### Models, providers, and user priorities

**Native orchestration first.** Use the chosen host's subagent lifecycle, messaging,
result collection, and permission mechanisms before building process orchestration.
The user should not manage multiple terminal processes or desktop sessions to complete
one task. An interactive CLI session is a complete primary experience, not a fallback
that requires a desktop app. CLI-to-CLI automation is an optional integration only
when native capabilities cannot meet a justified need; jflow owns its coordination.

Design and validate for Codex and GitHub Copilot desktop apps, and for standalone
Claude Code, Codex CLI, and GitHub Copilot CLI use. These are support targets, not a
claim of tested parity. Discover capabilities by host and version rather than assume
that desktop features, CLI features, or model choices are interchangeable.

Keep core behavior portable, with host-specific adapters where required. Discover
available skills, models, effort controls, delegation, and state access. Support
cross-provider coordination and independent review where integrations permit it;
never require a particular provider or pretend unavailable capabilities were used.
Distinguish a separate reviewer context, a different model, and a different provider.
Cross-provider review is useful when available but is not required for independent
review. Document permission and question handling for foreground, background, and
non-interactive workers; an unattended process may not be able to obtain new approval.
Visual review requires suitable browser, screenshot, or interaction tools in either
interface; a desktop UI or terminal alone does not establish those capabilities.

Save efficiency, speed, quality, or balanced priorities in project state, with
per-task overrides. Honor explicit model choices and budgets.

| Priority | Routing behavior |
| --- | --- |
| Efficiency | Economical models, compact context, fewer handoffs, focused checks and review; accept the user's chosen tradeoff in depth or polish. |
| Speed | Reduce latency and parallelize safe independent work when worthwhile, accounting for extra token use. |
| Quality | Increase reasoning, exploration, verification, and independent scrutiny where they improve the result. |

Escalate effort for ambiguity, difficult decisions, or failed attempts regardless
of activity name. Count coordinator context, calls, review, and retries in the cost.
Distinguish measured usage from estimates. Select for fit, not a claimed guarantee
of optimality, and explain material tradeoffs or limits without requiring routine
model-selection decisions from the user.

### Migration and package scope

Rename `agent-skills` to `j-skills` and `workflow` to `jflow`. Preserve a documented
v2 Git reference. Implement an explicit migration for any renamed files or skills,
retaining content and references rather than maintaining two workflow interfaces.

| Existing assets | Preserve in v3 |
| --- | --- |
| `memory.remember`, `memory.compact` | Learning capture, occurrence tracking, skill promotion, and explicit memory cleanup. |
| `checkup`, `evals` | Real-run health and routing evidence, focused reviewer evaluation, and accumulated cases. |
| `MEMORY.md`, `memory/` | Index, pattern pages, evidence, counts, and promotion history. |
| `.workflow/<slug>/` | Resumable task agreements, progress, decisions, and archived runs. |
| `ROUTING.md`, `WORKLOG.md`, `SKILL-IMPACT.md` | Preferences, run evidence, skill trials, and kept/reverted/rejected outcomes. |

Replace fixed step counts, repeated technical-spec production, blanket execution
restrictions, mandatory per-step commits and resets, and vendor changes at every
phase with the behavioral requirements above. Preserve independent challenge,
verification evidence, Git/GitHub delivery, and learning through that transition.

Supporting names such as `scout`, `shape`, `check`, and `keep` remain proposals,
not required new skills or manual commands. Use a consistent package namespace to
avoid clashes where the host supports it. Reuse existing or external capabilities
when they fit rather than adding helpers solely to mirror this document's sections.

### Implementation choices to validate

Product commitments above are settled direction. Resolve these technical choices
through implementation and focused trials. Treat proposed mechanisms and external
review claims as hypotheses until checked against source files and observed behavior.
Record the claim, test conditions, result, and remaining limitations. Existing v2
instructions establish intended behavior, not proof that it works in v3.

Start with a concise inventory of what is kept, changed, new, or supplied by the
host, linked to implementation evidence. Keep detailed protocols and compatibility
results in supporting implementation records rather than expanding this roadmap.

- First validate minimal task state, stable work references, evidence versioning,
  interruption recovery, and concurrent contributions to shared knowledge. Test
  stale state and uncommitted edits; measure recovery rather than promise a latency.
- Check package loading and skill discovery early in two target hosts. Record tested
  host/version capabilities and the adapters required, including native delegation,
  worker questions, permissions, and explicit behavior when capabilities are absent.
- Define and exercise the reviewer handoff and result format against exact changes,
  including uncommitted edits, and test invalidation after subsequent changes.
- Isolation, integration, and tracker synchronization for concurrent work without
  competing state writers or duplicate requirements.
- Routing defaults, review scopes, and retry controls that meet user priorities
  without excessive coordination or lost scrutiny.
- Test migration for preservation of content and references, idempotence, interruption
  recovery, and a clear change report. Determine safe handling of dirty trees and
  partial migration from these trials; commit layout remains an implementation choice.

### Evidence required before claiming v3 support

Stage validation without weakening the guarantees:

1. Prove the core loop on one host, using the scenarios below to test its claimed
   capabilities. Check a second host early to expose portability assumptions before
   the architecture settles; this is not a claim of full support for that host.
2. Expand verified support host by host. Exercise the core guarantees and host-specific
   integrations in each, including a complete CLI-only experience. Publish tested
   capabilities and limitations; all five target hosts need not gate the first release.
3. Validate optional cross-host recovery separately, with required state access made
   explicit. Switching hosts remains optional for the user.

| Scenario | What must be demonstrated |
| --- | --- |
| Tiny change | Minimal discussion and one compact record; appropriate checks, focused independent review, and durable completion evidence. |
| Ambiguous or consequential work | Decisions resolved in dependency order, approach reviewed when needed, no invented commitments. |
| Fresh-session resume | Recover from saved state without the original conversation, including stale references, partial edits, and truncated tracker responses. |
| Multi-unit work | Dependencies advance from evidence; conflicts are handled; unit, integration, and delivery milestones remain distinct. Separate tasks can contribute shared knowledge without lost updates or duplicate occurrence counts. |
| Review and correction | Detect seeded defects, reject unsupported findings, review the actual changes, and verify fixes without unproductive loops. |
| UX/UI change | Inspect the experience, catch drift from `DESIGN.md`, and distinguish usability defects from preference. |
| Compound learning | Capture once; a later task retrieves and applies the lesson without hooks, avoids the documented mistake, and rejects stale or irrelevant guidance. Retain trial evidence for a skill or routing improvement. |
| One chosen host | Complete delegated work within each supported desktop app or interactive CLI, including a worker question, coordinator resolution or user decision, permission handling, continued work, independent review, and saved state. No manual management of other apps or CLI processes. |
| Host capabilities | Verify available worker models, provider routing, messaging, and visual tools per supported host/version. Exercise unavailable capabilities and denied approvals; preserve blocked state honestly. |
| Multiple setups | Demonstrate start, continue, and fresh-session resume independently in each supported host; test cross-host recovery as an additional portability capability, documenting limitations and fallbacks. |

Use real runs to assess quality, completion time, user interruptions, and coordination
cost, reporting measured usage separately from estimates. These scenarios are release
evidence, not a checklist every user task must execute. Include adverse cases that
could disprove the proposed design; a successful demonstration alone does not prove
reliability. Revise mechanisms when evidence contradicts their expected benefit.

### Example experience and public identity

```text
User: jflow rename Export to Download. Prioritize efficiency.
Coordinator: I'll update the label and check the affected UI.
[Records intent, makes the change, verifies, obtains focused independent review,
 and saves completion evidence within repository policy.]

User: jflow add exports, with quality as the priority.
[Resolves consequential choices, records the agreement, coordinates appropriately
 sized work, and reviews the result using relevant perspectives.]

User, in a fresh supported session: jflow resume
Coordinator: CSV export is verified. Permission handling still needs review.
             Your quality preference and the agreed scope are restored.
```

- **Package:** j-skills is an open-source toolkit of agent skills that keeps your
  development workflow connected—from idea to shipped, across conversations and tools.
- **Workflow:** jflow — an adaptive development workflow, from intent to verified
  results and reusable learning.
- **Continuity:** The project carries decisions and unfinished work so your agent
  can pick them up in the current conversation or a fresh supported session.
- **Learning:** j-skills starts with a workflow and grows with your work. Turn
  recurring work into reusable skills, then improve those skills through use.
- **Tagline:** One project. Any session. Keep your flow. Short: Pick up where you left off.

Publish these as capabilities land, not as claims about v2.

### Design inputs

This target state incorporates the 2026-09-15 review of Matt Pocock's workflow,
adapted to jflow's orchestration, continuity, and compound-learning goals:

| Topic | Source | Documentation |
| --- | --- | --- |
| Discovery and shared language | [grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me), [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) | Reviewed source and domain-modeling references. |
| Agreement | [to-spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md) | [Guide](https://www.aihero.dev/skills-to-spec) |
| Decomposition | [to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md) | [Guide](https://www.aihero.dev/skills-to-tickets) |
| Implementation | [implement](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md) | [Guide](https://www.aihero.dev/skills-implement) |
| Review | [code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) | [Guide](https://www.aihero.dev/skills-code-review) |

