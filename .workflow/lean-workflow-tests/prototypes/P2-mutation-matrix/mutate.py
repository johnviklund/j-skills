"""P2 throwaway: which tests kill which mutants of the workflow scripts.

Usage: python3 mutate.py <scripts-dir> <covmap-dir> <out.json> [--list] [--workers N] [--only FILE]
Each mutant changes one AST node; only the tests whose P1 coverage reaches the mutated line run.
"""
import argparse
import ast
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

SWAP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
        ast.GtE: ast.Gt, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}


def mutants(path):
    src = path.read_text()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        new = []
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in SWAP:
                    m = ast.Compare(node.left, list(node.ops), node.comparators)
                    m.ops[i] = SWAP[type(op)]()
                    new.append((f"{type(op).__name__}->{SWAP[type(op)].__name__}", m))
        elif isinstance(node, ast.BoolOp):
            other = ast.Or() if isinstance(node.op, ast.And) else ast.And()
            new.append((f"{type(node.op).__name__}->{type(other).__name__}", ast.BoolOp(other, node.values)))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            new.append(("drop-not", node.operand))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("any", "all"):
            other = "all" if node.func.id == "any" else "any"
            new.append((f"{node.func.id}->{other}", ast.Call(ast.Name(other, ast.Load()), node.args, node.keywords)))
        elif isinstance(node, ast.Constant) and type(node.value) is int:
            new.append((f"{node.value}->{node.value + 1}", ast.Constant(node.value + 1)))
        elif isinstance(node, ast.Constant) and type(node.value) is bool:
            new.append((f"{node.value}->{not node.value}", ast.Constant(not node.value)))
        elif isinstance(node, (ast.If, ast.While)) and not isinstance(node.test, (ast.Compare, ast.BoolOp, ast.UnaryOp)):
            new.append(("negate-test", None))
        for desc, m in new:
            if desc == "negate-test":
                seg = (node.test.lineno, node.test.col_offset, node.test.end_lineno, node.test.end_col_offset)
                text = "(not (" + ast.get_source_segment(src, node.test) + "))"
            else:
                seg = (node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                text = "(" + ast.unparse(m) + ")"
            out.append({"id": f"{path.name}:{seg[0]}:{seg[1]}:{desc}", "file": path.name, "line": seg[0],
                        "seg": seg, "text": text, "desc": desc})
    return src, out


def apply(src, seg, text):
    lines = src.splitlines(keepends=True)
    (l1, c1, l2, c2) = seg
    before = "".join(lines[:l1 - 1]) + lines[l1 - 1][:c1]
    after = lines[l2 - 1][c2:] + "".join(lines[l2:])
    return before + text + after


def coverage(covdir):
    per = defaultdict(set)
    for f in Path(covdir).glob("*.json"):
        d = json.loads(f.read_text())
        test = d["test"].split(" [")[0]
        if test.count(".") == 2:
            for name, line in d["lines"]:
                per[(name, line)].add(test)
    return per


# unittest prints "<name> (<id>)", then " [msg]" for subTest(msg) and " (k=v)" for subTest(k=v)
FAIL = re.compile(r"^(?:FAIL|ERROR): \S+ \(([\w.]+)\) ?(.*)$", re.M)


def run(scripts, m, tests, sources):
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "scripts"
        shutil.copytree(scripts, copy, ignore=shutil.ignore_patterns("__pycache__"))
        mutated = apply(sources[m["file"]], m["seg"], m["text"])
        try:
            compile(mutated, m["file"], "exec")
        except SyntaxError:
            return dict(m, tests=tests, killers=[], status="syntax")
        (copy / m["file"]).write_text(mutated)
        start = time.time()
        try:
            r = subprocess.run([sys.executable, "-m", "unittest", *tests], cwd=copy / "tests",
                               capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return dict(m, tests=tests, killers=["timeout"], status="timeout", seconds=600)
        found = FAIL.findall(r.stderr)
        killers = sorted({test for test, _ in found})
        cases = sorted({f"{test} {case}" for test, case in found if case})
        status = "killed" if r.returncode else "survived"
        if r.returncode and not killers:
            status, killers = "killed-unparsed", ["?"]
        return dict(m, tests=tests, killers=killers, cases=cases, status=status, seconds=round(time.time() - start, 1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scripts"), p.add_argument("covmap"), p.add_argument("out")
    p.add_argument("--list", action="store_true"), p.add_argument("--workers", type=int, default=4)
    p.add_argument("--only")
    p.add_argument("--tests", help="comma-separated test ids: run only these, where they reach the line")
    a = p.parse_args()
    scripts = Path(a.scripts).resolve()
    cov = coverage(a.covmap)
    sources, todo, uncovered = {}, [], []
    for name in ("check-run.py", "next-step.py", "run-worktree.py"):
        if a.only and name != a.only:
            continue
        src, ms = mutants(scripts / name)
        sources[name] = src
        for m in ms:
            tests = sorted(cov.get((name, m["line"]), ()))
            if a.tests:
                tests = [t for t in tests if t in a.tests.split(",")]
            (todo if tests else uncovered).append((m, tests))
    print(f"{len(todo)} covered mutants, {len(uncovered)} on unreached lines", file=sys.stderr)
    if a.list:
        for m, tests in todo:
            print(m["id"], len(tests))
        return
    results = [dict(m, tests=[], killers=[], status="unreached") for m, _ in uncovered]
    done = 0
    with ThreadPoolExecutor(a.workers) as pool:
        for res in pool.map(lambda mt: run(scripts, mt[0], mt[1], sources), todo):
            results.append(res)
            done += 1
            if done % 25 == 0:
                print(f"{done}/{len(todo)}", file=sys.stderr, flush=True)
                Path(a.out).write_text(json.dumps(results, indent=0))
    Path(a.out).write_text(json.dumps(results, indent=0))


if __name__ == "__main__":
    main()
