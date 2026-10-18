# Tests — the reference execute and plan work from

> Reached from `phase-3-execute.md` and `phase-2-plan.md`; read it through the `workflow` skill.

A ticket's behaviours become tests; its acceptance lines become cases. These rules keep them useful.

**Test behaviour at the seam.** A test drives the ticket's public interface and asserts what a
caller can observe. It reads like the acceptance line it came from ("usage with float token
counts is stored as ints") and survives a rewrite of the internals.

**Smallest seam.** Pick the smallest seam that proves the line. A pure rule gets a unit test of
its function. The reached surface gets one end-to-end test per behaviour, not per acceptance line.

**One concept per test.** Assert the value the line names, with few literals: no unrelated
derived strings, call counts or prompt layout. An exact long string only when it is the product.

**Parametrize variants.** Inputs that share one expectation are one parametrized test
(`subTest`, `pytest.mark.parametrize`), not one test each.

**No test imports a test.** Shared fixtures go in `conftest.py` or a fixtures module.
`check-run.py` warns on a ticket commit that adds one.

**Keep test files small.** A test file stays at 1,500 lines or fewer; split it by feature before it
grows past. A big file costs every reader its tokens, and an edit to it is harder to review.

**Never assert source text.** SQL, a code file's contents and CTE aliases are not behaviour:
assert the schema contract or the output. A deny-list of forbidden tokens is the one exception.
`check-run.py` warns on a ticket commit whose tests add SQL file reads.

**A deny-list gets a case per form.** List every form the grammar allows for the thing it blocks
(every Snowflake write statement, not only the ones the corpus uses) and give each a negative case.
A guard that requires several lines gets one case per line missing alone; a guard that matches on
several keys gets one case per key, differing only in that key. Dropping all at once cannot tell
them apart.

**Expected values come from outside the code.** Use the literal from the acceptance line, a
worked example, or a known-good fixture. An expected value computed the way the code computes it
(`assert total(items) == sum(i.price for i in items)`) passes by construction — a **tautology**.

**Mock only at system boundaries**: external APIs, paid providers, time, randomness, and
sometimes the database or filesystem. Your own modules run for real. When a boundary is hard to
fake, inject it (pass the client in) and give it one small function per operation.

**Verify through the interface.** Read the result back the way a caller would (`get_user(id)`),
not through a side channel (querying the table directly).

**Test the surface that is actually reached.** A UI test drives the page or component the user
gets — confirm the module under test has a live importer before trusting it; a builder nothing
renders proves nothing. When the ticket suppresses or retires a value, search every read of it
(ordering, labels, ranks, captions, exports) and assert each one, not only the value's own cell.

**Round-trip contracts.** A test that asserts a new or changed field on a producer validates the
producer's real output against the consumer's contract model in the same test (for example, parse
it with the strict consumer schema). Asserting the producer's own dict passes while every consumer breaks.

**Assert something positive.** At least one assertion per behaviour checks that the new answer is
present with its real value. "Lineage exists", "old text is gone" and "no error" all pass on an
empty result.

**Live results are receipts.** What only a live system can show (an ingest, a deployed page, a
paid run) is checked by an operator ticket's receipt against literal values — never by a mock
standing in for the live system.

**Red → green, one behaviour at a time.** Write one test with parametrized acceptance cases.
Run each new case, watch it fail for the expected reason, then write the least code that passes.
The failing run proves the test can catch the bug; a test that never went red proves nothing.

**Prove it can fail.** At green, invert or revert one line of the change and rerun: it must go
red. The report records it as `Mutation: <line> → red`. Add a test beyond the acceptance lines
only when a mutation survives.

**Verify keywords.** `unittest -k` matches case-sensitively against `module.Class.method`, so put
the keyword in each test method name and check the `Ran N tests` count, not just OK. A keyword must
not be a substring of another ticket's test names, or this ticket's Verify goes red during that
ticket's red step.

**Test the boundary.** A ticket that moves a limit gets one test that passes exactly at the new
limit and one that fails just over it; the over-limit test alone lets a `<` for `<=` mutation live.

**Test budget.** From 2026-10-19, logic and contract commits with ≥ 50 tests net error above 1.5× code added.
Use one parametrized test per behaviour; exceptions need `Ratio waived: T# — <reason>` under `## Deviations`. Earlier plans keep their rules.

**Signs a test is wrong:** it breaks on a refactor that kept behaviour; it asserts call counts or
call order on your own code; its name describes how instead of what; it needed a mock of a
module you own; it passes on either arm of an "or".

**Existing tests are the old bar.** Rewriting a test you didn't write is a deviation: diff its
assertions, not the file — count them before and after, and say which changed and why.
