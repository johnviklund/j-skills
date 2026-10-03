# Learning loop & Worklog — `workflow learn` / `workflow log`

> ⚠️ Read through the `workflow` skill; the command ends with its closing card.

## Learning loop — `workflow learn`

Commits save *what* changed; `MEMORY.md`, skills, and `DESIGN.md` save *why*. This is the point
of the workflow, not an afterthought: **solve a real problem → remember it. Do the same kind of
thing 3+ times → turn it into a skill.**

Append one line per learning to `.workflow/<slug>/learnings.md` before any reset, and
any time something worth keeping gets solved — don't wait for wrap-up:

```text
## Phase N — <name> (YYYY-MM-DD)
- [durable→memory] <the fix, gotcha, or decision>
- [durable→skill] <the transferable principle, stripped of concrete schema/names/logic>
- [durable→design] <the UI pattern/convention/token decision>
- [durable→eval] code-review — <the P0/P1 that was missed, and by whom> (artifacts: the diff + the finding)
- [drop] <one-off noise>
```

### `[durable→eval]` — a small reviewer exam, and nothing else

Models earn seats on **trial runs**, not exams (protocol in `ROUTING.md`): a candidate takes a
seat for a real run, and the worklog's `Run:`/`Seats:` lines are the evidence. The one exception
is the strict reviewer, because a reviewer miss is expensive and a diff with known findings is a
cheap, honest exam. So the only case shape is `code-review`, filed in the exam set (`j-skills-evals/strict-reviewer/`, a private repo cloned beside j-skills; the `evals` skill says how to find it):

| Case shape | Seat directory | Input → what a pass must name |
|---|---|---|
| `code-review` | `strict-reviewer` | a self-contained diff → the confirmed P0/P1 findings in it, one line each |

**Admission test:** a case is deposited only when a P0/P1 was *missed by the writer and caught by
the reviewer*, or *missed by the reviewer and caught later* (the most discriminating kind — file it
when the miss surfaces, even in a later run). Routine findings teach nothing. Seeded cases
(a planted slip in a shipped diff) fill the set until real misses arrive; a missed case
outranks them. **Cap: 10 cases, rolling** — when full, a new case displaces the oldest seeded
one first, then the weakest; never append past the cap. There are no spec, plan, or mechanical sets: an approved
plan or spec is not a reusable exam, and those seats prove themselves on trial runs.

Tag the line `[durable→eval] code-review — <what was missed, by whom>` any time during the run;
wrap performs the deposit (see `references/wrap.md`).

### `[durable→memory]` — pattern pages, not a flat list

Repo memory is a folder: **`MEMORY.md` is the index** (one line per page: `- [<slug>](memory/<slug>.md) — <one-line claim> · occurrences N · <last confirmed>`), and **each durable pattern is a page in `memory/<slug>.md`**. A page is small and always the same shape:

```markdown
# <claim in one line>
Applies when: <the situation that should trigger recall>
Root cause: <why it happens — one or two lines>
Fix: <what to do — concrete, with paths or commands where they exist>
Evidence: <run slug or sha> · <run slug or sha>          ← one entry per occurrence
Occurrences: N · Last confirmed: YYYY-MM-DD · Status: active | superseded by <slug>
```

A repeat is not a new page: `memory.remember` finds the existing page by claim, appends the run
slug as an evidence entry — once per run, never twice — bumps `Occurrences`, updates `Last
confirmed`, and marks the learnings line `[routed → …]` so a second pass skips it. That count is what makes the
second-occurrence review tag mechanical, and `Occurrences: 3` is the signal to consider a skill
(`[durable→skill]`) — the page then records `Promoted to: <skill>` and stays as the why. Pages
never move into `.workflow/`; they are canonical docs and follow the canonical-doc edit rules.

Then invoke `memory.remember` (a sibling skill in this same repo) to actually route each line —
any time, not only at wrap-up. It reads `MEMORY.md`/`memory/`/`AGENTS.md`/`README.md`/`DESIGN.md`/
every existing skill's frontmatter *and every installed plugin's skill names* before deciding a
destination, so it won't create a skill that collides with one you don't own. For periodic
`memory/` cleanup, invoke `memory.compact` manually — it never runs on its own.

### `[durable→skill]` — logged, then trialed, never just applied

A change to a skill is gated the same way a model is: on the runs after it. `memory.remember`
applies the edit in its own commit (never mixed with code) and adds a line to the skills repo's
`SKILL-IMPACT.md` (`<date> · <skill> · <what changed> · from: <memory page> · trial until: <N runs>`).
The next N worklog entries carry `Skills: <skill>@<sha>` so `checkup` can compare `Run:` numbers
before and after; worse means revert the commit and log the reversal in the same file. A change
considered and rejected is logged there too, so it is not re-proposed.

## Worklog — `workflow log`

A small, **bounded, rolling** `WORKLOG.md` at the repo root: a newest-first index of what was
built or changed, so any session can backtrack development quickly. It is deliberately **not** a
source of truth and **not** an archive — git is the source of truth for *what* changed, and the
repo's canonical docs (`PRODUCT.md`/`DESIGN.md`/`AGENTS.md`) own *what we're building*.
`WORKLOG.md` only **points into git**; the diffs live in the commits.

**Anti-bloat is the whole point**: the file is
capped and rolls off. Never let it grow into a second memory file that confuses future sessions.

- **Cap:** keep roughly the **15 most recent entries** (about one screen). Before appending, if
  there are already ~15 `## ` entries, **delete the oldest ones** — they are preserved forever in
  git history of the file and in the commits they cite. Rolling off is deletion, not archival.
- **Entry = pointer, not payload.** One entry per unit of work (a workflow run, or an ad-hoc
  session). Shape:

  ```markdown
  ## YYYY-MM-DD · <run slug> · <one-line what> · <model>
  - <1–4 terse bullets: what shipped / changed>
  - Commits: <sha> <sha> ... (+ <other-repo> <sha> if it spanned repos)
  - Review: <verdict> @ <reviewed sha>   (workflow runs only — omit when no review ran)
  - Run: <tickets> tickets · <cycles> review cycles · <deviations> deviations · <overturned> findings overturned   (workflow runs only)
  - Seats: 0 <model> · 2 <model> · 3 <model> · 4 <model>   (workflow runs only — brainstorm · plan · execute · review; suffix "(trial)" where a trial model ran)
  - Skills: workflow@<sha>[, <other skill>@<sha>]   (workflow runs only — the skill versions that ran, so a skill change can be judged like a model)
  - Why: <one line>
  ```

  For a completed `workflow realign` evidence review that accepted no redline, the entry may use
  `Commits: none — docs confirmed current`; omit `Review:` because this is not a standard workflow run.

  The `Run:` and `Seats:` lines are how models are evaluated: read the numbers from `plan.md`
  (ticket count, `## Deviations`, `Writer:` lines) and `review.md` (`## Cycle N` count,
  dispositions marked wrong-by-human) at wrap, so `checkup` can compare a candidate's runs on a
  seat against the incumbent's without opening every archived run folder.

- **When it's written:**
  - `workflow wrap` appends an entry automatically as part of wrap-up.
  - `workflow log` appends one on demand for an **ad-hoc session that didn't run the full
    workflow** (like a quick fix or a review). Same shape, same cap. This is what keeps the log
    complete instead of only capturing formal runs.
- **Never** paste diffs, file dumps, rationale essays, product/design decisions, or learnings
  into it. Learnings go through `memory.remember`; product/design go to their canonical docs;
  detail lives in git and the session store. If an entry needs more than ~4 bullets, it's too
  much.
- If `WORKLOG.md` doesn't exist yet, create it with a one-line header explaining it's a bounded,
  rolling, git-pointing index, then add the first entry.
