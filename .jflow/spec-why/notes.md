# spec-why notes

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
