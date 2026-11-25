# jflow in issue and pull request mode

Use this mode on a shared or public GitHub repository that will not take `.jflow/` files or direct
pushes to the default branch. The run lives in GitHub comments, and the branch holds only the code.
Every step works as in [SKILL.md](../SKILL.md) and its step reference, whose last section lists
what changes for that step. Agents read that section; this page is the whole mode in one place. You
need `gh`, installed and logged in.

## Turning it on

- `jflow <command> #42`, or the issue URL in place of `#42`, always runs in this mode.
- For a plain slug, set `git config jflow.mode github` in the clone, or `"mode": "github"` in the
  `--config` or `$JFLOW_CONFIG` file. `.jflow/config.json` cannot set it. Without either, a plain
  slug runs in `.jflow/` mode as before.
- A plain slug's issue is the one titled `jflow: <slug>`. `record spec` opens it when it is missing.

## Where the run lives

| `.jflow/` file | Here |
|---|---|
| `spec.md` | a `jflow:spec` comment on the issue |
| `## Accepted` lines | `jflow:accepted` comments on the issue |
| `notes.md`, `Yes:` and `Checks allowed:` lines | `jflow:notes` comments on the pull request |
| `receipts/check-N.md` | `jflow:receipt` comments on the pull request |
| `run.jsonl` | `jflow:record` comments: the spec's on the issue, the rest on the pull request |
| `drive.py` | `$(git rev-parse --git-dir)/jflow/<issue>/drive.py`: inside `.git`, so never committed |

The pull request is the draft whose head branch is `jflow/<issue>`, in this repo or in a fork.
Its body says `Closes #<issue>` so merging the pull request closes the issue; a fork's pull request is
found through that reference. `jflow.py` reads comments in the order they were posted, and only
from the `gh` user and people with write access to the repo. An organization member with read
access does not count.

Write each text to a temporary file outside the repo, then let `jflow.py` post it. It adds the
comment's first line, the marker, so never post a jflow comment by hand:

- `jflow.py validate <slug> <step> --file F` checks a spec, receipt or Accepted lines before posting.
- `jflow.py record <slug> spec|check|accept --file F ...` validates and posts the text, then the record.
- `jflow.py note <slug> --file F` posts a notes comment: an `## Approach`, a judgement call, a
  `Yes:` line, `Checks allowed:` or `Live done:`.

`validate` and `next` refuse the run when the branch has `.jflow/` files, staged or committed, and
when anyone has edited, unmarked or deleted the spec comment since `record spec`. To change the
spec, run `jflow spec` again: it posts a new spec comment and records it, and `next` then asks for a
check, so every row runs again.

## Spec

Never edit the issue body. On an existing issue, post the spec as a comment with `record spec`; it
also adds the `ready-for-agent` label (and removes `next` if present) so the board moves the issue
to Ready. For a plain slug, `record spec` opens the issue first. Set `Base:` to the default branch's
`HEAD`.

## Build

Create branch `jflow/<issue>` from `Base`. Make an empty first commit, push it, and open a draft
pull request with `Closes #<issue>` in its body (`gh pr create --draft`). Do this before anything else,
because notes, including an `## Approach` for **Ask first**, go on that pull request. Later pushes
wait for done, as in `.jflow/` mode.

## Check

Work on branch `jflow/<issue>`. Read the spec and its Accepted lines in the issue's comments
(`gh issue view <issue> --comments`). The builder's notes are on the pull request: read no pull
request comment until your findings are drafted. The key check is done for you: `validate` and
`next` refuse a spec comment that was edited, or added without `record spec`. Keep `drive.py` at
the path in the table: later checks in the same clone reuse it, and git never tracks it. Post the
receipt with `record check --file`.

## Done

Follow [done.md](done.md) with three changes. In step 4, leave the spec comment as it is:
`record done` marks the run done. In step 6, delete `drive.py` from `.git/jflow/<issue>/`. In
step 8, push the branch, then mark the pull request ready with `gh pr ready <number>`. Never merge it: the repo's
own review does that. The step ends when the pull request is ready for review.

## Public repos

`public_paid_needs_human` covers every comment, issue, push and pull request on a public repo.
Before each one, show the human what will be posted and ask. On their yes, pass `--confirmed`.
Without it, `record` and `note` refuse to post to a public repo.

## When gh fails

`jflow.py` runs `gh` in the clone that `--repo` names. A missing `gh`, a `gh` that is not logged
in, or a missing pull request stops `jflow.py` with one
line naming the cause, and nothing is posted. Fix the cause and run the same command again.
