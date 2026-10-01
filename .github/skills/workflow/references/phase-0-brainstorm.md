# Brainstorm — `workflow brainstorm <slug>` · `workflow improve` · `workflow park`

> ⚠️ Read through the `workflow` skill; the phase ends with its closing card.

Seat: **brainstorm partner** (`ROUTING.md`). The brainstorm is a **grill**: a relentless interview
that ends in a **brief** — `brainstorm.md` — that planning can slice into tickets without asking
the human anything new. Everything plan, execute and review check against starts here, so this
is where "done" gets defined.

## 1. Open the run

`workflow brainstorm <slug>` creates `.workflow/<slug>/`. First run `git check-ignore -q .workflow`;
an ignored folder stops the phase until the ignore rule is removed (runs are tracked history).
No slug → propose a kebab-case one in the first round. An existing slug is that run: resume it if
live, offer to unpark it if parked; a done run is history, so start a new slug.

## 2. Ground before the first question

Read the idea, then the code it touches. When product or UI is in scope, read `PRODUCT.md`/`DESIGN.md`
by heading and open the sections the idea touches, plus vocabulary and principles, so settled
decisions stay settled; read them in full when the idea sets new product direction. Then place the
idea against intake and direction — by heading and `grep` of the idea's key words, not whole files:

- **`TODO.md` answers "already captured?"** Matching item → seed from it, and treat each of its
  details as a claim to re-verify in the code. Related items touching the same feature or files →
  list them in round 1 and ask which fold into scope. A hit in `TODO_ARCHIVE.md` means it was
  already handled — read that line and the run or commit it points to.
- **`ROADMAP.md` answers "already committed?"** Say which: part of a committed item (its scope is
  the boundary), contradicting one (stop — changing committed direction is the human's call), or
  new (say whether it should become a roadmap item or stay intake). A hit in
  `ROADMAP_ARCHIVE.md` means it already shipped.

## 3. Grill in rounds

Treat the idea as a **design tree**: every decision branches into the decisions that hang off it.
The **frontier** is every open decision whose prerequisites are settled. Each round asks the
frontier — up to 5 questions, the ones that most change scope or architecture first — then waits.

```
**Q1 — <title>** <the question in ≤2 plain sentences>
  a) <option>   b) <option>   c) <option>
  ➡️ <recommended answer, one line on why>
```

- **Facts are yours, decisions are the human's.** Anything the code, docs, git or a read-only query
  of the data can answer, look up (a read-only sub-agent may do it) and state as a finding; only ask
  a question whose answer is a choice. Questions downstream of an unfinished lookup wait for a later round.
- **Pin every fuzzy term.** When a word could mean two things ("account", "session", "done"), pin
  it to one meaning, in the code's and `PRODUCT.md`'s vocabulary, and use only that meaning afterwards.
- **Push back** on shaky assumptions and on scope bigger than the need; put 2–3 approaches with
  their trade-offs to the human when the approach itself is open.
- **Play back** an answer in one line before moving on whenever misreading it would be expensive.
- **Write as it settles.** After round 1, open `brainstorm.md` with `Status: drafting` and append
  each decision the moment it is made, so a reset loses nothing.

Settled answers push the frontier outward; recompute it and ask the next round.

Two openings for when round 1 has nothing to grill yet:

- **Blind-spot pass** (unfamiliar territory): first list what an expert here would know that
  nobody has said yet — the unknown unknowns — explain them, then start the rounds.
- **Reference instead of prose** (the human can't describe it but would recognise it): read the
  named file, library or component as the reference for shape and behaviour, then grill how it
  adapts here.

## 4. Close the frontier with outcome, behaviours and seams

When no decision is open, draft the sections planning depends on and put them to the human as
the final round:

- **Outcome** — what the user sees or can do when this ships, on the surface they actually reach
  (a page, a report, an API response, a CLI output). Review checks it there, so name the surface.
  When it depends on real data, state the lookup that shows the data can produce it
  ("5 topics have ≥ 10 countable weekly signals — query in D3").
- **Behaviours** — what will be observably true when the run is done, each one checkable by a
  single test or receipt: `B# — <situation/input> → <observable result>`. Name real values where
  they exist ("a 429 from the provider → the job retries after the Retry-After seconds, max 3 times").
  At least one behaviour asserts something positively present — the new answer, a supported score —
  not only that lineage exists or old text is gone. A behaviour only observable in a live system
  or a hosted console is marked `(live)`; plan gives it an operator ticket.
  5–15 behaviours; more means two runs.
- **Test seams** — the public interfaces where tests will observe those behaviours. Prefer seams
  that already exist; use the highest one that can see the behaviour; fewer is better, one is ideal.

The phase is complete when the human confirms the outcome, behaviours and seams — "shared
understanding" is that confirmation, not a feeling. Too big for one run? Say so, keep this slug to one run's
worth, and recommend `workflow brainstorm <other-slug>` for the rest. Live-operation work splits
naturally at its human gates: build and prove locally in one run, operate and verify live in the next.

## 5. The brief — `brainstorm.md` (≤ ~80 lines)

```markdown
Command: workflow brainstorm <slug>
Created: <date>
Base:    <git sha>
Inputs:  none
Status:  complete

## Problem
<the human's problem, from the user's or caller's side, 1–3 lines>

## Outcome
<what is true for the user when this ships, on the surface they reach (name it), 1–3 lines>

## Behaviours
- B1 — <situation/input> → <observable result>
- B2 — <situation/input> → <observable result> (live)

## Decisions
- D1 — <decision> — <one-clause why> (code: <path> | product call)

## Test seams
- <public interface> — observes B1, B2 (existing | new)

## Out of scope
- <item> — <one-clause why>   (every TODO item considered and excluded, by name)

Docs read: <PRODUCT.md §…, DESIGN.md §… — the sections checked, or "none in scope">
```

Rejected ideas go under **Out of scope** by name; anything left unnamed gets quietly re-imported
by a later phase.

## Improve — `workflow improve <feature> - goal: <goal>`

A brainstorm seeded by a code audit instead of a blank idea: one feature, one pass. Read the
feature's code and list concrete improvement findings (correctness, tech debt, performance,
missing tests, DX), each citing `file:line` and weighed against the goal. Show them as a short
table in round 1 and ask which to pursue. Each chosen finding becomes a behaviour ("<input> no
longer <bad result>; → <good result>"); rejected ones go under Out of scope with the reason. Same
brief, same shape.

## Park — `workflow park [slug]`

Set `Status: parked` in `brainstorm.md` and append under `## Parked`: date, the phase it was at,
what would unpark it. Nothing is deleted; the folder is the idea's home (`TODO.md` keeps only
ideas not yet brainstormed). Park before planning where possible: a parked brief keeps for
months, a parked plan goes stale with the next commit to its files. Unpark with
`workflow <phase> <slug>`; the freshness check decides whether the plan needs redoing. In chat:
`⏸ Parked <slug> at <phase> — <what unparks it>`, then stop. "Good idea, not now" during a
brainstorm parks the run the same way.

Close with the closing card from `SKILL.md` — next is `workflow plan <slug>`.
