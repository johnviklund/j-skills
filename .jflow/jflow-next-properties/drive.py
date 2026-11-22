"""Run the proof commands for jflow-next-properties from the repo root."""

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from time import monotonic


SKILL = Path(".github/skills/jflow")
TESTS = SKILL / "scripts/tests"
TEST = "test_next_properties.py"
PROPERTIES = ["-m", "unittest", "discover", "-s", str(TESTS), "-p", TEST]
GROUPS = {
    "historical": ("2f8aaa8", "38b1e04", "f6fb039"),
    "reruns": ("count-every-receipt", "any-yes"),
    "policy": ("first-cap", "edge-first", "edge-fix", "no-late"),
}
MUTATIONS = {
    "2f8aaa8": (r'- (none\.?|<none\b[^>]*>)\s*$', r'- <?none\b'),
    "38b1e04": (
        '            acceptances.append((m.group(1, 2), m.group(3), added))',
        r'            for item in re.findall(r"\b(Row|Defect) (\d+)\b", l):' '\n'
        '                acceptances.append((item, m.group(3), added))',
    ),
    "f6fb039": ("not added or after(created, added)", "True"),
    "count-every-receipt": (
        "counted = sum(1 for x, y in zip(shas, shas[1:]) if changed(repo, x, y) is not False)",
        "counted = len(receipts)",
    ),
    "count-blocked-or-waiting": (
        "counted = sum(1 for x, y in zip(shas, shas[1:]) if changed(repo, x, y) is not False)",
        'counted = sum(1 for x, y, r in zip(shas, shas[1:], receipts) if changed(repo, x, y) is not False'
        ' or (not r["defects"] and set(r["rows"]) <= {"PROVED", "BLOCKED", "WAITING"}'
        ' and set(r["rows"]) & {"BLOCKED", "WAITING"}))',
    ),
    "any-yes": (r'^Yes: {point}\b', r'^Yes: '),
    "first-cap": ("int(allowed[-1])", "int(allowed[0])"),
    "edge-first": ("elif stuck:  # before [edge] defects", "elif stuck and not edge:"),
    "edge-fix": ('elif edge:\n            step = "edge"',
                 'elif edge:\n            step, n, why = "fix", newest["n"], f"{name} has open defects"'),
    "no-late": ("and not accepted_late():", ":"),
    "skip-approach": (' and not yes("approach"):', " and False:"),
}


def run(args, cwd=Path("."), **variables):
    env = {key: value for key, value in os.environ.items() if key not in {"JFLOW_PROP_SEED", "JFLOW_PROP_RUNS"}}
    env.update(variables)
    return subprocess.run([sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True)


def passed(result):
    assert result.returncode == 0 and "Ran 1 test" in result.stderr, result.stderr


def failed(result):
    match = re.search(r"^AssertionError: (.*?)\nseed (\d+): rerun with JFLOW_PROP_SEED=.*?\nwhy: (.*?)\nrun: (\{.*?^\})",
                      result.stderr, re.M | re.S)
    assert result.returncode != 0 and match, result.stderr
    return match.groups()


def normalized(failure):
    # Separate git histories can assign different hashes to the same commits.
    hashes = {}
    summary = re.sub(r"\b[0-9a-f]{40}\b", lambda match: str(hashes.setdefault(match[0], len(hashes))),
                     failure[-1])
    return (*failure[:-1], summary)


def mutations(keys, replay=False, **variables):
    survivors = []
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        shutil.copytree(SKILL, root / SKILL, ignore=shutil.ignore_patterns("__pycache__"))
        path = root / SKILL / "scripts/jflow.py"
        original = path.read_text()
        for key in keys:
            old, new = MUTATIONS[key]
            assert original.count(old) == 1, key
            source = original.replace(old, new)
            if key == "38b1e04":
                sha_check = " and (named.startswith(sha) or sha.startswith(named))"
                assert source.count(sha_check) == 1
                source = source.replace(sha_check, "")
            path.write_text(source)
            shutil.rmtree(path.parent / "__pycache__", ignore_errors=True)
            result = run(PROPERTIES, root, **variables)
            if result.returncode == 0:
                passed(result)
                survivors.append(key)
                print(f"{key}=0 (buggy copy passed)")
                continue
            first = failed(result)
            seed = first[1]
            if replay:
                repeated = failed(run(PROPERTIES, root, JFLOW_PROP_SEED=seed, JFLOW_PROP_RUNS="1"))
                assert normalized(repeated) == normalized(first), (first, repeated)
                print(f"seed {seed} printed with run summary and reproduced the same failure")
            else:
                print(f"{key}=nonzero (seed {seed})")
    if survivors:
        raise SystemExit(1)


def count():
    # Count completed generate() calls without modifying the test.
    probe = """
import sys
import unittest
cases = []
def trace(frame, event, arg):
    if event == 'return' and frame.f_code.co_name == 'generate':
        if frame.f_globals.get('__name__') == 'test_next_properties':
            cases.append(arg)
sys.setprofile(trace)
unittest.main(module=None, exit=False, argv=['unittest', 'discover', '-s', sys.argv[1],
                                            '-k', 'test_generated_runs_follow_next_rules'])
print(len(cases))
"""
    started = monotonic()
    default = run(["-m", "unittest", "discover", "-s", str(TESTS), "-k", "test_generated_runs_follow_next_rules"])
    elapsed = monotonic() - started
    passed(default)
    counted = []
    for variables in ({}, {"JFLOW_PROP_RUNS": "51"}):
        result = run(["-c", probe, str(TESTS)], **variables)
        passed(result)
        assert result.stderr.strip().endswith("OK"), result.stderr
        counted.append(int(result.stdout.strip()))
    print(f"default={counted[0]} runs in {elapsed:.2f}s, override={counted[1]} runs")
    assert counted[0] >= 50 and elapsed < 10 and counted[1] > counted[0]


def stdlib():
    passed(run(["-I", *PROPERTIES]))
    tree = ast.parse((TESTS / TEST).read_text(), feature_version=(3, 9))
    imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
               for alias in node.names}
    imports.update(node.module.split(".")[0] for node in ast.walk(tree)
                   if isinstance(node, ast.ImportFrom) and node.level == 0)
    assert not imports - sys.stdlib_module_names, imports - sys.stdlib_module_names
    print("isolated unittest OK, 0 third-party imports, Python 3.9 AST OK")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "historical":
        passed(run(PROPERTIES))
        print("HEAD=0")
    if mode in GROUPS:
        mutations(GROUPS[mode])
    elif mode == "replay":
        mutations(("2f8aaa8",), replay=True)
    elif mode == "approach":
        mutations(("skip-approach",))
    elif mode == "blocked-rerun":
        mutations(("count-blocked-or-waiting",))
    elif mode in ("38b1e04", "edge-fix", "skip-approach"):
        seed = {"38b1e04": "59", "edge-fix": "81", "skip-approach": "105"}[mode]
        variables = {"JFLOW_PROP_SEED": seed, "JFLOW_PROP_RUNS": "1"}
        passed(run(PROPERTIES, **variables))
        mutations((mode,), **variables)
    elif mode == "count":
        count()
    elif mode == "stdlib":
        stdlib()
    else:
        raise SystemExit(f"unknown proof: {mode}")
