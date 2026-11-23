# Notes: jflow-issue-pr-mode

## Approach
- **Markers.** Every jflow comment begins with one line `<!-- jflow:KIND v1 sha=SHA -->`, where KIND is `spec`, `accepted`, `notes`, `receipt n=N` or `record`, and SHA is `HEAD` when it was posted. The body after it is the same Markdown the matching `.jflow/` file holds; a `record` body is the run.jsonl line in a ```json fence. Comments without a marker are ignored.
- **Spec lock.** `record spec` stores the sha256 of the spec comment body in its record. `validate` and `next` refuse the run when the current body hashes differently. `## Accepted` lines live in their own `accepted` comments, never in the spec comment.
- **Link.** The run key is the issue number: `#42` or an issue URL gives `42`. A plain slug in GitHub mode finds the open issue whose spec comment carries `slug=<slug>` in its marker, or `jflow spec` opens one titled `jflow: <slug>`. The pull request is the draft whose head branch is `jflow/<issue>`, with `Refs #42` in its body (`Refs`, not `Closes`, so nothing closes the issue).
- **Config.** `git config jflow.mode github` (repo-local, never committed) or a top-level `"mode": "github"` in the `--config` or `$JFLOW_CONFIG` file. `.jflow/config.json` cannot set it. Allowed values: `jflow` (default) and `github`.
- **Order.** Where `.jflow/` mode asks git which commit came first, GitHub mode uses comment order: an `## Accepted` line closes an item when it was posted after that check's receipt comment and names its sha. The cap and no-code-change reruns still compare the receipts' code shas with `git diff`, as now.
- **Code.** `jflow.py` is at 29,991 of 30,000 bytes, so the GitHub code goes in a new `scripts/jflow_gh.py`. It reads the comments into a temporary run folder plus an ordering table, and `jflow.py` gains a small hook paid for by trimming its own comments and docstrings. Every `gh` call goes through one wrapper that turns a missing binary, an auth error or a missing PR into one line on stderr and exit 1. Nothing is posted until every check has passed.
- **Public repos.** `record` refuses to post to a public repo unless `--confirmed` is passed. The docs tell the agent to ask the human first, which is how `public_paid_needs_human` works today.
Yes: approach · "yes" · 2026-11-23

## Build notes
- **Replay, not a second rule set.** `jflow_gh.py` turns the comments into a temporary git repo. It borrows the real repo's objects, and makes one commit per comment, in posting order, on top of the code tree the comment's `sha=` names. `jflow.py`'s `next`, `validate` and `summary` then run unchanged against that repo. The order rules (receipt before Accepted, no-code-change reruns, the cap) come out of the same git calls as in `.jflow/` mode, so the two modes cannot drift. `test_github.py` plays each Row 3 story in both modes and compares the decisions.
- **`record done` stands in for `Status: done`.** The spec comment is locked, so the replay sets `Status: done` at the done record.
- **Size cap.** `jflow.py` stays under 30,000 bytes (29,998) only because three `git log --diff-filter=A` calls became one `born()` helper, the slug check moved into `Hub.of`, and four comments and one help string got shorter. The GitHub options and the `note` command are registered by `jflow_gh.add_args`.
- **`.jflow/config.json` and `mode`.** `seats()` accepts `mode` as a known key. `jflow_gh.github_mode` refuses it in `.jflow/config.json` and refuses any value other than `jflow` or `github`. `jflow.py seat` never reads `mode`.
- **A missing pull request is an error only when one is needed.** `next` routes to `spec` and `build` before the pull request exists. It fails only once code has changed since Base, or for `note` and the records that live on the pull request. Build opens the draft with an empty first commit, so the Ask first approach has somewhere to go.
- **Who counts.** Only the `gh` user's comments count, plus comments from people whose collaborator permission is `admin`, `maintain` or `write` (fix for check-1 defect 3: `MEMBER` can be read-only). The `gh` user is trusted so a fork contributor without push access can still run jflow on their own pull request. If the permission call is refused (403 or 404), that commenter does not count. Test: `test_marked_comment_counts_only_from_the_gh_user_or_write_access`.
- **Public repos.** `record` and `note` refuse to write without `--confirmed`. The check runs before any write, so the refusal posts nothing.
- **`drive.py`** goes in `.git/jflow/<issue>/`: reused across checks in one clone, and never tracked.

## Open
- `record` posts two comments (the text, then the record). If the second fails, the text stays without its record. Running `record` again posts both again, and the newest pair wins.
- `validate` errors still name `.jflow/#42/spec.md:N`. The line numbers match the comment body, but the path is the temporary one.
- A plain slug finds its issue by listing every issue. That is slow on a repo with thousands.

## Fix after check-1
- **Defect 1.** The spec lock now also refuses a spec comment that was unmarked or deleted after `record spec`: once a lock exists, the newest spec comment must exist and match it.
- **Defect 2.** A spec posted after the newest receipt now needs another check. The replay adds a stand-in file, `.jflow-spec-changed`, outside `.jflow/` in the temporary repo's final commit. `jflow.py` sees a change since that receipt and asks for a check, until the next receipt is posted. Only the spec comment body counts, so Accepted comments do not trigger it. `.jflow/` mode has the same gap (its `changed()` ignores `spec.md`). I left it alone, because changing `.jflow/` mode is a non-goal. Test: `test_spec_recorded_after_the_newest_check_needs_another_check`.
- **Defect 4.** Every `gh` call runs with `cwd` set to the clone `--repo` names.
- **Defect 5.** If no pull request comes from `<owner>:jflow/<issue>`, the issue's timeline is read for cross-references from pull requests in this repo, and the first one whose head branch is `jflow/<issue>` is used. That covers fork pull requests with `Refs #<issue>`.
- **Defect 6.** No step reads `github.md` any more. Each step reference ends with a short "Issue and pull request mode" section, and `SKILL.md` links to it in one line. With the check section included, `SKILL.md` + `check.md` is 13,997 bytes. To fit, I dropped the template's three repeats of the 240-character limits; the prose above the template still states both limits. `github.md` stays as the whole mode in one place, for people and for Row 7.
- The checker's `drive.py` probes for defects 3 to 5 patch the old stub text and post the approval as the `gh` user. They cannot see these fixes as written. The new tests cover each defect against the updated stub.

## Fix after check-2
- **Defect 1.** A done record counts only when it comes after the newest spec comment. A spec posted after done starts the run again: the spec reads `Status: ready`, and the stand-in file from the check-1 fix asks for check-2. Test: `test_spec_recorded_after_done_needs_another_check`.
- **Defect 2.** `find_pr` collects every pull request from `jflow/<issue>`: from this repo's head branch, plus the forks found through the issue's references whenever this repo has no open one. It picks an open pull request first, then the highest number. Test: `test_fork_pull_request_found_through_its_issue_reference_open_one_first`.
Checks allowed: 4

## Fix after check-3
- **Defect 1.** The replay writes `Status: done` only for a done record after the newest spec comment, so an earlier, superseded done leaves no `Status: done` in the temporary history. `summary` then ends at the current run's done and counts code added after a re-spec. `.jflow/` mode keeps its own `done_commits[-1]` (the oldest change to `Status: done`), so historical runs keep their numbers. A re-spec after done in `.jflow/` mode would show the same undercount; changing that is a non-goal. Test: extended `test_spec_recorded_after_done_needs_another_check`.
