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
A round is ready to send only when every question in it passed the **prototype test** (§3a):
empirical ones are already answered as findings, and questions of feel carry their variants'
evidence. "I can prototype this if you want" is never a line in a round. A question of feel that
depends on another open question in the round (density before layout) waits for the next round.

```
**Q1 · <title>** <the question in ≤2 plain sentences>
  a) <option>   b) <option>   c) <option>
  ➡️ <recommended answer, one line on why>
```

- **Restate first.** Round 1 opens with **Problem, as I read it**: 2–3 plain lines, in your own
  words, on what is wrong or wanted and for whom: the symptom, who meets it, how to see it. It
  comes before any finding or question, so a misread is caught before it shapes the round. A
  pasted thread, issue or bug report is compressed to that, red herrings dropped. The human's
  guesses about cause or fix are hypotheses: leave them out of the restatement and check them
  like any claim. A correction to it is the first answer of round 1.
- **Facts are yours, decisions are the human's.** Anything the code, docs, git or a read-only query
  of the data can answer, look up (a read-only sub-agent may do it) and state as a finding; only ask
  a question whose answer is a choice. A fact you can only get by running something (how it
  behaves, how fast it is, what it outputs) is still yours: settle it with a prototype (§3a). Questions downstream of an unfinished lookup wait for a later round.
- **Pin every fuzzy term.** When a word could mean two things ("account", "session", "done"), pin
  it to one meaning, in the code's and `PRODUCT.md`'s vocabulary, and use only that meaning afterwards.
- **Push back** on shaky assumptions and on scope bigger than the need; put 2–3 approaches with
  their trade-offs to the human when the approach itself is open, sketched as prototypes first
  when they differ in what a user would see or what you could measure (§3a).
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

## 3a. Settle it with a prototype

A **prototype** is a throwaway sketch that answers one question by observation instead of
debate. Reach for it when a frontier question is:

- **Empirical:** the answer is a fact you could observe by running something: behaviour, timing,
  output, perf, whether a library handles the case. It is yours: build, observe, and state the
  result as a finding. The human never gets the question.
- **A matter of feel:** layout, density, interaction, on-screen wording, where people choose
  better by seeing than by reading. Build 2–3 genuinely different variants, not flavours of one,
  and put the pictures in the question. The human still decides.

Skip it when the codebase already has the pattern, the constraints leave one viable option, or
the question is a product call no experiment can settle.

**The prototype test**, run on each question before a round goes out: is it empirical, or a
matter of feel, with no skip reason above? Then the prototype is built now, inside this round:
build, observe, and send the question with its evidence. Waiting for permission to prototype
costs the human a round and asks the question twice. A prototype needs the run folder, so create
`.workflow/<slug>/` first.

- **One question each.** A prototype's note opens with `P# — <the question it settles>`. No
  question, no prototype.
- **Throwaway and isolated.** Code goes in `prototypes/P#-<topic>/`: the lightest thing that
  shows the answer. For a visual question, static HTML/CSS/JS with CDN dependencies; for a
  behavioural one, the smallest script. No tests, no abstractions, product source untouched.
  Variants sit behind one switcher (buttons or a key), each labelled. When the answer only shows
  inside the real app, sketch on a throwaway branch `proto/<slug>-P#`, collect the evidence, and
  delete the branch, so the run's branch never carries prototype edits.
- **Observe on the matching surface.** Visual: screenshot each variant to
  `screens/p#-<variant>.jpg`, through the repo's verify skill (`.agents/skills/verify-*/`) when
  the sketch runs in the app. With no way to take a screenshot, the question names the file to
  open and the switcher's keys (`open prototypes/P1-density/index.html` · keys 1–3). Behaviour or timing: the printed output, or the measured number
  and how many runs it took. The observation is the test. For a web page, a headless browser is
  the matching surface (`chromium --headless`, `google-chrome --headless`, Playwright): run
  `command -v` for each before calling a measurement impossible.
- **Bounded.** Two attempts that show nothing → report it inconclusive with what it did show,
  and ask the question plainly. At most three prototypes per brainstorm; more means two runs.
- **Recorded.** `notes/P#-<topic>.md`, ≤ 10 lines: the question, the variants, evidence paths,
  the result. The decision it settles is written `(prototype: P#)`. Commit the prototype folder,
  its screens and its note with the brief, so the evidence can be rerun.

A question with pictures keeps the round shape:

```
**Q2 · Row density** The task list can be compact or roomy. I built both (P1).
  a) compact · screens/p1-compact.jpg   b) roomy · screens/p1-roomy.jpg
  ➡️ a, it shows twice as many rows above the fold at 1280×800
```

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
understanding" is that confirmation, not a feeling — and, after `Status: complete` is set,
`python3 <skill>/scripts/check-run.py <slug>` (`<skill>` is the workflow skill's folder) reports no ERROR. Too big for one run? Say so, keep this slug to one run's
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
- D1 — <decision> — <one-clause why> (code: <path> | product call | prototype: P#)

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
`⏸ Parked <slug> at <phase> · unparks when <what unparks it>`, then stop. "Good idea, not now" during a
brainstorm parks the run the same way.

Close with the closing card from `SKILL.md` — next is `workflow plan <slug>`.
