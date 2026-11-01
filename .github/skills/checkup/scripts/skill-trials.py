#!/usr/bin/env python3
"""Report skill trials without editing evidence. Requires only Python 3."""
import argparse
from pathlib import Path
import re


def rows(path, trialing=True):
    result = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not re.match(r"\| 20\d\d-", line):
            continue
        cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
        if len(cells) != 6:
            raise ValueError(f"{path}:{number}: expected 6 cells, got {len(cells)}")
        date, skill, change, source, trial, outcome = (c.strip() for c in cells)
        if not trialing or outcome == "trialing":
            names = [s.removesuffix(" (new)").strip() for s in skill.split(" · ")]
            result.append(dict(date=date, skill=skill, names=names, change=change,
                               source=source, trial=trial, saves=0))
    return result


def count_saves(trials, repos, all_rows):
    for repo in repos:
        for path in sorted((repo / ".workflow").glob("*/learnings.md")):
            for number, line in enumerate(path.read_text().splitlines(), 1):
                tag = re.search(r"\[saved→skill\] (\d{4}-\d{2}-\d{2}) (\S+)(.*?) — ", line)
                if not tag:
                    continue
                date, skill, words = tag.groups()
                matches_row = lambda r: (r["date"] == date and skill in r["names"]
                                        and words.strip().casefold() in r["change"].casefold())
                matches = [r for r in trials if matches_row(r)]
                if len(matches) == 1:
                    matches[0]["saves"] += 1
                elif matches or not any(matches_row(r) for r in all_rows):
                    print(f"⚠️ tag {path.relative_to(repo)}:{number} matches {len(matches)} rows; add words of the change")


def worklogs(repos):
    entries = []
    for repo in repos:
        path = repo / "WORKLOG.md"
        if not path.exists():
            continue
        for block in re.split(r"(?m)^## ", path.read_text())[1:]:
            date = re.match(r"\d{4}-\d{2}-\d{2}", block)
            cycles = re.search(r"(\d+) review cycles", block)
            deviations = re.search(r"(\d+) deviations", block)
            skills = re.search(r"(?m)^- Skills: (.+)", block)
            if date and cycles and deviations and skills:
                names = re.findall(r"([\w.-]+)@", skills[1])
                entries.append((date[0], names, int(cycles[1]) + int(deviations[1])))
    return sorted(entries, key=lambda entry: entry[0])


def report(row, sweep, entries):
    count, unit = row["trial"].split(" · ")[0].split(maxsplit=1)
    runs = [e for e in entries if set(row["names"]).intersection(e[1])]
    before = [e[2] for e in runs if e[0] < row["date"]][-int(count):]
    after = [e[2] for e in runs if e[0] > row["date"]][:int(count)]
    mean = lambda values: f"{sum(values) / len(values):.1f}" if values else "n/a"
    better = bool(before and after and sum(after) / len(after) < sum(before) / len(before))
    numbers = ("numbers better" if better else "numbers not better" if before and after
               else "numbers unavailable") + f" (before {mean(before)} → after {mean(after)})"
    insurance = "insurance:" in row["source"]
    saves = f'{row["saves"]} save' + ("" if row["saves"] == 1 else "s")
    label = "insurance" if insurance else "keep" if row["saves"] or better else "candidate"
    words = row["change"].split()
    change = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
    if sweep:
        detail = f" · {numbers}" if entries else ""
        print(f'{label} · {row["date"]} · {row["skill"]} · {saves} · {row["change"]}{detail}')
    elif "runs" not in unit:
        print(f'⚠️ {row["date"]} {row["skill"]} · {change} · open · count {unit} by hand')
    elif len(after) == int(count):
        reason = row["source"] if insurance else saves if row["saves"] else numbers
        verdict = f"kept · {reason}" + (f" · {numbers}" if insurance or row["saves"] else "")
        if label == "candidate":
            verdict = f"0 saves · {numbers} · removal candidate → workflow improve {row['names'][0]}"
        print(f'{"⚠️" if label == "candidate" else "✅"} {row["date"]} {row["skill"]} · {change} · trial complete · {verdict}')



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
        archive = args.impact.with_name("SKILL-IMPACT_ARCHIVE.md")
        all_rows = rows(args.impact, trialing=False)
        if archive.exists():
            all_rows += rows(archive, trialing=False)
        count_saves(trials, repos, all_rows)
        entries = worklogs(repos)
        for row in trials:
            report(row, args.sweep, entries)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
