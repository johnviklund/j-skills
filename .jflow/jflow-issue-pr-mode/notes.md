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
- **Only commenters with write access count** (`OWNER`, `MEMBER`, `COLLABORATOR`). On a public repo, anyone could otherwise post a marked `Yes: approach`. The extra test `test_marked_comment_without_write_access_is_ignored` covers this; no Proof row reaches it.
- **Public repos.** `record` and `note` refuse to write without `--confirmed`. The check runs before any write, so the refusal posts nothing.
- **`drive.py`** goes in `.git/jflow/<issue>/`: reused across checks in one clone, and never tracked.

## Open
- `record` posts two comments (the text, then the record). If the second fails, the text stays without its record. Running `record` again posts both again, and the newest pair wins.
- `validate` errors still name `.jflow/#42/spec.md:N`. The line numbers match the comment body, but the path is the temporary one.
- A plain slug finds its issue by listing every issue. That is slow on a repo with thousands.
- The `SKILL.md` pointer adds `references/github.md` (4,351 bytes) to what a step reads in this mode. The 14,000-byte cap test covers only `SKILL.md` plus each of the four step files, which all stay under it.
