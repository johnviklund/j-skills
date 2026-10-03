---
name: understand
description: >
  Human-friendly explainer for a finished workflow run or an area of a codebase: one HTML page
  with plain-English prose, inline SVG diagrams, before/after screenshots
  of every changed screen with unrequested UI changes flagged, decisions, and open questions and
  risks; every claim cites a file:line or commit. Run only on an explicit "understand SLUG" or
  "understand AREA" message, typically after "workflow wrap"; never on casual mentions of
  understanding something.
---

# understand

An **explainer** is a page a human reads to understand work an agent did. The reader is the user
in six months, or a colleague with little context: they know how to code, not this repo. The page
answers three questions: what is this, why does it exist, how does it work. When the work changed
what users see, the page shows it before it tells it, and it shows every visible change, asked
for or not. Every claim is pinned to code, so the page stays honest after its author is gone.

**Invocation:**

| Command | Target | Output folder |
|---|---|---|
| `understand <slug>` | a done `.workflow/<slug>/` run | `.workflow/<slug>/understand/` |
| `understand <area>` | a path, feature or question about the repo | `docs/understand/<topic>/` (`<topic>` = kebab-case of the area) |
| `understand` | — | list the three most recently wrapped runs, lettered, and ask |

The page is `explainer.html` in the output folder; screenshots this skill takes go in its
`screens/`. `<skill>` below is this skill's folder.

## Steps

1. **Resolve the target.** Done when the output folder, the evidence set and the pinned `HEAD` sha
   are named.
   - **Slug:** `brainstorm.md` must carry `Status: done`; a live run routes to `workflow wrap <slug>`.
   - **Area:** resolve it to files with grep/glob. More than one plausible reading: list them
     lettered with a recommended default and ask.
   - An existing explainer is regenerated from scratch; git keeps the old version.

2. **Gather evidence.** Done when every section of the template has evidence, or is marked n/a
   with a reason. The run's artifacts say what was *intended*; code and tests say what *is*: every
   behaviour the page states is seen at a line you can cite.
   - **Slug:** `wrap.md` (outcome, ticket → sha), `brainstorm.md` (problem, behaviours B#,
     decisions, out of scope), `plan.md` (tickets, `## Deviations`, `Base:`), `review.md` (verdict,
     deferrals, `## Resolved`), `learnings.md`, and the file list of `receipts/` and `screens/`.
     Then `git diff --stat <plan Base>..<last shipped sha>` and read the hunks that carry the
     behaviours. This skill reads a done run in full; the workflow's "`wrap.md` alone" rule
     governs later runs' grounding, not this.
   - **Area:** entry points and the path a request or record takes through them; the tests that pin
     the behaviour; `git log --oneline -20 -- <paths>`, traced back past the latest commit
     (`git log --follow`), because the current shape is often several decisions old; done runs that touched it
     (`grep -l '<path>' .workflow/*/wrap.md`, their `wrap.md` only); `PRODUCT.md`/`DESIGN.md` by
     heading, the sections naming the area; `memory/` pages whose `Applies when` matches.
   - **Why, from review** (both): for the commits that shaped the cited code, find their PRs (`(#N)`
     in the subject, or `gh pr list --state merged --search <sha>`) and read the body and review
     discussion with `gh pr view N --json title,body,comments,reviews`. Reviewers often wrote down
     the trade-off the code never states. Cite a PR by its merge commit (`data-sha`) with `href`
     to the PR, so the checker still verifies it. A reason found only in discussion is stated as
     the author's stated intent, not as fact. No `gh`, no remote, or no PR: say "PR discussion
     not searched" under *Open questions & risks*.
   - **Screens changed** (slug): UI files in the run's diff — components, pages, styles, templates;
     tests excluded. Map each to the screen a user reaches and to the B# or ticket that asked for
     it. A visible change no behaviour or acceptance line asked for is **unrequested**.

3. **Pictures.** Done when every changed screen has a before and an after picture, or a stated
   reason for each one missing. Skip this step when no screen changed. Take the cheapest source
   that exists:
   1. The run's own `screens/` (execute saves them per UI ticket): use them as they are.
   2. Capture with a browser tool. *After*: run the app at `HEAD`. *Before*: a worktree at the
      plan's `Base` (`git worktree add $TMPDIR/understand-before <Base>`; reuse the main
      checkout's dependencies when the lockfile is unchanged; another port). Same route, viewport
      1280×800 and data for both; crop to the changed region; JPEG into the output folder's
      `screens/`. Remove the worktree after.
   3. The app cannot run (credentials, live data): leave that side as a *not captured* box and say
      why in the caption.

   Open each picture at most once, to write its caption.

4. **Draw.** Done when 1–3 diagrams are in the page, or the receipt says why there are none. Each
   diagram answers one question the prose asks: what the parts are, the order of steps, who calls
   whom, where data moves, or which states a thing passes through.
   - Hand-write inline SVG with the template's diagram kit (classes listed in its `How it works`
     comment); the template's CSS styles it. Copy the example `<figure>` and grow it.
   - Lay nodes on a grid before writing coordinates: 150×52 boxes, columns 190 px apart, rows
     90 px apart, at most 10 nodes. Keep the `viewBox` at most 760 wide, the page's text column,
     so labels render at full size: that fits four columns, and a longer chain wraps to a second
     row. Edges are straight or right-angled `path`s from box edge to box edge; the main path uses
     `.edge.main`. Labels stay under ~18 characters per line.
   - Give every `<svg>` a `viewBox` that contains all of its shapes, a `width` equal to the
     viewBox width (so it renders 1:1 and shrinks only on narrow screens), and a `<title>`.

5. **Write the page** from `<skill>/assets/explainer.html` into the output folder. Done when no
   placeholder is left and each section meets its line below. Prose follows *Writing* and *Look*;
   every factual claim about code, behaviour or history carries an `a.cite` (markup in the
   template's header comment; permalink base from `gh repo view --json url`).
   - **In short** — three sentences: what it is, what it does for the user, the one thing to keep.
     When screens changed, one of them says how many, and how many were unrequested.
   - **Screens** (only when screens changed) — one figure per changed screen, unrequested ones
     first: tag, before/after pair, one-sentence caption with a cite. Side by side when each crop
     is under ~400 px wide; `.stack` otherwise.
   - **Why it exists** — slug: the brief's problem. Area: its purpose and who relies on it.
   - **How it works** — diagrams, each followed by the prose it illustrates; depth that a first
     read can skip goes in `<details>`. On a UI run the pictures carry the story: keep this to
     one diagram and two short paragraphs.
   - **What changed** (slug only) — before/after in behaviour terms (from the B# list, as shipped),
     then a table of ticket → what it did → commit cite.
   - **Decisions** — from the brief, `## Deviations`, review and PR discussion: the choice, why,
     the rejected alternative.
   - **Open questions & risks** — review deferrals, related `TODO.md` lines, out-of-scope items,
     known fragility, any claim you could not verify, and any doc statement the code contradicts.
   - **Glossary** — every repo term the page uses, `PRODUCT.md` vocabulary first.
   - **Sources** — every artifact and doc read.

   Process history (seats, cycles, who ran what) appears only where it explains a decision.

6. **Verify.** Done when the checker exits 0 and every cite supports its sentence.
   - `python3 <skill>/scripts/check-explainer.py <page> --repo <root>`: fix every `ERROR`
     (placeholders, network-loaded resources, cites to a missing commit, file or line range, broken
     SVG, missing image); fix every `WARN`, except a long sentence whose split would hide a cause
     and its effect.
   - **Fidelity pass:** re-open every cited range and confirm the sentence says what the lines
     show. Correct a claim that fails, or move it to Open questions as "not verified".
   - With a browser tool, screenshot the page at desktop width and look at it against *Look*.

7. **Commit.** `git add <output folder>` only, then commit
   `understand: <slug|topic> — <what it explains>` and push when the branch tracks a remote.
   Leave other dirt in the tree alone.

**Receipt:** path · size · screens (changed / unrequested / pictures missing) · diagrams (count, or
why none) · cites checked · `WARN`s left · commit sha · contradictions found (lettered, routed to
the human) · `open <path>` to read it.

## Writing

Prose follows the Rules of the `plain` skill: invoke it before step 5 and apply every rule. Two additions for this page:

- Put each term the page keeps in the Glossary, `PRODUCT.md` vocabulary first.
- Technical names stay in `code`; the rules apply to the prose around them.

`scripts/check-explainer.py` enforces the rules it can count: 25 words per sentence, six
sentences per paragraph, no em dashes, no parentheses in prose. If those limits change in
`plain`, change the checker's constants in the same commit.

## Look — simple and beautiful

The page is a calm, light document in a Scandinavian report style: white space does the
separating, one blue carries the structure, and colour appears only where it means something.
Keep the template's palette, type and spacing; add no CSS beyond small layout tweaks.

- Colour has one meaning each: blue for titles, structure and the main path; red for a risk or an
  unrequested change; green for what is new or better; gray for everything secondary. Use no
  other colours.
- Prose in paragraphs of two to six related sentences; a run of one-sentence paragraphs reads as
  a list, so make it one.
- Cites are numbered `[n]` in reading order and trail the sentence they support; the `title`
  attribute carries the path.
- Open questions & risks: `.risk` for what can go wrong, `.question` for what is unknown or
  unverified. Red stays rare enough to mean something.
- Diagrams: few nodes, generous space, at most one `.main` node; every label legible at the
  page's width. A diagram that needs a legend is two diagrams.

## Boundaries

- Writes only its output folder. Run artifacts, the run's `screens/`, product docs, `memory/` and
  `TODO.md` stay untouched: a contradiction goes to Open questions and the receipt, and the human
  decides who fixes it (`memory.remember`, `workflow todo`, a doc edit).
- Budget: page ~150 KB, each screenshot ≤ ~400 KB; one explainer per run or topic.
