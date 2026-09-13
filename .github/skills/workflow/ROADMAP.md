# jflow roadmap

**One project. Any session. Keep your flow.**

`j-skills` will be the open-source package, with `jflow` as its main workflow skill.
The supporting skills will serve the same connected development workflow.

## v2 — Small improvements

- Leave room for minor additions, fixes, and polish to the current workflow.
- Add specific items here as needs arise.
- Keep v2 available through a documented Git tag or commit for users who want
  the existing manual workflow.

## v3 — Agent orchestration with continuous context

Build the best coordinated workflow around an agent running `jflow`. The user
provides intent and priorities; the orchestrator manages planning, execution,
verification, memory, and learning through the supporting skills.

### Product focus

- Make orchestration the primary v3 experience. The agent chooses and coordinates
  the steps, models, effort, and handoffs within the user's instructions.
- Keep the user able to steer, pause, and resume through the same conversation.
- Design supporting skills as focused capabilities for the orchestrator to use.
  A separate manual mode, standalone commands for every helper, and compatibility
  with v2's manual command sequence are outside v3's scope.
- Preserve v2's knowledge and useful capabilities as the foundation. Preserve a
  v2 Git reference for the old experience instead of maintaining two workflows in v3.
- Use the host's execution capabilities and add integration code where needed to
  make orchestration reliable. Limited delegation can mean the coordinator executes
  a step itself; the user should not have to manage routine handoffs.

### Core experience

- **Stay in one conversation.** Direct the work and review results in one thread,
  while jflow coordinates the helper skills and supported agents underneath.
- **Resume in a fresh session.** Open a CLI at any time and pick up the objective,
  decisions, progress, unfinished work, and next steps.
- **Carry context with the project.** Keep durable state that supported tools can
  read and update, so continuity does not depend on conversation history alone.
- **Use Git as memory.** Let agents retrieve relevant commits, diffs, and tracked
  project knowledge to recover context and ground decisions in prior work.
- **Grow through use.** Build on the existing workflow's learning behavior to turn
  recurring work into reusable skills and improve those skills through use.
- **Support the user's setup.** Design for desktop apps, CLIs, and combinations
  chosen by the user. Resume across tools when they can access the project's state.
- **Establish the public identity.** Rename the root package and repository from
  `agent-skills` to `j-skills`, and the workflow skill from `workflow` to `jflow`.
  Keep the package focused on jflow and its supporting skills.

Success means returning in the same thread or a new supported session and
continuing without manually reconstructing context or managing routine handoffs.

### Setup independence

As an open-source package, `j-skills` should adapt to the user's choice of tools,
providers, and models. Avoid requiring a particular app, CLI, or combination.

- Keep the core workflow portable and consistent, with host-specific setup and
  integrations where needed.
- Adapt skill invocation, project-state access, delegation, model selection, and
  effort settings to the capabilities available in each host.
- Keep state and routing preferences scoped to the relevant project or environment.
- Validate the core start, continue, and resume experience for supported hosts;
  document capabilities, limitations, and fallbacks without assuming feature parity.

### Git and GitHub as project memory

Git-backed history and GitHub integration are core capabilities carried forward from
v2. The primary purpose is to give agents a durable, inspectable memory source across
sessions: what changed, what was tried, and the recorded reasons behind decisions.

- **Retrieve relevant history.** Use targeted history searches, commits, diffs, and
  archived runs to investigate prior work without loading the entire history.
- **Preserve the reasons.** Keep plans, decisions, memory pages, learning evidence,
  and run progress tracked alongside code. Diffs show changes; recorded rationale
  explains intent. Do not invent reasons when the history does not establish them.
- **Connect memory to evidence.** Link lessons and learned skills to relevant run
  artifacts and commits so later agents can inspect their origin and applicability.
- **Use GitHub context.** Consult relevant PR descriptions, review discussions, and
  issues through the available integration. These complement local Git history and
  are not automatically included in a clone.
- **Check current applicability.** Compare historical findings with the current
  branch and working tree before reusing them; preserve superseded decisions as history.
- **Keep curated memory useful.** Let `memory.remember` capture reusable lessons and
  point to Git evidence, while agents consult history for detail as needed.
- **Keep GitHub delivery.** Preserve checkpoint, commit, push, and PR workflows under
  the user's repository policy. Distinguish local, committed, and pushed progress.

Moving between machines is a secondary benefit of synchronizing code, tracked
context, and any separate skill repositories. Local Git memory also works without
a remote; GitHub is a first-class integration, while other remotes remain possible.
Track this roadmap in Git so it is available when planning and developing v3
from another checkout.

### Coordinator and user priorities

The user talks to a capable coordinator, such as Astra, running `jflow`. The
coordinator selects supporting skills, available models, and reasoning effort,
then brings results back into the same conversation. Model names are configurable;
the workflow should not depend on one specific coordinator model.

- **Follow the user's priority.** Support token efficiency, speed, quality, or a
  balance. Save the preference in project state, with per-task overrides.
- **Efficiency:** Favor economical models, lower effort, compact context, fewer
  handoffs, and focused checks. Accept less depth or polish when the user prefers
  that tradeoff; do not silently default to maximum quality.
- **Speed:** Favor low latency and parallel work where it reduces completion time,
  recognizing that parallel work can spend more tokens.
- **Quality:** Spend more on reasoning, exploration, and independent review where
  they improve the result.
- **Adapt to the task.** Use stronger models or more effort for ambiguity, difficult
  decisions, or failed attempts. Keep straightforward work economical. Avoid retry
  loops that erase the savings of a cheaper model.
- **Count coordination too.** Include the coordinator's context, calls, and review
  work when assessing efficiency. Delegate when the benefit justifies the overhead.
- **Respect constraints.** Honor explicit model choices and budgets. Distinguish
  measured usage from estimates; explain material tradeoffs or budget limits.
- **Work within the host.** Discover available models and effort controls. Where
  delegation or model selection is unsupported, continue with the current model
  and state the limitation without pretending a switch occurred.

The user sets intent and priorities; routine routing should not require choosing
a model for every step. Selection aims for the best fit, not a guarantee of an
optimal choice.

### Learning and skill evolution

The bundled skills are a starting point. Carry the existing learning behavior into
v3 so project knowledge, reusable methods, and routing decisions improve over time.
This improves how the workflow uses the host's harness; it does not require changing
the underlying runtime.

- **Remember:** Capture useful decisions, lessons, and evidence from completed work.
- **Recognize:** Identify recurring patterns that contain a reusable method.
- **Create or refine:** Improve an existing skill when it fits, or create a focused
  new skill when it would save future work or prevent recurring mistakes.
- **Reuse:** Make learned skills discoverable to the coordinator in later sessions.
- **Evaluate:** Use observed results to keep, adjust, merge, or retire skills.
- **Scope:** Keep learned skills local to the project by default. Promote useful
  ones deliberately into the user's shared toolkit or the public package.

The proposed `keep` entry point coordinates the existing learning capabilities;
it should reuse their behavior rather than introduce a duplicate memory system.
For example, repeated database migrations could produce a project-specific migration
skill that jflow discovers and uses on the next migration. Repetition alone does not
justify another skill; the extracted method should offer a clear benefit.

### Carry forward from v2

v3 evolves the current workflow. Existing companion capabilities, accumulated
knowledge, and run history are the foundation. Their names and invocation patterns
can change to serve orchestration; preserving the manual interface is not required.

| Existing capability | Role in v3 |
| --- | --- |
| `memory.remember` | Continue routing lessons, counting distinct occurrences, and creating or refining skills from reusable patterns. |
| `memory.compact` | Retain explicit, proposal-based memory cleanup; a coordinator does not make cleanup automatic. |
| `checkup` | Retain health checks and evidence from real runs for judging model and skill changes. |
| `evals` | Retain the focused reviewer evaluation and accumulated cases. |
| `MEMORY.md` and `memory/` | Preserve the index, pattern pages, evidence, occurrence counts, and promotion history. |
| `.workflow/<slug>/` | Preserve resumable run artifacts and archived runs. |
| `ROUTING.md`, `WORKLOG.md`, and `SKILL-IMPACT.md` | Preserve routing preferences, run evidence, skill trials, and kept/reverted/rejected outcomes. |

Keep the user's autonomous-versus-approval choice for skill changes. Keep repeated
learning capture idempotent and retain trial evidence before accepting improvements.
Any renamed skill or changed file layout needs an explicit migration that preserves
existing content and references. Proposed helper names describe the future interface;
their mapping to current companion skills remains a design decision.

### Example interaction

Illustrative v3 behavior, not an implemented command contract:

```text
User: jflow add dark mode. Prioritize token efficiency.
Coordinator: I'll use a focused plan and economical implementation and checks.
             I'll increase effort if a blocker needs it.

[Selects helpers and models, implements, checks, and saves project progress.]

User: This part is tricky. Prioritize quality for the theme migration.
Coordinator: I'll use deeper reasoning and an independent review for that part.

[Later, in a fresh session with access to the same project state.]

User: jflow resume
Coordinator: Dark mode is implemented. The migration review is next.
             Your default is token efficiency; the migration has a quality override.
```

### Descriptions to keep

**Package description**

> j-skills is an open-source toolkit of agent skills that keeps your development
> workflow connected—from idea to shipped, across conversations and tools.

**Main skill description**

> jflow coordinates planning, building, reviewing, and learning, helping you
> continue the same work in one conversation or a fresh session.

**Short workflow description**

> jflow — a five-phase development workflow, from idea to lessons learned.

**Learning description**

> j-skills starts with a workflow and grows with your work.
> Turn recurring work into reusable skills, then improve those skills through use.

**README opening**

> Keep a conversation going all week, or open a fresh terminal tomorrow. jflow
> helps your agent pick up the plan, decisions, and unfinished work so you can
> keep building.

These describe the intended v3 experience; publish them as capabilities land.

### Tagline ideas

- **Lead:** One project. Any session. Keep your flow.
- **Short:** Pick up where you left off.
- Keep your context. Keep your flow.
- Your development workflow, connected.
- **Single-thread feature:** Stay in one thread. Keep building.
- One conversation, from idea to shipped.
- A full toolkit. A continuous conversation.

### Supporting skill names

Use `j-skills` as the shared package identity, `jflow` as the user-facing entry point,
and short, consistent names for the orchestrator's supporting skills. These are
naming ideas, not a committed list of new skills or standalone user commands.

| Skill | Role |
| --- | --- |
| `jflow` | Guides the work from start to finish and coordinates supporting skills. |
| `scout` | Explores the codebase and gathers context. |
| `shape` | Turns an idea into an actionable plan. |
| `check` | Reviews and verifies the result. |
| `keep` | Coordinates existing memory and learning skills to capture lessons and develop reusable skills. |

Where a host supports namespacing, names such as `j-skills:scout` and
`j-skills:check` can make package membership clear. Otherwise, consider
`jflow-scout`, `jflow-shape`, `jflow-check`, and `jflow-keep` if bare names would
clash with other installed skills. Keep one convention across the helpers.

## v4 — Later, if needed

- Reserve for needs that emerge from using v3.
- No committed scope yet.
