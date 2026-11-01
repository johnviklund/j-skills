# T3 confirmation
Runner: agent after approval. Risk: cheap. This repo only.
Review every row in notes/t3-choices.md; approve recommendations or give row-number exceptions.
Recommended: 11 keep; 26 candidate; no insurance. All rows have 0 saves.
On approval, run from the repo root:
```sh
python3 .github/skills/checkup/scripts/skill-trials.py --sweep . > .workflow/retire-on-no-signal/receipts/t3-sweep.txt
```
Check 37 labels and 0 tag warnings; remove home-path examples before committing the receipt.
Record each answer in decisions.md. Confirmed keeps become kept with numbers and date.
Insurance requires the incident in From. Candidates stay trialing. No rule is removed.
Verify the final sweep has no keep line. Add this change's impact row after the 37-row receipt check.
