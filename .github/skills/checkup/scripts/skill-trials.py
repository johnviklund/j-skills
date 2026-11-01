#!/usr/bin/env python3
"""Report skill trials without editing evidence. Requires only Python 3."""
import argparse
from pathlib import Path
import re


def rows(path):
    result = []
    for line in path.read_text().splitlines():
        if not re.match(r"\| 20\d\d-", line):
            continue
        date, skill, change, source, trial, outcome = (c.strip() for c in line.strip("|").split("|"))
        if outcome == "trialing":
            names = [s.removesuffix(" (new)").strip() for s in skill.split(" · ")]
            result.append(dict(date=date, skill=skill, names=names, change=change,
                               source=source, trial=trial, saves=0))
    return result


def count_saves(trials, repos):
    for repo in repos:
        for path in sorted((repo / ".workflow").glob("*/learnings.md")):
            for number, line in enumerate(path.read_text().splitlines(), 1):
                tag = re.search(r"\[saved→skill\] (\d{4}-\d{2}-\d{2}) (\S+)(.*?) — ", line)
                if not tag:
                    continue
                date, skill, words = tag.groups()
                matches = [r for r in trials if r["date"] == date and skill in r["names"]
                           and words.strip().casefold() in r["change"].casefold()]
                if len(matches) == 1:
                    matches[0]["saves"] += 1
                else:
                    print(f"⚠️ tag {path.relative_to(repo)}:{number} matches {len(matches)} rows; add words of the change")


def report(row, sweep):
    if sweep:
        label = "insurance" if "insurance:" in row["source"] else "keep" if row["saves"] else "candidate"
        saves = f'{row["saves"]} save' + ("" if row["saves"] == 1 else "s")
        print(f'{label} · {row["date"]} · {row["skill"]} · {saves} · {row["change"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", action="store_true", help="label every trialing row")
    parser.add_argument("--impact", type=Path,
                        default=Path(__file__).resolve().parents[2] / "workflow/SKILL-IMPACT.md")
    parser.add_argument("repos", nargs="*", type=Path, help="evidence repos, default: current directory")
    args = parser.parse_args()
    repos = list(dict.fromkeys(p.resolve() for p in (args.repos or [Path(".")])))
    try:
        for repo in repos:
            if not repo.is_dir():
                parser.error(f"evidence repo is not a directory: {repo}")
        trials = rows(args.impact)
        count_saves(trials, repos)
        for row in trials:
            report(row, args.sweep)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
