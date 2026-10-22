# Learnings — retire-date-gates

- [durable→memory] Gating a rule on run status needs one test per status the gate branches on (live, parked, done). Cycle 1 found two P1s that way: a done run lost its sha walk, and a parked draft failed strict section checks. [routed → none: already covered by the one-test-per-guard-key rule in tests.md]
- [durable→memory] A gate keyed on `Report.done` must keep the checks that only make sense after `done`, because wrap sets the brief done in the same commit as the wrap summary. [routed → none: recorded in plan.md finding F2 and review.md C1-1]
