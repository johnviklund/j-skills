#!/usr/bin/env python3
"""Account for removed SKILL.md sentences. Requires Python 3 and git.

Run: sentence-ledger.py SKILL-DIR BASE
Duplicate ledger: notes/dups-NAME.txt, tab-separated removed sentence, repo path,
and retained phrase. Whitespace is normalized; words and punctuation stay exact.
"""
import pathlib
import re
import subprocess
import sys


def normalize(text):
    return " ".join(text.split())


def sentences(text):
    # Reuse check-explainer.py's sentence boundary; paragraphs retain list seams.
    for block in re.split(r"\n\s*\n|\n(?=\s*(?:[-*]|\d+\.)\s)", text):
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", normalize(block)):
            if sentence:
                yield sentence


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                   stderr=subprocess.PIPE)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    skill, base = pathlib.Path(sys.argv[1]).resolve(), sys.argv[2]
    try:
        root = pathlib.Path(git(skill, "rev-parse", "--show-toplevel").strip())
        relative = skill.relative_to(root)
        old = git(root, "show", f"{base}:{relative}/SKILL.md")
        hub = (skill / "SKILL.md").read_text()
        refs = list((skill / "references").rglob("*.md"))
        before = set(git(root, "ls-tree", "-r", "--name-only", base, "--", str(relative)).splitlines())
        duplicates = {}
        ledger = root / ".workflow/lean-skill-hubs/notes" / f"dups-{skill.name}.txt"
        for row in ledger.read_text().splitlines() if ledger.exists() else []:
            removed, path, kept = row.split("\t")
            if normalize(kept) not in normalize((root / path).read_text()):
                raise ValueError(f"{ledger}: retained phrase missing in {path}: {kept}")
            duplicates[normalize(removed)] = (path, kept)
        current = normalize(hub)
        disclosed = [normalize(path.read_text()) for path in refs]
        moved = duplicate = unaccounted = 0
        for sentence in sentences(old):
            if sentence in current:
                continue
            if any(sentence in text for text in disclosed):
                moved += 1
            elif sentence in duplicates:
                duplicate += 1
            else:
                unaccounted += 1
                print(f"unaccounted: {sentence}")
        errors = 0
        for path in refs:
            if str(path.relative_to(root)) in before:
                continue
            name = path.relative_to(skill).as_posix()
            if not re.search(r"\]\(" + re.escape(name) + r"(?:#[^)]*)?\)", hub):
                print(f"{name}: not linked from SKILL.md")
                errors += 1
            lines = path.read_text().splitlines()
            # agent-docs requires contents above ~100 lines; the first 12 expose it on a short read.
            if len(lines) > 100 and not re.search(r"contents", "\n".join(lines[:12]), re.I):
                print(f"{name}: missing contents list")
                errors += 1
        print(f"moved {moved} · duplicate {duplicate} · unaccounted {unaccounted}")
        return bool(unaccounted or errors)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ledger: {error}; check SKILL-DIR, BASE, and duplicate rows", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
