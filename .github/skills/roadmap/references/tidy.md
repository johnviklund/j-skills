# roadmap tidy

Reviews the whole roadmap, proposes every change with its evidence, and applies only what the human
says yes to.

## 1. Check

Run `check` with `--repo` for every repo an item's `Run` names. Look for each repo beside the
current one; list any you cannot find as unchecked. When the file is not yet in the format, `check`
reports errors on most lines: that is the starting point for a conversion, below.

## 2. Review every open item

Read `PRODUCT.md` and `DESIGN.md` first. Then read each open item, and verify at least one fact
in it against git, the code or a run. Look for:

- **Stale:** the problem no longer holds, or the item names a branch, file, skill or item that has
  changed. Quote the commit or line that shows it.
- **Overlap:** two items that solve the same problem.
- **Conflict:** two items that pull in opposite directions, or an item that contradicts a decision
  recorded in the repo.
- **No why:** a `Problem` that names a solution, or holds no evidence; an `Impact` with no size,
  or in a unit the items beside it do not use.
- **Fix chosen early:** an `Options` line, or a `Problem` or `Solved when` that only one fix can
  meet. Turn each idea into an `Open for spec` question.
- **Rank:** items in a group out of priority order, by `Impact` for `Budget`, then `Why now`.
- **Off course:** an item whose `Serves` outcome it does not really move, or that works against a
  principle or non-goal in `PRODUCT.md`, or against a decision in `DESIGN.md`.
- **Gap:** an outcome in `PRODUCT.md` that no open item moves. Propose an item, or ask whether the
  outcome still holds.
- **Wrong group**, by the table in `SKILL.md`.
- **Hard to read:** fields as plain lines, which render as one paragraph, or a field longer than
  two sentences. Converting the layout is a fact; shortening a field changes what it says.
- **Next up:** whether the order still holds, whether each line says why it goes before the next,
  and whether the first item can start today.

**Converting a roadmap** that is not yet in the format: each item takes its fields from the text
that already exists, quoted or condensed. A required field with no source becomes a question;
an `Impact` the repo can measure is measured first. A list of fixes becomes `Open for spec`
questions.
Prose that is not an item, such as a plan or a decision, stays in its own document, and the
roadmap's preamble links to it.

Done when every open item has been read and each finding has its evidence.

## 3. Propose

Write the change list to a temp file: one numbered change per line, each with its finding and its
evidence. Then ask, in rounds of at most five questions:

- **Facts first, as one question:** status from a done run with its sha, format fixes, done items
  moving to the archive.
- **One question per change in meaning:** merge, drop, rewrite a `Problem`, move to another group,
  reorder a group or Next up. Recommend an answer for each.

A conversion with many items asks group by group. Done when every change has an answer.

## 4. Apply

Apply the changes the human said yes to, and only those. Finish as `SKILL.md` says under
*Changing the file*. The final message lists what changed, what the human declined, and what is
still open, then Next up. Done when the roadmap is committed and `check` prints no `error:` line.
