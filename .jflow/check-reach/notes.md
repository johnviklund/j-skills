# check-reach notes

- The tag sits right after the defect number: `- 1. [edge] file: ...`. `validate` and `next` both
  read it there, so a tag elsewhere in the line counts as untagged and routes to fix.
- The receipt template in `check.md` shows `[use]` as the literal tag, not a placeholder such as
  `[use or edge]`, because a copied placeholder would fail `validate`.
- An edge-only stop comes before the BLOCKED/UNREACHABLE stop. Once the human accepts the defects,
  `next` moves on to the stuck rows as before.
- The edge-only stop is a human stop, not a fix, so the check cap does not fire there. If the human
  picks B and fixes, the next check counts toward the cap as usual.
- Room under the 30,000-byte cap came from existing code with the same output: one fix-command
  string in `next_step`, a dict for the line counts in `summary`, one read of spec and notes, and
  a loop for the shared argparse arguments. `test_next_and_summary_match_base_on_five_runs` shows
  `next` and `summary` match the Base script. The script is at 29,993 bytes.
- `validate` now adds `None` to the defect set for a placeholder line. That is harmless, because
  BROKEN citations look up digit strings.

## Fix 1 (check-1)
- Defect 1: the edge-only stop now runs after the cap is known. At the cap, option B adds
  `Checks allowed: N+1` before the fix, so the fix leads to a check, not a second stop. Accept
  stays first, as goal 2 asks. Following B by hand at `b5b2e13` with `Checks allowed: 4` led to
  `jflow check check-scope`.
- Defect 2: the tag slot takes any bracket text, `[^]]*`, so `[needs-review]` is refused. A
  markdown link such as `[x](url)` has no `] ` and still counts as untagged.
- Defect 3: `validate` refuses a repeated defect number. `next` keys defects by number, so a repeat
  hid the `[use]` line. Every old receipt still validates, 9 of 10 as before.
- Room: `check_fields` is gone. Its no-receipt error was unreachable, because `record check` runs
  `validate` first, which already reports the missing receipt. The script is at 29,985 bytes.
