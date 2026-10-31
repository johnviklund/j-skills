"""P3 throwaway: how a test's time splits between fixture git calls and the script under test.
Usage: python3 split.py <tests-dir>  — runs the workflow suite with subprocess.run timed by argv[0]."""
from collections import defaultdict
import subprocess
import sys
import time
import unittest

spent, calls = defaultdict(float), defaultdict(int)
real = subprocess.run


def timed(args, *a, **k):
    start = time.perf_counter()
    try:
        return real(args, *a, **k)
    finally:
        kind = "script" if str(args[0]) == sys.executable else str(args[0]).rsplit("/", 1)[-1]
        if kind == "script":
            kind += ":" + str(args[1]).rsplit("/", 1)[-1]
        spent[kind] += time.perf_counter() - start
        calls[kind] += 1


subprocess.run = timed
start = time.perf_counter()
suite = unittest.defaultTestLoader.discover(sys.argv[1])
unittest.TextTestRunner(verbosity=0).run(suite)
total = time.perf_counter() - start
for kind in sorted(spent, key=spent.get, reverse=True):
    print(f"{kind:28} {calls[kind]:5d} calls {spent[kind]:6.1f} s  {spent[kind] / total:5.1%}")
print(f"{'total':28} {'':11} {total:6.1f} s")
