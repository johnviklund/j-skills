# jflow roadmap

**One project. Any session. Keep your flow.**

`j-skills` is the planned open-source package; `jflow` is its main workflow skill.
This document defines the active v3 direction, not capabilities already implemented.
Updated 2026-09-18 following the Jev workflow design discussion.

The previous v3 proposal is [archived separately](archive/v3-adaptive-orchestration-2026-09-18.md).
It is historical context only. This roadmap supersedes it; archived commitments
do not apply unless explicitly retained here.

## v2: maintenance and preservation

Allow small fixes and polish to the existing workflow. Preserve a documented Git
reference for users who want v2 and for migration of its knowledge and history.
The current skill instructions remain v2 until the new behavior is implemented.

## v3: agent-led workflow with Jev decision envelopes

### Product direction

The user works through one conversation with a primary reasoning agent in the user's
desktop app. That agent drives the work: understanding the
user, investigating, reasoning, executing or delegating, and communicating results.

`/jflow` is the workflow entry point and a wrapper around a Jev API helper and the
skills that perform the work. The agent follows the skill to gather project state,
request bounded classifications from Jev, and turn the results into an assignment
or next-step recommendation. A bundled script or connected tool makes the API call.
This design does not require a separate, continuously running controller.

The user can request a command directly or describe what they need, such as
`/jflow implement the next ticket`. The primary agent or a subagent can consult the
same decision helper within an existing assignment. Jev supplies typed judgments;
the primary agent remains responsible for acting on them under the user's direction.

Every outcome includes a next-step recommendation with its reason and any unmet
prerequisites. A recommendation can be to stop because the cycle is complete.
It does not by itself authorize execution of another ticket or workflow stage.

Success means that the user can continue in the same conversation or a fresh
supported session with intent, decisions, evidence, and unfinished work intact.
Small work stays small. Relevant skills and reasoning effort adapt to the work.

### Responsibilities

| Component | Owns |
| --- | --- |
| Human | Goals, priorities, consequential choices, and authorization. |
| Primary agent | Investigation, reasoning, execution or delegation, integration, and communication. |
| `/jflow` skill and helper | Workflow guidance, context assembly, Jev calls, recommendation assembly, skill selection, and durable records. |
| Jev | Bounded classifications, scores, and probability distributions over supplied questions and candidates. |
| Workflow skills | Methods for discovery, specification, planning, implementation, troubleshooting, review, and learning. |
| Project records | Specifications, plans, tickets, decisions, progress, and supporting evidence. |
| Host | Available tools, model and effort controls, worker execution, and permission enforcement. |

The primary agent owns shared task progress. Subagents receive bounded assignments
and return evidence and proposed updates. Their recommendations do not expand scope
or permissions. Verify host capabilities rather than assume that skill invocation,
API access, project files, model switching, and delegation work identically everywhere.

### Commands and outcomes

The public entry point is `/jflow <request>`. The command names below describe
capabilities behind that entry point. They do not require separate public skills or
a fixed sequence for every task. Enter where the available agreement and evidence
support the requested work.

| Command | Purpose and boundary | Durable outcome |
| --- | --- | --- |
| `what` | Help decide what to do next, explore an idea, or improve an existing capability. Investigate facts and interview the human until specification needs are met. Does not create the implementation plan. | Specification on disk or in the repository. |
| `plan` | Turn a sufficient specification into testable work units. Resolve implementation details from available evidence; avoid another routine human interview. | Implementation plan and tickets on disk or in the repository. |
| `implement` | Implement one selected, ready ticket and verify the result. Does not automatically execute the whole plan. | Testable changes, verification evidence, and updated ticket progress. |
| `troubleshoot` | Explain what has been developed, investigate a blocker, or establish how a ticket can proceed. Does not implement a fix or substitute for review. | Evidence-backed diagnosis and, when needed, an updated or new ticket. |
| `review` | Independently assess an implemented ticket or the integrated plan against the specification and project standards. Does not implement fixes. | Findings and their dispositions, a patch plan when needed, and a next-step recommendation. |
| `wrap` | Reconcile the completed cycle, preserve validated learning, and perform authorized cleanup. | Durable completion records and useful lessons for later cycles. |

These commands are available at any point:

| Command | Purpose |
| --- | --- |
| `status` | Report agreed, implemented, verified, reviewed, blocked, and delivered work. |
| `next` | Recommend the next action from current intent, priorities, and evidence. |
| `todo` | Capture and organize possible work without silently adding it to the active agreement. |
| `learn` | Capture or evaluate a lesson without waiting for the cycle to finish. |

Discovery stops when the next work is sufficiently defined. Planning normally uses
the settled specification; a newly discovered consequential product decision returns
to the human instead of becoming an invented implementation assumption. A diagnosis
may explain the situation without requiring any new ticket.

### Specification, plan, and ticket boundaries

The specification owns the problem, intended outcomes, user stories or concrete
scenarios, acceptance criteria, constraints, exclusions, and settled product decisions.
The plan references that agreement and owns implementation decisions, dependencies,
testing decisions, and the tickets needed to deliver it. Avoid duplicate requirements.

Each implementation step must be testable. A ticket represents a coherent, verifiable
outcome, potentially across several files or layers. Include the relevant agreement,
prerequisites, verification requirements, and stopping conditions. Small work can
share one compact file for specification, plan, and ticket state.

Approval applies to an identifiable plan or ticket and scope. A completed document,
a classification, or an agent-generated request does not grant execution authority.
Keep implementation, verification, independent review, and delivery distinguishable.

### Decision envelopes

A decision envelope is the durable record connecting a request, the classifications
used to interpret it, the recommended action, and what the agent actually did.
Separate these concepts:

| Part | Meaning |
| --- | --- |
| Intent | What the human, primary agent, or subagent requested, including the source. |
| Recommendation | What Jev's judgments and jflow's rules suggest doing in the current state. |
| Execution | What the agent accepted or overrode, what it did, and the resulting evidence. |

For an explicit command, record intent directly. For a conversational request, Jev
can classify intent. In either case, preserve the original request. For example,
the intent may be `implement` while the recommendation is to resolve a blocker
because no ticket is ready. Do not silently replace the user's requested outcome.

The envelope records:

- A stable decision identifier, time, initiating actor, original request, and task
  or ticket reference. Link the existing authorization and scope separately.
- The exact context sent to Jev and its project-state revision, including relevant
  uncommitted work. Mutable file paths alone do not identify the evaluated state.
- The question definitions, policy, skill catalog, and resolved model versions.
- The request and raw response, including probabilities and reported confidence,
  or the failure when no answer was obtained.
- The assembled recommendation and the rules that produced it. Distinguish model
  outputs, computed facts, and the primary agent's interpretation.
- The action accepted by the primary agent, any override and its reason, and links
  to execution, verification, and review evidence.

Save the request before calling Jev and the raw response before interpreting it.
Append the outcome without overwriting the original decision evidence. Record a
failure or fallback honestly. Reconcile changed project state before acting on an
older recommendation. Traceability supports investigation and evaluation; it does
not guarantee that another API call will reproduce the same probabilities.

Keep API credentials out of records. Choose storage, retention, and repository
publication rules for request context explicitly; project traceability need not
publish every raw payload. Link private evidence where appropriate.

### Reusable JSON definitions and the API helper

Maintain versioned JSON definitions that the helper combines with current project
facts to construct Jev's `state` and `questions` request. The library contains:

| Definition | Contents |
| --- | --- |
| Question templates | Intent categories, skill relevance, task difficulty, learning value, and escalation signals, with explicit criteria. |
| Workflow actions | Required inputs, prerequisites, expected outputs, and stopping conditions. |
| Skill registrations | Skill location and version, supported capabilities, required context, outputs, invocation rules, and side effects. |
| Routing policies | Human priorities, model preferences, budgets, thresholds, and fallback behavior. |

The primary agent supplies current facts and candidates. Reuse established questions
instead of asking it to invent the full classification scheme on every call. Populate
candidate options from actual eligible tickets, installed skills, and available host
capabilities. Keep complete skill instructions in their source files.

The helper validates the response and combines the answers into guidance the agent
can follow. Jev returns typed selections and scores; it does not generate arbitrary
implementation briefs. Assemble the assignment from the selected action, ticket,
context, skill registrations, and policy.

Batch questions that use the same state. Use another call when an earlier answer
determines the evidence or candidates needed for a later judgment. Keep exact
computations, dependency checks, and permission enforcement outside the classifier.
If one eligible ticket is already determined by the plan, do not require Jev to
rediscover it. Allow no suitable candidate and uncertain outcomes.

### Where Jev advises the agent

| Decision | Jev's contribution | What constrains the action |
| --- | --- | --- |
| Next action or ticket | Classify intent and assess suitable eligible work. | Explicit requests, dependencies, current evidence, and authorization. |
| Model and effort | Assess reasoning demands, ambiguity, and relevant risks. | Human policy, budget, host capabilities, and measured model performance. |
| Skills and context | Rank relevant methods and records; reject unsuitable matches. | Actual skill instructions, applicability, and explicit selections. |
| Delegation | Assess bounded proposed assignments for specialization, missing context, or overlap. | The primary agent's decomposition, resource conflicts, and host execution limits. |
| Human escalation | Flag consequential ambiguity or unresolved choices. | Missing information or authority; confidence cannot supply permission. |
| Learning | Assess novelty, applicability, recurrence, and likely reuse. | Supporting evidence and validation before retention or skill changes. |
| Evaluation | Assess individual rubric criteria, findings, and completion claims. | Tests, evidence inspection, and independent review where required. |

Consult Jev at meaningful boundaries, such as selecting work, encountering a blocker,
preparing review, or evaluating a lesson. Dynamic configuration means selecting
compatible skills, context, tools, and execution settings for an assignment. Novel
plans, instructions, and code remain work for the reasoning agent.

Jev's confidence describes its output distribution. Calibrate routing thresholds
against actual workflow outcomes; do not interpret a confidence value as a proven
accuracy rate. Schema validity does not establish correctness or review independence.

### Replaceable workflow skills

Keep public intent and workflow outcomes stable while allowing different skills to
provide the methods. `/jflow implement the next ticket` can use a local implementation
skill or a compatible external skill through its registration.

The [AI Hero skill catalog](https://www.aihero.dev/skills) is one source of candidates:
`grill-with-docs` for discovery, `to-spec` for specification, `to-tickets` for planning,
`implement` for implementation, `code-review` for review, and `diagnosing-bugs` for
diagnosis. These are candidate mappings, not adopted or tested integrations.

Check compatibility beyond the skill name. A skill may require direct human invocation,
commit changes, include its own review, use a tracker, or leave ticket completion to
the caller. The registration must describe those behaviors. Adapt the integration or
choose another skill when it conflicts with jflow's scope, authorization, or outputs.
Validate actual result artifacts before updating shared progress. Changing a JSON
mapping alone does not establish compatibility.

### Continuity, review, and learning

Persist decisions and progress as they occur, including partial work and blockers.
Recovery must work from project records and current files without the original
conversation. The envelope explains a decision; task records and actual evidence
establish current progress. Reconcile them when resuming.

Independent review examines the agreed scope and exact changes, including uncommitted
edits when relevant. Record the reviewer context and evidence covered. Self-review
and Jev rubric scores must not be presented as independent implementation review.
Later changes may invalidate earlier conclusions. Resolve or explicitly disposition
findings before claiming completion, and review integration when tickets interact.

Capture candidate lessons during work. Validate them before retaining them with their
applicability and evidence. `/jflow learn` can run anytime; `/jflow wrap` reconciles
the cycle and consolidates useful learning. Evaluate skill and routing changes through later runs,
preserving accepted, adjusted, reverted, and rejected outcomes.

### Example: implement the next ticket

1. The user asks `/jflow implement the next ticket` in the primary agent's conversation.
2. The agent loads jflow and reads the active agreement, plan, ticket state, and policy.
3. The helper identifies eligible tickets and consults Jev where judgment is needed.
4. It stores the decision evidence and assembles the assignment: action, selected
   ticket, relevant specification, skills, verification, and stopping conditions.
5. The primary agent reconciles readiness, loads the methods, and executes directly
   or delegates within the authorized assignment and available host capabilities.
6. It saves the result and reports a next-step recommendation, for example:
   "T-04 is implemented and its checks pass. Independent review is pending.
   Recommended next step: `/jflow review T-04`."

### Implementation and validation priorities

The architecture above is the active direction. Exact schemas, file layout, helper
transport, thresholds, and host integrations remain implementation choices to test.

1. Define the decision envelope and one `implement_ticket` skill registration.
   Exercise `/jflow implement the next ticket` through selection, execution evidence,
   and the next recommendation on one host.
2. Implement reusable question definitions and a bounded API helper. Verify trace
   persistence, response validation, and behavior on unavailable or uncertain answers.
3. Test a compatible external skill mapping, including invocation restrictions,
   side effects, review behavior, and result reconciliation.
4. Prove interruption recovery, stale-state handling, blocked tickets, changed scope,
   and subagent contributions without competing shared-state writers.
5. Compare simple rules, reasoning-agent judgment, and Jev-assisted decisions on
   representative and held-out cases. Measure wrong routes, unnecessary delegation,
   serious misses, user interruptions, end-to-end time, and total cost.
6. Expand supported hosts after verifying access to files, the API helper, skills,
   permissions, and any claimed delegation or model controls. Desktop and CLI use
   are portability goals; no specific app/model combination has validated v3 support yet.

Include explicit commands, ambiguous prompts, no eligible ticket, inappropriate skill
matches, misleading input, API failures, and successful completion in validation.
Use retained outcomes to improve questions and policies. Do not claim that Jev makes
routing optimal or that a vendor benchmark establishes performance on this workflow.

### Migration and package scope

Retain the planned `agent-skills` to `j-skills` and `workflow` to `jflow` naming change.
Migrate existing agreements, progress, memory, reviewer evaluation cases, routing
preferences, worklogs, and skill-trial history with content and references preserved.
Make renamed paths and changed command behavior explicit. Keep v2 available through
its documented Git reference rather than silently changing existing runs.

This roadmap change documents direction only. It does not install Jev, register
external skills, implement the helper, or replace the current execution instructions.

### Design references

- [TypeSafe introduction](https://docs.typesafe.ai/introduction): state and typed judgments.
- [API reference](https://docs.typesafe.ai/api): request and response shapes.
- [Primitives](https://docs.typesafe.ai/primitives): atomic questions and dependencies.
- [Confidence](https://docs.typesafe.ai/confidence): distributions and routing thresholds.
- [Skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion): candidate ranking and rejection.
- [Model limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13): constraints to test against.
- [AI Hero skills](https://www.aihero.dev/skills) and [implementation behavior](https://www.aihero.dev/skills-implement): external methods and integration boundaries.

## v4: later, if needed

Reserve for needs that emerge from using v3. No committed scope yet.
