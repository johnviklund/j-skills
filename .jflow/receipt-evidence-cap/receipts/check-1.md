# check-1 @ 3ad0bd2 · claude-opus-5.5 high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | Read `references/check.md:61`: "Each Evidence cell holds at most 240 characters: the command plus the one output line that decides the verdict." The template row says the same. |
| 2 | PROVED | Read `references/check.md:63`: "each defect's `Evidence:` part also holds at most 240 characters". Template has `\| 2 \| BROKEN \| defect 1 \|` and `- 1. ... Evidence:` capped. |
| 3 | PROVED | `grep -rn "quoted here" .github/skills/jflow` → no output, exit 1. `check.md:64`: "Quote a command that reruns as written ... raw output stays in the temp folder." |
| 4 | PROVED | `python3 .jflow/receipt-evidence-cap/drive.py row4` → `{'n': 1, 'sha': '3ad0bd2', 'rows': {'PROVED': 1, 'BROKEN': 1, 'BLOCKED': 1}, 'defects': 1, 'maybes': 0}` |
| 5 | PROVED | `grep -n "carried from check-N" .github/skills/jflow/references/check.md` → `38:` ... "as their evidence" |
| 6 | PROVED | `git diff --name-only 01f9bba..HEAD -- . ':(exclude).jflow'` → `.github/skills/jflow/references/check.md` only |

## Defects
- 1. `references/check.md` receipt rule, "A BROKEN row cites its defect number instead of repeating the evidence": a row that runs and misses its pass signal while the attack pass finds nothing, such as row 3 run at Base → the checker must invent a defect or leave the cell with no evidence → the rule should say what a BROKEN row with no defect holds, for example its own capped command and output line. Evidence: traced, `git show 01f9bba:.github/skills/jflow/references/check.md | grep -c "quoted here"` → `1`, so row 3 at Base is BROKEN with no defect to cite.

## Maybes
- Wrong-vendor note does not apply: the builder was GPT-6.1 Sol per `notes.md` and `run.jsonl`, so this Opus check is independent.
- A row whose input is a scratch fixture, like row 4, cannot quote a rerunnable command under 240 characters without `drive.py`. This check wrote `drive.py` for that. `check.md` could say so outright.
