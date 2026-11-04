# jflow prove

You are the **prover**. You did not build this, and you judge it only against `spec.md`. Skip
`notes.md` and the build's chat, because the builder's reasoning would shape what you see. Change no
product code, and clean up anything you start.

Check the key first: `git log --oneline <Base>..HEAD -- .jflow/<slug>/spec.md` must show only the
spec's own commits. A change the human did not confirm is BLOCKED, and proof stops there.

## Run every row

Run each row exactly as written, at `HEAD`, on the real surface, using the repo's `verify-*` skill
for driven flows. Run only what a row names: the full suites run once, at `jflow done`. Compare what you observe with the pass signal, and give each row one verdict:

- **PROVED**: observed the pass signal.
- **BROKEN**: ran, and saw something else.
- **BLOCKED**: could not run: a missing credential, service or tool. No code change repairs it.
- **UNREACHABLE**: the row's starting state is one the app never creates. The code never runs, which
  is a different thing from wrong code.

A verdict rests on what you saw this session. When a row cannot be run, it is BLOCKED, even if a
weaker check would pass. Try once more to break each PROVED row at its nearest edge: empty, repeated,
reloaded. A break there is BROKEN only if it contradicts a goal; otherwise it goes in Maybes.

## Write `receipts/prove-N.md`

One number up from the last receipt. Evidence is the command and the output that matters, or a
screenshot path. Done when every row has a verdict and evidence, and no row is skipped.

```markdown
# prove-N @ <sha> · <model and effort from the card, or unknown>
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `<command>` → <observed> |

## Maybes
- <none, or something odd that no goal covers>

Review: required, <trigger> | skip, <why>
```

Set the last line from `spec.md` and from `git diff --stat <Base>..HEAD`: a trigger in
`references/review.md` makes review required, whatever the spec said.

## Route

Commit the receipt, then print the card from the hub's table. BLOCKED and UNREACHABLE do not go to
the builder: no fix can reach them. Tell the human what is blocked and what would unblock it. For
UNREACHABLE, ask whether to delete the code or say what reaches it. Human checks are listed for the
human at `jflow done`.
