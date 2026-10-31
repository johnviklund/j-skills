"""P2 throwaway: summarise mutation results. Usage: python3 analyse.py <result.json>... [--cases]
Prints status counts per script, then each test (or case) with the mutants only it kills."""
from collections import Counter, defaultdict
import json
import sys

files = [a for a in sys.argv[1:] if not a.startswith("--")]
by_case = "--cases" in sys.argv
results = [r for f in files for r in json.load(open(f))]
for script in sorted({r["file"] for r in results}):
    c = Counter(r["status"] for r in results if r["file"] == script)
    print(script, dict(c))
killers = defaultdict(set)
ran = set()
for r in results:
    for k in (r.get("cases") or [] if by_case else r["killers"]):
        killers[k].add(r["id"])
    ran.update(r["tests"])
unique = Counter()
for r in results:
    ks = r.get("cases") if by_case else r["killers"]
    if by_case:
        # a test that failed without subtest detail counts as one case named after the test
        ks = list(ks or []) + [k for k in r["killers"] if not any(c.startswith(k + " (") for c in ks or [])]
    if len(ks) == 1:
        unique[ks[0]] += 1
names = set(killers) | (ran if not by_case else set())
print()
for name in sorted(names, key=lambda n: (unique[n], n)):
    short = name.replace("test_run_worktree.", "rw.").replace("test_check_run.", "cr.").replace("test_next_step.", "ns.")
    print(f"{unique[name]:3d} only-kills {len(killers[name]):4d} kills  {short}")
print()
for r in results:
    if r["status"] == "survived":
        print("survived", r["id"])
