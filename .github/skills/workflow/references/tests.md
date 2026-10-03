# Tests — the reference execute and plan work from

> Reached from `phase-3-execute.md` and `phase-2-plan.md`; read it through the `workflow` skill.

A ticket's acceptance lines become tests. These rules make those tests worth keeping.

**Test behaviour at the seam.** A test drives the ticket's public interface and asserts what a
caller can observe. It reads like the acceptance line it came from ("usage with float token
counts is stored as ints") and survives a rewrite of the internals.

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

**Red → green, one acceptance line at a time.** Write one test, run it, watch it fail for the
reason you expect, write the least code that passes it, run again. Then the next line. The
failing run is the proof the test can catch the bug; a test that never went red proves nothing.

**Signs a test is wrong:** it breaks on a refactor that kept behaviour; it asserts call counts or
call order on your own code; its name describes how instead of what; it needed a mock of a
module you own; it passes on either arm of an "or".

**Existing tests are the old bar.** Rewriting a test you didn't write is a deviation: diff its
assertions, not the file — count them before and after, and say which changed and why.
