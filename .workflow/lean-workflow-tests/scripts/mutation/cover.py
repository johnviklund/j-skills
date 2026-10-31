"""P2 throwaway: greedy set cover — the fewest tests (or cases) that keep every P1 line and
branch arm and every P2 kill. Usage: python3 cover.py <covmap-dir> <result.json>... [--cases]"""
import ast
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
by_case = "--cases" in sys.argv
items = defaultdict(set)


VARYING = re.compile(r"\b[0-9a-f]{40}\b|/tmp/tmp\w+")  # per-run shas and temp dirs


def case_key(test, desc):
    """Canonical case name from P1 '[msg{params}]' or P2 '[msg] (k=v)' descriptions."""
    if not by_case or not desc:
        return test
    return VARYING.sub("<v>", f"{test} {desc}")


for f in Path(args[0]).glob("*.json"):
    d = json.loads(f.read_text())
    m = re.match(r"(\S+)(?: \[(.*)\])?$", d["test"])
    test, sub = m.group(1), m.group(2)
    if test.count(".") != 2:
        continue
    desc = None
    if sub is not None:
        brace = sub.index("{")
        msg, params = sub[:brace], ast.literal_eval(sub[brace:])
        desc = " ".join(p for p in ([f"[{msg}]"] if msg else []) +
                        ([f"({', '.join(f'{k}={v!r}' for k, v in params.items())})"] if params else []))
    key = case_key(test, desc)
    items[key] |= {("L", *x) for x in d["lines"]} | {("B", *x) for x in d["branches"]}
for f in args[1:]:
    for r in json.load(open(f)):
        names = set(r["killers"])
        if by_case:
            names = {VARYING.sub("<v>", c) for c in r.get("cases") or []} | {k for k in r["killers"]
                                                 if not any(c.startswith(k + " ") for c in r.get("cases") or [])}
        for n in names:
            items[n].add(("K", r["id"]))
orphans = [k for k in items if all(i[0] == "K" for i in items[k])]
if orphans:
    print(f"warning: {len(orphans)} killing cases have no P1 entry, e.g. {orphans[0][:120]}")
universe = set().union(*items.values())
chosen, left = [], set(universe)
while left:
    best = max(items, key=lambda t: len(items[t] & left))
    if not items[best] & left:
        break
    chosen.append(best)
    left -= items[best]
methods = {k.split(" ")[0] for k in items}
print(f"{len(items)} {'cases' if by_case else 'tests'} ({len(methods)} methods) hold {len(universe)} items "
      f"({sum(1 for i in universe if i[0] == 'K')} kills); greedy cover keeps {len(chosen)}, "
      f"spread over {len({c.split(' ')[0] for c in chosen})} methods")
for mod in ("test_check_run", "test_next_step", "test_run_worktree"):
    total = sum(1 for k in items if k.startswith(mod))
    kept = sum(1 for k in chosen if k.startswith(mod))
    print(f"  {mod}: {total} → {kept}")
