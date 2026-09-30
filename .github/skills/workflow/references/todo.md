# TODO intake — `workflow todo [idea]`

> ⚠️ Read through the `workflow` skill; the command ends with its closing card.

Seat: **brainstorm partner** at medium effort — mapping in `ROUTING.md`. Rationale: this is
knowledge-shaped intake dialogue with no execution payoff — the same seat as brainstorm, and
it's a quick command; never spend a heavy or reviewer seat on it. Runs anytime, in any
session — it doesn't read or change `.workflow/` state.

Capture the idea into repo-root `TODO.md` well-placed and well-shaped — intake only, never the
start of implementation. `TODO.md` holds ideas *not yet brainstormed*; an idea that has been
brainstormed lives as a `.workflow/<slug>/` run (live or parked) and is not listed here twice.
Check `grep -l 'Status: parked' .workflow/*/brainstorm.md` before adding: a match means "that's
parked as `<slug>` — unpark it or leave it," not a new item. If the idea is clearly run-sized and
the human wants it now, offer `workflow brainstorm <slug>` instead of an intake line.

**1. Read before writing.** Read `TODO.md` in full (if missing, create it with a short header
stating it's the human's intake scratchpad, not a roadmap). If the idea touches product
direction, skim the relevant `PRODUCT.md` sections too — don't add an item that contradicts or
duplicates settled product truth; point at it instead.

**2. Analyze fit against existing items.** Decide, with a stated reason:

- **Duplicate / near-duplicate** of an existing item → propose merging or updating that item
  instead of adding a new one.
- **Extends an Active Initiative** → propose folding into that initiative's Details (and DoD if
  it changes the finish line).
- **New initiative-sized idea** → new Active Initiative in the file's standard shape (user
  story / purpose / definition of done / details — intentionally light, not a spec).
- **Small, concrete UI tweak** → checkbox under the right Small UI Changes subsection.
- **Genuine unknown needing a decision first** → Open Questions — unless it is a *product*
  decision (scope, direction, a stated boundary, the stack), which belongs in `PRODUCT.md`'s
  open-decisions list instead. Two lists of open decisions is how one of them goes stale.
- **Raw note that doesn't fit yet** → Misc / Scratchpad (Unsorted).
- **Already shipped or archived** (check Archived and, if cheap, the code) → say so; nothing to
  add.

**3. Ask about the idea** — one round, max 2–3 questions, sized to the item: for
initiative-sized ideas, ask what's needed to write an honest user story / purpose / DoD (who is
it for, what problem, what does done look like); for a small tweak, at most placement/scope. A
one-line UI fix does not get an interrogation.

**4. Propose, confirm, write.** Show the exact entry text and placement (and any existing item
being updated/merged) before touching the file; on confirmation, write it following the file's
existing conventions — initiative shape, checkbox style, section order, TOC only if a new
section was added, merged/subsumed leftovers noted in Archived per the file's traceability
style.

**Boundaries:** capture only — no code, no spec-writing (an entry stays light per the file's
own header; when it's ripe, it goes through `workflow brainstorm`); `PRODUCT.md` stays the
source of truth for product state — TODO entries point, never duplicate; and the file remains
the human's scratchpad — record their idea faithfully, don't grow it into your own.

Close by showing the entry as written. No next-step phase card — this command doesn't change
workflow state — but if the idea is clearly ripe for immediate work, suggest
`workflow brainstorm <initiative name>` in one line.
