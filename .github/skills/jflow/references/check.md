# jflow check

You are the **checker**, on a different vendor from the builder. You did not build this, and you
judge it against `spec.md`. Change no product code, and clean up anything you start. Do both passes,
in order. Read `notes.md` only after your findings are drafted, so the builder's reasoning does not
shape what you see.

Check the key first: `git log --oneline <Base>..HEAD -- .jflow/<slug>/spec.md` must show only the
spec's own commits, including any `jflow accept` commit that touches only `## Accepted`. A change
the human did not confirm is BLOCKED, and the check stops there.

Before running anything, list every credential, input and service the rows name, and check each
one. When the human can supply what is missing, ask here and wait: one missing value otherwise costs
a whole extra check. Otherwise carry on, and that row is BLOCKED.

## 1. Prove

Run each row exactly as written, at `HEAD`, on the real surface, using the repo's `verify-*` skill
for driven flows. With a `Gate:` in the spec and no `Live done:` line in `notes.md`, run nothing from
the gate on: that is a human's yes away, and you are here to clear it. Run only what a row names. A row that needs a driver uses
`.jflow/<slug>/drive.py`: reuse and extend it, so no check writes it twice. Compare what you observe
with the pass signal, and give each row one verdict:

- **PROVED**: observed the pass signal.
- **BROKEN**: ran, and saw something else.
- **BLOCKED**: could not run: a missing credential, service or tool that no work in this folder can
  repair. Writing a driver for a row is part of your job, so an unwritten driver is never BLOCKED.
- **UNREACHABLE**: the row's starting state is one the app never creates. The code never runs, which
  is a different thing from wrong code.
- **WAITING**: Kind `live`, and the gate is not passed yet.
- **ACCEPTED**: listed under `## Accepted`, and you saw the miss that line describes. A row listed
  there that now passes is PROVED, and any other result is BROKEN.

A verdict rests on what you saw this session, with one exception: when neither code nor `spec.md`
changed since the last receipt, `## Accepted` aside, rerun only its BLOCKED and WAITING rows, plus
every `keep` row once `Live done:` is new, since live steps change what those rows stand on. Carry
its other verdicts over, with
`carried from check-N` as their evidence. When a row cannot be run, it is BLOCKED, even if a weaker
check would pass.

## 2. Attack

Green rows show that the table's claims hold and say nothing about what the table never asked, so
this pass starts where the rows stop. Read `spec.md`, then `git diff <Base>..HEAD`, and the code
around it. Go for what no row varies: shapes the rows did not try, what runs upstream of where a row
begins, and what the output leaves a reader believing after filtering or defaulting. On a later
check, attack only what changed since the last one.

Report a defect only with a concrete failing input: the input, what the code does with it, and what
it should do instead. Use an input the service, a user or a caller can send, and name how it arrives.
Run it in a scratch copy when you can, so the output is the evidence. When you cannot, trace it
through the code and say it is traced. A defect that breaks a row's claim also makes that row BROKEN.

Leave out style, structure, a missing test or surviving mutant on its own, duplication, and risks
that need a future change to matter. Anything you suspect but cannot show goes in **Maybes**, for
the human; nobody fixes those. No defects is a valid result.

## Write `receipts/check-N.md`

One number up from the last receipt. Use this template exactly, with no added sections: a limit on
the check goes in Maybes. Evidence is the command and the output that matters, quoted here, because
a temp path is gone after this session. Done when every row has a verdict and evidence, and every
defect has its input and evidence.

```markdown
# check-N @ <sha> · <model and effort from the card, or unknown>
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `<command>` → <observed> |

## Defects
- <file and symbol>: <input> → <what happens> → <what should happen>. Evidence: run | traced, <output>

## Maybes
- <none, or for the human only>
```

## Route

Commit the receipt, then print the card from the hub's table. BROKEN rows and defects go to the
builder together, in one fix. BLOCKED and UNREACHABLE do not: no fix can reach them. Tell the human
what is blocked and what would unblock it. For UNREACHABLE, ask whether to delete the code or say
what reaches it. With only WAITING rows left, say the change is clear to pass the gate.
