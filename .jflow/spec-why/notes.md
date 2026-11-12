# spec-why notes

Checks allowed: 4
- The human allows fixing both check-3 defects and a fourth check: "option A" · 2026-11-12.

- `Serves: none` passes validate even with a PRODUCT.md. The spec template offers `none`, and a
  chore may move no outcome. Only a missing line or an unknown name fails.
- Serves must match a `###` heading exactly. A `##` heading such as "The desired state" fails.
- The size test allows under 50,000 bytes, and the skill sat at 49,996 before this change. To fit
  the new lines I reworded SKILL.md, spec.md and done.md, each cut keeping its rule: about 1,100
  bytes in all. build.md and check.md are untouched, per the Non-goals. Now 49,990.
- SKILL.md's Accepted paragraph lost two sentences that restated `next`'s matching: "a verdict
  carried from check-N came from check-N" and "a later check that fails the item again saw the
  acceptance". The code is unchanged; the example lines still show the format.
- Rows 3, 4 and 5 pass when I run them. Rows 1 and 2 need fresh headless spec sessions on the
  installed skill, which updates only after a push, so check runs them against this branch's copy.
- One new test covers row 3 as a table of five Serves cases. Row 4 is the existing historical-specs
  test and the fixture spec, which has no PRODUCT.md.
- Fix for check-1 defects 1 and 2, one cause: Serves matched raw text, not Markdown structure.
  Serves is now read only from the header (before the first `## `), and outcomes are `###`
  headings outside ``` or ~~~ fences, with optional closing hashes. The fence strip is a regex,
  not a CommonMark parser: it strips only closed fences, so a heading in an unclosed fence still
  counts. Malformed Markdown only; I judged that enough.
- To keep the skill under its 50,000-byte size test I removed the five usage lines from
  jflow.py's docstring; `jflow.py COMMAND -h` prints the same, and the docstring now says so.
- Fix for check-2 defects 2 and 3, one cause: the regex fence strip did not follow Markdown. A line
  scanner now reads PRODUCT.md. A fence opens on 3+ backticks or tildes indented 0-3 spaces. It
  closes only on the same mark, at least as long, alone on its line; unclosed, it runs to the end. A
  `###` heading counts when indented 0-3 spaces. The test table gained five cases, and
  `drive.py attack` now gives the right result for all seven inputs.
- Fix for check-2 defect 1: spec.md now says the item's chosen option is settled with its limits,
  such as a cutoff. On rerun, `drive.py 1` gave 2 of 2 sessions that start from `Open for spec`
  and do not reopen the 8 KiB cutoff.
- Size test again: now 49,999 bytes. I cut a slogan from SKILL.md, the line saying an accepted item
  is no longer open (the next paragraph says it), and spec.md's own "run next, print its card" and
  verify.create reason, both repeated elsewhere.
