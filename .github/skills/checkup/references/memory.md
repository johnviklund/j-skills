### 2. Memory hygiene

```sh
wc -lc MEMORY.md 2>/dev/null; ls memory/*.md 2>/dev/null | wc -l
grep -L '^Occurrences:' memory/*.md 2>/dev/null                      # pages missing the standard footer
grep -H '^Occurrences: *[2-9]\|^Occurrences: *[1-9][0-9]' memory/*.md 2>/dev/null   # repeats, for the enforcement checks
grep -H '^Enforced by:' memory/*.md 2>/dev/null
ls -d MEMORY.proposed.md memory.proposed MEMORY_ARCHIVE.proposed.md skill-promotion-candidates.proposed.md 2>/dev/null
```

- **Index ↔ pages.** Every `memory/<slug>.md` has a line in `MEMORY.md` and every index line
  resolves to a page; an orphan either way is ⚠️. Inline entries still in `MEMORY.md` (v1 shape)
  are ⚠️ "not yet split into pages -- `memory.compact`".
- **Page shape.** A page missing `Applies when` / `Root cause` / `Fix` / `Occurrences` is ⚠️ --
  it can't be matched on repeat.
- **Unenforced repeat.** A page with `Occurrences: 2` or more and no `Enforced by:` line is ⚠️ --
  classify it (`memory.remember`, *Repeats escalate to enforcement*). `Enforced by: pending` whose
  TODO line is gone from `TODO.md` and `TODO_ARCHIVE.md` is ⚠️ -- the ticket was dropped.
- **Enforced but still active.** `Enforced by: <check>` with `Status: active` is ⚠️ -- retire it.
  Confirm the named check still exists (grep its config or command); a missing one is 🔴, since
  the page claims a protection the repo lost.
- **Promotion signal.** A page with `Occurrences: 3` or more, `Enforced by: judgement` and no
  `Promoted to:` line is ⚠️ -- skill candidate (`memory.remember`), human decides.
- **Size pressure.** > ~40 pages or `MEMORY.md` > ~40 KB: recommend `memory.compact` (do not
  compact here).
- **Stale pages.** `Last confirmed:` > 90 days before today.
- **Superseded still active.** A page with `Status: superseded` still indexed as active belongs
  in `MEMORY_ARCHIVE.md` / out of the index.
- **Leftover proposals.** A lingering `MEMORY.proposed.md` / `memory.proposed/` (or archive/skill-promotion proposal)
  means a compaction was generated but never accepted or discarded -- ⚠️, recommend review/`mv` or delete.
