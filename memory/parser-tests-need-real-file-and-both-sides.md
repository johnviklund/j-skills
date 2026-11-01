# A new parser's tests pass on fixtures the real file and the guard's other side would break
Applies when: writing or reviewing a ticket that adds a script reading a repo file, or a `!=`, range or filter guard.
Root cause: fixtures hold only lines the parser keeps, and a guard is tested on the side that failed; deleting a row filter or flipping `!= 6` to `< 6` keeps every test green.
Fix: the acceptance runs the script on the real file and exits 0; each fixture copies the real file's non-matching lines; a `!=` or range guard gets one case on each side, and review mutates it to `<` and `>`. A sweep lists each `and` operand and each interpolated value as its own mutation. The rules sit in `workflow/references/tests.md` (*Fixtures copy the real form*) and `phase-4-review.md`; this run shows they still did not stop it.
Evidence: retire-on-no-signal · correction-mining (C1-1 `shlex.split` on an unmatched quote crashed the report; C2-1 a null `message` or string block still does: guard the whole record at the file loop, not each parser)
Occurrences: 2 · Last confirmed: 2026-11-02 · Status: active
Enforced by: judgement
Promoted to: workflow (tests.md, phase-4-review.md)
