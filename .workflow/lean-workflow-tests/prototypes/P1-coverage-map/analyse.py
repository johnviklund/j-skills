"""P1 throwaway: summarise a coverage map. Usage: python3 analyse.py <out-dir> [--subtests]"""
from collections import defaultdict
import json
from pathlib import Path
import sys

out = Path(sys.argv[1])
per = defaultdict(set)
for f in out.glob("*.json"):
    d = json.loads(f.read_text())
    test = d["test"]
    if "--subtests" not in sys.argv:
        test = test.split(" [")[0]
    per[test] |= {("L", *x) for x in d["lines"]} | {("B", *x) for x in d["branches"]}
per.pop("between", None)
total = set().union(*per.values())
owners = defaultdict(set)
for t, items in per.items():
    for i in items:
        owners[i].add(t)
for script in sorted({i[1] for i in total}):
    print(f"{script}: {sum(1 for i in total if i[1] == script and i[0] == 'L')} lines, "
          f"{sum(1 for i in total if i[1] == script and i[0] == 'B')} branch arms")
print()
rows = []
for t, items in sorted(per.items()):
    unique = [i for i in items if len(owners[i]) == 1]
    supers = [o for o in per if o != t and items <= per[o]]
    rows.append((t, len(items), len(unique), supers))
for t, n, u, supers in rows:
    short = t.replace("test_run_worktree.", "rw.").replace("test_check_run.", "cr.").replace("test_next_step.", "ns.")
    sup = ",".join(s.split(".")[-1] for s in supers[:2])
    print(f"{u:4d} unique {n:5d} items  {short}" + (f"  ⊆ {sup}" if supers else ""))
