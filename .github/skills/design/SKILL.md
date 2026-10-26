---
name: design
description: >
  Short path for pure UI and UX changes to an existing screen, without a full workflow run: one
  session invents 2-3 design directions as rendered mockups, the human picks or mixes, the same
  session builds it in the real code and screenshots before and after; "design check" then has
  the other vendor look at the screenshots only, with fresh eyes. Hands over to workflow as soon
  as the change needs new data, an API, schema or logic. Run only on an explicit "design SLUG",
  "design check SLUG" or "/design" message; never on casual mentions of design or UI.
---

# design

A **design run** changes how a screen looks and feels, and nothing under it. It costs two
sessions where a workflow run costs five or more, because the human's eyes are the real test
of a visual change: code review, tickets and acceptance lines check things that a pure UI
change does not touch. The **scope gate** below is what makes skipping them safe.

| Command | Session | Does |
|---|---|---|
| `design <slug> - goal: <what should look or feel different>` | 1 · design seat | ground, explore, pick, build, try, commit |
| `design check <slug>` | 2 · fresh-eyes seat, fresh session | reads the screenshots only, reports drift, fixes what the human picks |

Models: the design seat is Anthropic · Opus 5.5 · high; fresh eyes is the other vendor, OpenAI ·
GPT-6.1 Terra · medium (picker ID `gpt-6.1-terra`), chosen for its visual reasoning at about a
tenth of the price. When `workflow/ROUTING.md` has rows named *Design* and *Design check*, those
rows win.

Everything the human reads follows the Rules of the `plain` skill: invoke it once before the
first message. Questions use the workflow's shape: one decision each, lettered options, the
➡️ recommended one first and bold, a reason on every option.

## The run — `.design/<slug>/`

Tracked in git and kept. A separate root from `.workflow/`, so the workflow's state machine and
`check-run.py` never mistake it for a half-finished run.

```
.design/<slug>/
  design.md            the record, ≤ ~40 lines (template below)
  mockups/M1-<name>/   one self-contained index.html per direction; compare.html beside them
  screens/             before-*.jpg, m1-*.jpg, after-*.jpg — each at 1280 and 375 wide
```

## The scope gate

The change is a design run while the diff touches only presentation: markup, styles, layout,
copy, icons, spacing, motion, and component props that only change how something looks. It
leaves alone what data is read or written, API calls, persisted state, validation, routes and
permissions.

Check the gate twice: when a direction is picked, and on `git diff --stat` before the commit.
A change that fails it **hands over**: stop, copy the picked mockup and its screens into
`.workflow/<slug>/prototypes/P1-<name>/` and `screens/`, write the reason in `design.md` with
`Status: handed over`, and end on the workflow's brainstorm card (`workflow brainstorm <slug>`),
naming the prototype as evidence for the decision it already settles. The pick is not
re-asked there.

## Session 1 — `design <slug> - goal: ...`

1. **Ground.** Read the `DESIGN.md` headings and the sections this screen uses; `PRODUCT.md`
   §Vocabulary when copy changes; the screen's own components and styles. Screenshot the
   current screen through the repo's `verify-*` skill (`.agents/skills/verify-*/`), else any
   browser tool this CLI has, at 1280 and 375 wide into `screens/before-*.jpg`. When the app
   cannot run here, ask once for the human's screenshots or start without them, said in
   `design.md`. Done when you can name the screen's tokens (colours, type scale, spacing,
   radius) and the real content it shows.

2. **Explore.** Invent 2–3 directions that differ in idea, not in shade: layout, density,
   hierarchy, grouping, interaction. Each answers the goal in its own way, and one stays close
   to the current design so the cost of change is visible. Build each as static HTML in
   `mockups/M#-<name>/index.html` with the repo's real tokens and real labels and values copied
   from the screen; invented content makes a mockup look better than the product will.
   When this CLI has an image tool and a direction is about mood more than layout, add one
   generated image of it beside the HTML. Screenshot each at both widths into
   `screens/m#-<width>.jpg`, then write `mockups/compare.html`: the before screen and every
   direction side by side, one column each, with a one-line idea under each. Done when every
   direction has both screenshots and passes the floor (below).

3. **Pick.** One question round: the directions as options with their screenshot paths, the
   recommended one first with why it serves the goal best. The human may mix ("b's layout, a's
   density"); restate a mix as one direction before building. Check the scope gate on the
   pick. This turn ends on the question, with no card.

4. **Build.** Apply the pick to the real code, the smallest diff that does it: reuse the
   repo's existing components and tokens; a new token or component is named in `design.md` and
   added to `DESIGN.md` in the same commit. Build the screen's main region first and screenshot
   it before the rest, so a wrong turn costs one region. Then screenshot every screen the diff
   touches into `screens/after-*.jpg` at both widths, check the floor and the scope gate. Done
   when the after screenshots match the pick, and anything that differs is written in
   `design.md` with why.

5. **Try, then commit.** Give the human the start command, route and what to look at. Commit
   code, `DESIGN.md` and `.design/<slug>/` together, `Status: built`, only after they say it
   works. Before a push, scan with `gitleaks git --log-opts="@{u}..HEAD" --redact -v
   --no-banner` and push only on exit 0. End on the card for `design check <slug>`.

## Session 2 — `design check <slug>`

Fresh eyes are worth something only when they have not seen the reasoning. Read `design.md`'s
**Goal** and **Pick** lines, the picked mockup's screenshots, and the before and after
screenshots, and nothing else; leave the code, the other mockups and the rest of
`design.md` closed until the findings are written. Then run `git diff --stat <Base>..HEAD` for
the scope gate.

Report under `## Check` in `design.md`, at most 8 lines, each one of:

- **drift** — the after screen differs from the pick, or changed something the goal did not ask for
- **floor** — a line of the floor fails
- **craft** — spacing, alignment, hierarchy or state that looks unfinished

Each line names the screenshot and the spot on it. Ask which to fix, ➡️ drift and floor first.
Fix the chosen ones, re-screenshot, let the human try it, commit with `Status: done`. A finding
that needs a logic change hands over to `workflow` instead of being fixed here.

## The floor

Every mockup and every after screen meets all of these; a design reason never overrules one.

- Text contrast at least 4.5:1, large text and controls 3:1.
- Every interactive element shows a visible focus state and is reachable by keyboard.
- Motion respects `prefers-reduced-motion`.
- The 375-wide layout has no sideways scroll, clipped text or tap target under 44 px.
- Content is the product's own: labels, values and states as the screen really shows them.
- Empty, loading and error states the screen has still look designed.

## design.md — default template

```
Command: design <slug> - goal: <goal>
Created: <date> · <model>
Base: <sha>
Status: exploring | built | done | handed over
Docs read: DESIGN.md §… · PRODUCT.md §… | none in scope

Goal: <one line, the human's words>
Screen: <route or component path>
Directions: M1 <name> — <idea> · M2 … · M3 …
Pick: M2, with M1's density — <why, one line>
Built: <files changed> · new tokens/components: <names | none>
Differs from pick: <what and why | none>
Floor: pass | <line that fails>

## Check
<written by design check>
```

When the repo has a `WORKLOG.md`, add one line at `done`:
`<date> · design <slug> · <goal> · <sessions> sessions · <models>`.
