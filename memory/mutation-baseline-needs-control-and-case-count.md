# A coverage or mutation baseline without a control and a runner case count is inflated
Applies when: measuring that a test cleanup lost nothing, with a mutation tool or coverage counts.
Root cause: a temporary copy missing a sibling file (`ROUTING.md`) fails tests by itself and inflates the caught count; coverage contexts count outer contexts that accompany subtests twice.
Fix: run the mutation tool once on an unmutated temporary copy before trusting its caught count. Count test cases from the runner's own list, not coverage contexts. Record both numbers in the Base receipt before any test changes.
Evidence: lean-workflow-tests (T1, prototype caught count inflated by 32 fixture failures; Base case count 274 vs 266)
Occurrences: 1 · Last confirmed: 2026-10-31 · Status: active
Enforced by: judgement
<!-- memory.compact 2026-11-01: converted from the legacy workflow/MEMORY.md entry "A baseline for coverage or mutation counts needs a control and a case count". -->
