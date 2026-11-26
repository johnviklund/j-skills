# TODO

Archived items: see TODO_ARCHIVE.md (grep it).

## jflow
- Re-spec gap in `## Proposed edits` — after a mid-run re-spec, a proposal deleted in one commit and reposted unchanged in a later one, or trimmed with its stale yes removed, skips its `edits` stop. Fix: treat the proposal as new when any commit to `notes.md` since the re-spec changed its `- ` lines, read with `git log`. Make room under `jflow.py`'s 30,000-byte cap first: it is at 29,991 (headless-done-wait-point, accepted at check-4)
- GitHub-mode `validate` errors name the temporary `.jflow/#42/spec.md:N` path; name the spec or receipt comment instead (jflow-issue-pr-mode)
- `.jflow/` mode re-spec gap — a `spec.md` change after a passing check or after done routes no new check, and `summary` ends at the first done; GitHub mode fixed both in `jflow_gh.py` (jflow-issue-pr-mode)
- GitHub-mode `memory.remember` on a spec-only run with no linked PR has nowhere to post its routing note, because `jflow.py note` needs the PR (jflow #7)
- Unpushed commits on Human checks stop — `jflow.py next` adds an `Unpushed: N commits ahead of <upstream>` detail line when `@{u}..HEAD` has commits (hq-py39 retro)
- `skill-trials.py` reads `jflow:` lines only from `WORKLOG.md`; a repo with no worklog keeps its line in `notes.md` with no date, so its runs never count toward a trial. Fix: date it from the run's `done` record in `run.jsonl` (delete-workflow)
- Guardrail: test — resolve the git object directory with `git rev-parse --git-common-dir` instead of `ROOT / '.git/objects'` in `.github/skills/jflow/scripts/tests/test_validate.py` (`test_historical_specs_and_all_sixteen_receipts`) · must fail in a `git worktree` at `5396a4c` (escaped-defects retro)
- Guardrail: check — in GitHub mode, when HEAD is not on `jflow/<issue>` and `Base..HEAD` has code, `jflow_gh.py` says "no linked pull request: open a draft PR", which sends the human to do build's job. Name the real cause instead: "HEAD is on BRANCH, not jflow/N, and has commits past Base: check out Base or jflow/N and rerun; build opens the draft PR" · must fail on hq-brain `c8ec374` (branch `brain-reddit-pr-template-feedback`) against #3's `Base: 3c85897` (retro #3, hq-brain, 2026-11-26)

## Review deferrals
- `jflow-config`: Unsupported flags or invalid `--session` values can echo key-like text in stderr; nothing is recorded. The human kept this existing behavior on 2026-11-08.
- `receipt-evidence-cap`: Measure the next three trial runs. Every Evidence cell and defect `Evidence:` part must be at most 240 characters, and each receipt under 3 KB. A work-repo run done 2026-11-17: every Evidence cell at most 240 characters; all 15 receipts over 3 KB, 3.0 to 7.7 KB, mostly Maybes.
- `check-scope`: After five runs, measure row 1 with `jflow.py summary --json` and receipt sizes: median checks a run under 3.5, Maybes under 1.7 a check, no check rerun without new input, every receipt under 3 KB. Also judge whether check still catches real defects. Accepted at done on 2026-11-17: a numbered list under a bare `Checks allowed:` heading can override the cap line above it.
- `check-reach`: After five runs, judge whether edge-only stops replaced fix rounds without hiding a real bug. `jflow.py` is at 29,991 of its 30,000 bytes, so the next change to it must make room.
- `jflow-validate`: Revisit non-template BROKEN citation lists and leading-zero defect IDs if needed; check-3 records the limits kept at done on 2026-11-10.
- `escaped-defects`: Accepted at check-5 on 2026-11-25: a commit or compare URL carrying a credential-like `prefix:` qualifier before a 40-char commit SHA in `--ref` is accepted instead of refused.
