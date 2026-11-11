#!/usr/bin/env python3
"""Mechanical checks for a roadmap file in the `roadmap` skill's format.

Usage:
    roadmap.py check FILE [--repo PATH ...] [--product PATH]
    roadmap.py next FILE

`check` prints one line per finding and exits 1 when any `error:` line was printed, 0 otherwise.
`error:` lines are format problems a script reading the file would trip on. `stale:` lines are
freshness findings for `roadmap tidy` to raise with the human; they do not fail the check.
`--repo PATH` names a repo whose `.jflow/SLUG/` run folders show which items started or finished.
`--product PATH` names the north-star file; it defaults to PRODUCT.md beside FILE. When it exists,
every item's `Serves:` must name one of its headings, and each `###` outcome under its
`## The desired state` section should have at least one open item.

`next` prints the Next up list with each item's status.

Python 3.9 or later, standard library only.
"""
import argparse
import os
import re
import sys

GROUPS = ("Features", "Bugs", "Design", "Architecture", "Tooling", "Measurement")
REQUIRED = ("Status", "Problem", "Solved when", "Budget", "Run")
OPTIONAL = ("Serves", "Why now", "Options", "Out of scope", "After", "Open for spec")
OUTCOMES = "The desired state"  # the PRODUCT.md section whose ### headings are the outcomes
# Next up answers "where do I start". Past five lines it turns into a second backlog.
NEXT_MAX = 5

SLUG = r"[a-z0-9][a-z0-9.-]*"
ITEM_RE = re.compile(rf"^### ({SLUG}) · (\S.*)$")
NEXT_RE = re.compile(rf"^\d+\. ({SLUG}) · (\S.*)$")
FIELD_RE = re.compile(r"^([A-Z][a-z]*(?: [a-z]+)*): (.*)$")
STATUS_RE = re.compile(r"^(open|started|blocked: \S.*|done \d{4}-\d{2}-\d{2} [0-9a-f]{7,40})$")
SECTION_RE = re.compile(r"^## (.+?)\s*$")


class Roadmap:
    def __init__(self):
        self.next = []  # (line number, slug)
        self.items = {}  # slug -> dict(line, group, fields)
        self.errors = []
        self.stale = []


def parse(text):
    rm = Roadmap()
    section = None
    item = None
    last_field = None
    seen_next = False
    for n, line in enumerate(text.splitlines(), 1):
        m = SECTION_RE.match(line)
        if m:
            section, item, last_field = m.group(1), None, None
            if section == "Next up":
                seen_next = True
            elif section not in GROUPS:
                rm.errors.append(f"line {n}: section '## {section}' is not a group; groups: {', '.join(GROUPS)}")
            elif not seen_next:
                rm.errors.append(f"line {n}: '## {section}' comes before '## Next up'")
            continue
        if section == "Next up":
            m = NEXT_RE.match(line)
            if m:
                rm.next.append((n, m.group(1)))
            elif line.strip() and not line.startswith("  "):
                rm.errors.append(f"line {n}: Next up lines read '1. SLUG · why it is next'")
            continue
        if section not in GROUPS:
            continue  # preamble or an unknown section, already reported
        if line.startswith("### "):
            m = ITEM_RE.match(line)
            if not m:
                rm.errors.append(f"line {n}: item headings read '### SLUG · outcome', with a kebab-case slug")
                item = None
                continue
            slug = m.group(1)
            if slug in rm.items:
                rm.errors.append(f"line {n}: slug '{slug}' is used twice, first at line {rm.items[slug]['line']}")
            item = {"line": n, "group": section, "fields": {}}
            rm.items[slug] = item
            last_field = None
            continue
        if item is None or not line.strip():
            continue
        if line.startswith("  ") and last_field:
            item["fields"][last_field] += " " + line.strip()
            continue
        m = FIELD_RE.match(line)
        if m and m.group(1) in REQUIRED + OPTIONAL:
            last_field = m.group(1)
            item["fields"][last_field] = m.group(2).strip()
        else:
            rm.errors.append(f"line {n}: unknown item line; fields: {', '.join(REQUIRED + OPTIONAL)}")
    if not seen_next:
        rm.errors.append("no '## Next up' section")
    return rm


def archive_slugs(path):
    stem, ext = os.path.splitext(path)
    archive = f"{stem}_ARCHIVE{ext}"
    if not os.path.exists(archive):
        return set()
    with open(archive, encoding="utf-8") as f:
        return {m.group(1) for m in (ITEM_RE.match(line) for line in f) if m}


def done(item):
    return item["fields"].get("Status", "").startswith("done ")


def after(item):
    raw = item["fields"].get("After", "none")
    return [] if raw.strip() == "none" else [s.strip() for s in raw.split(",") if s.strip()]


def check_items(rm, archived):
    for slug, item in rm.items.items():
        where = f"line {item['line']} {slug}"
        for field in REQUIRED:
            if not item["fields"].get(field):
                rm.errors.append(f"{where}: missing '{field}:'")
        status = item["fields"].get("Status")
        if status and not STATUS_RE.match(status):
            rm.errors.append(f"{where}: Status reads open, started, 'blocked: why' or 'done YYYY-MM-DD SHA'")
        for dep in after(item):
            if dep not in rm.items and dep not in archived:
                rm.errors.append(f"{where}: After names '{dep}', which is in neither the roadmap nor its archive")
        if done(item):
            rm.stale.append(f"{where}: done, move it to the archive")


def check_next(rm):
    if len(rm.next) > NEXT_MAX:
        rm.errors.append(f"Next up holds {len(rm.next)} items; at most {NEXT_MAX}")
    earlier = set()
    for n, slug in rm.next:
        item = rm.items.get(slug)
        if item is None:
            rm.errors.append(f"line {n}: Next up names '{slug}', which is not an item")
            continue
        if done(item):
            rm.stale.append(f"line {n}: Next up names '{slug}', which is done")
        for dep in after(item):
            dep_item = rm.items.get(dep)
            if dep_item and not done(dep_item) and dep not in earlier:
                rm.stale.append(f"line {n}: '{slug}' waits for '{dep}', which is open and not earlier in Next up")
        earlier.add(slug)


def run_status(repo, slug):
    """'done', 'started' or None, from the repo's jflow run folder for this slug."""
    spec = os.path.join(repo, ".jflow", slug, "spec.md")
    if not os.path.exists(spec):
        return None
    with open(spec, encoding="utf-8") as f:
        head = f.read(2000)  # Status sits in the first lines; 2 KB is well past it
    return "done" if re.search(r"^Status: done\b", head, re.M) else "started"


def product_headings(path):
    """(every heading, the outcomes under OUTCOMES) of PRODUCT.md, lower-cased; None when it is missing."""
    if not os.path.exists(path):
        return None
    headings, outcomes, in_outcomes = set(), [], False
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^(#{1,6}) (.+?)\s*$", line)
            if not m:
                continue
            level, text = len(m.group(1)), m.group(2)
            headings.add(text.lower())
            if level <= 2:
                in_outcomes = level == 2 and text == OUTCOMES
            elif level == 3 and in_outcomes:
                outcomes.append(text)
    return headings, outcomes


def check_product(rm, path):
    found = product_headings(path)
    if found is None:
        rm.stale.append(f"no {os.path.basename(path)} beside the roadmap: the bootstrap skill writes one")
        return
    headings, outcomes = found
    served = set()
    for slug, item in rm.items.items():
        serves = item["fields"].get("Serves")
        if not serves:
            rm.errors.append(f"line {item['line']} {slug}: missing 'Serves:', the PRODUCT.md outcome it moves")
        elif serves.lower() not in headings:
            rm.errors.append(f"line {item['line']} {slug}: Serves '{serves}' is not a heading in PRODUCT.md")
        elif not done(item):
            served.add(serves.lower())
    for outcome in outcomes:
        if outcome.lower() not in served:
            rm.stale.append(f"PRODUCT.md outcome '{outcome}' has no open item")


def check_repos(rm, repos):
    for repo in repos:
        if not os.path.isdir(repo):
            rm.errors.append(f"--repo {repo}: no such folder")
            continue
        name = os.path.basename(os.path.abspath(repo))
        for slug, item in rm.items.items():
            state = run_status(repo, slug)
            status = item["fields"].get("Status", "")
            if state == "done" and not done(item):
                rm.stale.append(f"line {item['line']} {slug}: its jflow run in {name} is done, the item says '{status}'")
            elif state == "started" and status == "open":
                rm.stale.append(f"line {item['line']} {slug}: its jflow run in {name} has started, the item says 'open'")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        sys.exit(f"error: cannot read {path}: {e.strerror}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a roadmap file.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    c.add_argument("--repo", action="append", default=[])
    c.add_argument("--product")
    nx = sub.add_parser("next")
    nx.add_argument("file")
    args = ap.parse_args(argv)

    rm = parse(load(args.file))
    if args.cmd == "next":
        if not rm.next:
            print("Next up is empty")
        for i, (_, slug) in enumerate(rm.next, 1):
            item = rm.items.get(slug)
            status = item["fields"].get("Status", "?") if item else "not an item"
            print(f"{i}. {slug} · {status}")
        return 0

    check_items(rm, archive_slugs(args.file))
    check_next(rm)
    check_repos(rm, args.repo)
    check_product(rm, args.product or os.path.join(os.path.dirname(os.path.abspath(args.file)), "PRODUCT.md"))
    for line in rm.errors:
        print(f"error: {line}")
    for line in rm.stale:
        print(f"stale: {line}")
    return 1 if rm.errors else 0


if __name__ == "__main__":
    sys.exit(main())
