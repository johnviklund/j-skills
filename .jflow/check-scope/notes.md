# check-scope notes

- New input means any commit since the one that added the previous receipt, other than receipts and
  `run.jsonl`. So a `notes.md` line, an accept or a code commit counts, and re-recording a committed
  receipt still sees its own commit as no input.
- A previous receipt that was never committed skips the input rule: there is no commit to count from.
- Rows 5 to 7 are doc reads with no test; a grep test would only repeat the wording.
- Row 1 is measured over the next five runs; nothing here can prove it now.
