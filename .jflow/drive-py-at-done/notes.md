# notes

- The deletion is a new done step 6, before the commit step, so it lands in the done commit. Steps 6
  and 7 became 7 and 8; nothing else cites done's step numbers.
- The `git show` rerun rule sits in that step, not in `check.md`, because the spec keeps check's
  driver rules unchanged.
- Row 7 has no new test: row 8 allows only `.md` changes. I ran it by hand in a scratch repo, and
  `changed` returned `False`.
- The `SKILL.md` tree line stays one line, so row 5's grep shows "deleted at done".
