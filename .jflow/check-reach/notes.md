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
