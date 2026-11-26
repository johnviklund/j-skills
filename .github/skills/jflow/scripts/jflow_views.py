"""The two views a jflow stop shows above its options. Standard library, Python 3.9+."""
import re


def views(receipts, notes, run):
    """One Checker view line from the newest receipt and one Builder view line from the newest note.

    receipts: the receipt paths in order; notes: the lines of notes.md; run: the run folder,
    relative to the repo. A blank line leads them. The checker's line is its first defect, else its
    first row that is not PROVED, else its first Maybe, else that nothing is open. The builder's line
    is the newest note line that records no decision.
    """
    out = []
    if receipts:
        text = receipts[-1].read_text("utf-8")
        maybes = [l for l in text.partition("\n## Maybes")[2].splitlines()
                  if l.startswith("- ") and not re.fullmatch(r"- (none\.?|<none[^>]*>)\s*", l, re.I)]
        said = (re.findall(r"^- \d+\. .*", text, re.M) + re.findall(r"^\|\s*\d+\s*\|\s*(?!PROVED)[A-Z].*", text, re.M)
                + [f"Maybe: {l[2:]}" for l in maybes] + ["every row PROVED, no defects or Maybes"])
        out.append(f"Checker view ({run}/receipts/{receipts[-1].name}): {short(said[0])}")
    said = [l for l in notes if re.match(r"(?!#|Yes:|Checks allowed:|Live done:)\S", l)]
    if said:
        out.append(f"Builder view (notes.md): {short(said[-1])}")
    return [""] + out if out else []


def short(line):
    line = line.strip("-| ")
    return line if len(line) <= 200 else line[:199] + "…"
