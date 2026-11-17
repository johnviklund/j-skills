# check-scope notes

- New input means any commit since the one that added the previous receipt, other than receipts and
  `run.jsonl`. So a `notes.md` line, an accept or a code commit counts, and re-recording a committed
  receipt still sees its own commit as no input.
- A previous receipt that was never committed skips the input rule: there is no commit to count from.
- Rows 5 to 7 are doc reads with no test; a grep test would only repeat the wording.
- Row 1 is measured over the next five runs; nothing here can prove it now.

## Fix after check-1
- Defects 1 and 2: new input is now only code outside `.jflow/`, or this run's `notes.md` or
  `spec.md`. A previous receipt that was never committed counts from its header sha.
- Defect 3: size is the file's byte count on disk, so CRLF counts.
- Defect 4: a limit on the check goes in the evidence of the row it stops, not in Maybes.
- `test_full_run_counts_sessions_rounds_checks_and_lines` recorded check-2 with no commit after
  check-1, which defect 1 says must be refused. With the human's yes, its fixture now commits
  check-1, then a `notes.md` line, before check-2. No assertion changed.
- Row 1 stays BLOCKED until five runs finish after done.

## Fix after check-2
- Defects 1 and 2: input now comes from a tree diff between the previous receipt's commit and
  `HEAD`, with renames off. `git log --name-only` skipped merge commits and gave only a rename's
  destination.
- Defect 3: an unreadable previous receipt is reported as "cannot read check-N", with no traceback.

## Fix after check-3
- The OpenAI checker session took over the fix from the Anthropic builder session.
- `validate` compares Git paths as bytes. A filename with a non-UTF-8 byte no longer hides new input.

Checks allowed: 4

- Check 4 ran in a fresh OpenAI session. The last fix also ran on OpenAI.
