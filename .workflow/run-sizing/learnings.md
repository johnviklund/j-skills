Command: workflow wrap run-sizing
Created: 2026-10-10
Base:    38dea5df6e9017b0ef36d863fa457ab53206defd
Inputs:  review.md @ 38dea5df6e9017b0ef36d863fa457ab53206defd
Status: done

## Phase 4 — review (2026-10-10)
- [durable→memory] A limit that changes (acceptance lines 4 → 6) needs a test that passes exactly at the new limit as well as one that fails just over it; the over-limit test alone let a `<` for `<=` mutation survive. [routed → references/tests.md "Test the boundary"]
- [drop] A session counter moved to a new home (plan.md ledger) and one writer site (patch plan) was missed; C1-T2 fixed it in the execute and wrap rules themselves, so the rule text now carries the lesson.
