# TODO intake — `workflow todo [idea]`

> ⚠️ Read through the `workflow` skill; the command ends with its closing card.

Seat: **brainstorm partner** at medium effort — mapping in `ROUTING.md`. Rationale: this is
knowledge-shaped intake dialogue with no execution payoff — the same seat as brainstorm, and
it's a quick command; never spend a heavy or reviewer seat on it. Runs anytime, in any
session — it doesn't change `.workflow/` state.

Capture the idea into repo-root `TODO.md` as **one short line** — intake only, never the start of
a spec or of implementation. `TODO.md` is a scratch pad (target ~10 KB; sections such as the
idea areas, `## Open Questions`, `## Review deferrals`, and a one-line `## Archived` pointer to
`<repo>/TODO_ARCHIVE.md`) holding ideas *not yet brainstormed*; an idea that has been brainstormed
lives as a `.workflow/<slug>/` run (live or parked) and is not listed here twice. Check
`grep -l 'Status: parked' .workflow/*/brainstorm.md` before adding: a match means "that's parked as
`<slug>` — unpark it or leave it," not a new item. If the idea is clearly run-sized and the human
wants it now, offer `workflow brainstorm <slug>` instead of an intake line.

**1. Read before writing.** Read `TODO.md`'s headings, then the section the idea belongs in and
anything `grep -i` finds for its key words (read the whole file only if it is under ~15 KB and the
fit is unclear). `grep -i` the key words in `TODO_ARCHIVE.md` too — never read it whole. If the idea
touches product direction, `grep` the relevant `PRODUCT.md` headings and read only that section —
don't add an item that contradicts or duplicates settled product truth; point at it instead.

**2. Decide fit, with a stated reason:**

- **Duplicate / near-duplicate** of an open item → propose updating that line instead.
- **Already shipped or archived** (a hit in `TODO_ARCHIVE.md`, or the code) → say so; nothing to add.
- **Genuine unknown needing a decision first** → `## Open Questions` — unless it is a *product*
  decision (scope, direction, a stated boundary, the stack), which belongs in `PRODUCT.md`'s
  open-decisions list instead. Two lists of open decisions is how one of them goes stale.
- **Anything else** → one line in the right section: `- <short title> — <one clause: what / why>`
  (≤ ~160 characters, no user story, no definition of done, no sub-bullets).

**3. Ask only what placement needs** — at most one round of 1–2 questions (which section, is it a
duplicate). Never interrogate for a story, purpose or definition of done: an idea that needs more
than a line is brainstorm material, and the answer is `workflow brainstorm`, not a longer entry.

**4. Propose, confirm, write.** Show the exact line and placement (and any existing line being
updated) before touching the file; on confirmation write it following the file's conventions.

**Boundaries:** capture only — no code, no spec; refuse to grow an idea into a spec or merge detail
from the conversation into the line (the human's wording stays, shortened if needed). `PRODUCT.md`
stays the source of truth for product state — entries point, never duplicate. This command writes
only `TODO.md`; archiving is wrap's job.

Close by showing the line as written. No next-step phase card — this command doesn't change
workflow state — but if the idea is clearly ripe for immediate work, suggest
`workflow brainstorm <idea>` in one line.
