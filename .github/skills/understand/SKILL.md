---
name: understand
description: >
  Human-friendly explainer for a finished workflow run or an area of a codebase: one
  self-contained HTML page with controlled-English prose (~80% ASD-STE100), inline SVG diagrams, a
  guided code tour, decisions, open questions and risks, and for a run a before/after view; every
  claim cites a file:line or commit. Run only on an explicit "understand <slug>" or
  "understand <area>" message, typically after "workflow wrap"; never on casual mentions of
  understanding something.
---

# understand

An **explainer** is a page a human reads to understand work an agent did. The reader is the user
in six months, or a colleague with little context: they know how to code, not this repo. The page
answers four questions: what is this, why does it exist, how does it work, where do I start reading.
Every claim is pinned to code, so the page stays honest after its author is gone.

**Invocation:**

| Command | Target | Output |
|---|---|---|
| `understand <slug>` | a done `.workflow/<slug>/` run | `.workflow/<slug>/explainer.html` |
| `understand <area>` | a path, feature or question about the repo | `docs/understand/<topic>.html` (`<topic>` = kebab-case of the area) |
| `understand` | — | list the three most recently wrapped runs, lettered, and ask |

`<skill>` below is this skill's folder.

## Steps

1. **Resolve the target.** Done when the output path, the evidence set and the pinned `HEAD` sha
   are named.
   - **Slug:** `brainstorm.md` must carry `Status: done`. A live run stops here and routes to
     `workflow wrap <slug>`: an HTML file in a live run trips wrap's clean-tree gate.
   - **Area:** resolve it to files with grep/glob. More than one plausible reading: list them
     lettered with a recommended default and ask.
   - An existing explainer is regenerated from scratch; git keeps the old version.

2. **Gather evidence.** Done when every section of the template has evidence, or is marked n/a
   with a reason. The run's artifacts say what was *intended*; code and tests say what *is*: every
   behaviour the page states is seen at a line you can cite.
   - **Slug:** `wrap.md` (outcome, ticket → sha), `brainstorm.md` (problem, behaviours B#,
     decisions, out of scope), `plan.md` (tickets, `## Deviations`, `Base:`), `review.md` (verdict,
     deferrals, `## Resolved`), `learnings.md`. Then `git diff --stat <plan Base>..<last shipped sha>`
     and read the hunks that carry the behaviours. This skill reads a done run in full; the
     workflow's "`wrap.md` alone" rule governs later runs' grounding, not this.
   - **Area:** entry points and the path a request or record takes through them; the tests that pin
     the behaviour; `git log --oneline -20 -- <paths>`; done runs that touched it
     (`grep -l '<path>' .workflow/*/wrap.md`, their `wrap.md` only); `PRODUCT.md`/`DESIGN.md` by
     heading, the sections naming the area; `memory/` pages whose `Applies when` matches.

3. **Draw.** Done when 1–3 diagrams are in the page, or the receipt says why there are none. Each
   diagram answers one question the prose asks: what the parts are, the order of steps, who calls
   whom, where data moves, or which states a thing passes through.
   - Hand-write inline SVG with the template's diagram kit (classes listed in its `How it works`
     comment); the CSS themes it for light and dark. Copy the example `<figure>` and grow it.
   - Lay nodes on a grid before writing coordinates: 150×52 boxes, columns 190 px apart, rows
     90 px apart, at most 10 nodes. Keep the `viewBox` at most 760 wide, the page's text column,
     so labels render at full size: that fits four columns, and a longer chain wraps to a second
     row. Edges are straight or right-angled `path`s from box edge to box edge; the main path uses
     `.edge.main`. Labels stay under ~18 characters per line.
   - Give every `<svg>` a `viewBox` that contains all of its shapes, and a `<title>`.

4. **Write the page** from `<skill>/assets/explainer.html`. Done when no placeholder is left and
   each section meets its line below. Prose follows *Writing* and *Look*; every factual claim about code,
   behaviour or history carries an `a.cite` (markup in the template's header comment; permalink
   base from `gh repo view --json url`).
   - **In short** — three sentences: what it is, what it does for the user, the one thing to keep.
   - **Why it exists** — slug: the brief's problem. Area: its purpose and who relies on it.
   - **How it works** — diagrams, each followed by the prose it illustrates; depth that a first
     read can skip goes in `<details>`.
   - **What changed** (slug only) — before/after in behaviour terms (from the B# list, as shipped),
     then a table of ticket → what it did → commit cite.
   - **Code tour** — 4–8 stops in reading order: entry point first, then the path through the
     code, tests last. Each stop: what to look at, and why it matters.
   - **Decisions** — from the brief, `## Deviations` and review: the choice, why, the rejected
     alternative.
   - **Open questions & risks** — review deferrals, related `TODO.md` lines, out-of-scope items,
     known fragility, any claim you could not verify, and any doc statement the code contradicts.
   - **Glossary** — every repo term the page uses, `PRODUCT.md` vocabulary first.
   - **Sources** — every artifact and doc read.

   Process history (seats, cycles, who ran what) appears only where it explains a decision.

5. **Verify.** Done when the checker exits 0 and every cite supports its sentence.
   - `python3 <skill>/scripts/check-explainer.py <page> --repo <root>`: fix every `ERROR`
     (placeholders, network-loaded resources, cites to a missing commit, file or line range, broken
     SVG); fix every `WARN`, except a long sentence whose split would hide a cause and its effect.
   - **Fidelity pass:** re-open every cited range and confirm the sentence says what the lines
     show. Correct a claim that fails, or move it to Open questions as "not verified".
   - With a browser tool, screenshot the page once in each colour scheme and look at it.

6. **Commit.** `git add <page>` only, then commit `understand: <slug|topic> — <what it explains>`
   and push when the branch tracks a remote. Leave other dirt in the tree alone.

**Receipt:** path · size · diagrams (count, or why none) · cites checked · `WARN`s left · commit
sha · contradictions found (lettered, routed to the human) · `open <path>` to read it.

## Writing — ~80% ASD-STE100

ASD-STE100 is the controlled English of aerospace maintenance manuals. Keep its discipline:

- One topic per sentence: at most 20 words in a procedure, 25 in a description.
- At most six sentences per paragraph, main point first.
- Active voice, present tense: "The loader reads the file."
- One word, one meaning: choose a term per concept, keep it, put it in the Glossary.
- Common words; keep articles; cut filler ("basically", "in order to", "note that").
- A list for three or more steps; a table for a comparison.

The 20% you relax: technical names (in `code`) and domain terms beyond the STE dictionary.

## Look — simple and beautiful

The page is a quiet document, not a dashboard. Keep the template's palette, type and spacing;
add no CSS beyond small layout tweaks.

- Prose in paragraphs of two to six related sentences; a run of one-sentence paragraphs reads as
  a list, so make it one.
- Cites trail the sentence they support; the template styles them as quiet marks.
- One callout per section at most; the `In short` box is the only tinted block in the top half.
  Open questions & risks is the exception: one `.risk` block per item.
- Diagrams: few nodes, generous space, one emphasis colour on the main path; every label legible
  at the page's width. A diagram that needs a legend is two diagrams.

## Boundaries

- Writes only its output page. Run artifacts, product docs, `memory/` and `TODO.md` stay
  untouched: a contradiction goes to Open questions and the receipt, and the human decides who
  fixes it (`memory.remember`, `workflow todo`, a doc edit).
- Page budget ~150 KB; one page per run or topic.
