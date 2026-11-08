"""Checker's driver for receipt-evidence-cap. Run from the repo root: python3 .jflow/receipt-evidence-cap/drive.py row4"""
import pathlib
import sys
import tempfile

sys.path.insert(0, ".github/skills/jflow/scripts")
import jflow  # noqa: E402

# A receipt in the new template: PROVED, BROKEN and BLOCKED rows, one numbered defect, "- none" maybes.
RECEIPT = """# check-1 @ 3ad0bd2 · claude-opus-5.5 high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `grep -n x f` → 1 hit |
| 2 | BROKEN | defect 1 |
| 3 | BLOCKED | no token |

## Defects
- 1. `a.py` `f`: input → bad → good. Evidence: run, `python3 a.py` → Traceback

## Maybes
- none
"""


def row4():
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d, "check-1.md")
        path.write_text(RECEIPT, encoding="utf-8")
        print(jflow.receipt_fields(path))


if __name__ == "__main__":
    {"row4": row4}[sys.argv[1]]()
