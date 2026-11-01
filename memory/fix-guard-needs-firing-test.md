# A guard added by a fix ticket ships with no test that makes it fire
Applies when: writing or reviewing a patch ticket whose fix adds a guard, check or early return.
Root cause: the ticket's acceptance names the case that failed, so the new guard is covered only by the original case; deleting the guard keeps every test green.
Fix: the patch ticket accepts one line that makes the guard fire (an input only the guard refuses), and review mutates the guard once to see it fail.
Evidence: git-hooks (C2-2) · exam case missed-assistant-privacy-guard-has-no-test (private set, 2026-10-21)
Occurrences: 2 · Last confirmed: 2026-11-01 · Status: active
Enforced by: judgement
