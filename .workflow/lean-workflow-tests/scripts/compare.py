"""Capture sorted receipts or compare them. Python 3, standard library only.

Run from this run folder:
  python3 scripts/compare.py --capture LABEL COVMAP_DIR [MUTANTS.json ...]
  python3 scripts/compare.py BASE LABEL
Only killed mutants are coverage obligations. All mutant outcomes remain in the receipt.
A partial per-script mutation receipt compares only its scripts; covmap always covers all three.
"""
from collections import Counter
import json
from pathlib import Path
import sys

SCRIPTS = ("check-run.py", "next-step.py", "run-worktree.py")


def capture(label, covdir, files):
    items, tests, cases = set(), set(), set()
    for path in Path(covdir).glob("*.json"):
        data = json.loads(path.read_text())
        if data["test"] == "between":
            continue
        test = data["test"].split(" [")[0]
        if test.count(".") == 2:
            tests.add(test)
            cases.add(data["test"])
        items.update("line " + " ".join(map(str, row)) for row in data["lines"])
        items.update("arm " + " ".join(map(str, row)) for row in data["branches"])
    # Outer test entries accompany subtest entries; count only the latter for those tests.
    cases = {c for c in cases if " [" in c or not any(k.startswith(c + " [") for k in cases)}
    rows = [f"# {len(tests)} tests; {len(cases)} cases"]
    counts = Counter(tuple(i.split()[:2]) for i in items)
    rows += [f"# {s}: {counts['line', s]} lines; {counts['arm', s]} arms" for s in SCRIPTS]
    Path(f"receipts/covmap-{label}.txt").write_text("\n".join(rows + sorted(items)) + "\n")
    results = [r for f in files for r in json.loads(Path(f).read_text())]
    ids = [r["id"] for r in results]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate mutant ids")
    counts, items = Counter(), set()
    for r in results:
        kind = "message" if r["desc"] == "message" else "ratio" if r["desc"].startswith("ratio->") else "P2"
        counts[r["file"], kind, r["status"]] += 1
        items.add(f"{r['status']} {r['file']} {kind} {r['id']}")
    rows = [f"# scope {s}" for s in sorted({r["file"] for r in results})] + [f"# {s} {k} {status}: {n}" for (s, k, status), n in sorted(counts.items())]
    Path(f"receipts/mutants-{label}.txt").write_text("\n".join(rows + sorted(items)) + "\n")
    print("\n".join(rows))


def read(kind, label):
    path = Path(f"receipts/{kind}-{label}.txt")
    return {line for line in path.read_text().splitlines() if line and not line.startswith("#")}


def compare(base, label):
    lost = set()
    for kind in ("covmap", "mutants"):
        before, after = read(kind, base), read(kind, label)
        scope = {line.split()[2] for line in Path(f"receipts/{kind}-{label}.txt").read_text().splitlines()
                 if line.startswith("# scope ")}
        if kind == "mutants" and not scope:
            raise ValueError(f"mutants-{label}.txt has no script scope")
        for script in SCRIPTS:
            if kind == "mutants" and script not in scope:
                continue
            for group in (("line", "arm") if kind == "covmap" else ("P2", "message", "ratio")):
                def selected(items):
                    return {i for i in items if i.split()[1] == script and
                            (i.split()[0] == group if kind == "covmap" else
                             i.split()[0] == "killed" and i.split()[2] == group)}
                missing = selected(before) - selected(after)
                print(f"{script} {kind} {group}: lost {len(missing)}")
                lost.update(missing)
    for item in sorted(lost):
        print("lost item:", item)
    return bool(lost)


if __name__ == "__main__":
    try:
        if len(sys.argv) >= 5 and sys.argv[1] == "--capture":
            capture(*sys.argv[2:4], sys.argv[4:])
        elif len(sys.argv) == 3:
            sys.exit(compare(*sys.argv[1:]))
        else:
            sys.exit("usage: compare.py BASE LABEL | --capture LABEL COVMAP_DIR MUTANTS.json ...")
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f"receipt error: {exc}")
