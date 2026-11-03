#!/usr/bin/env python3
"""Mutate the Python lines changed since a commit and run a test command against each mutant.

Usage: mutate.py --base <sha> [--path P ...] [--repo .] [--jobs N] [--timeout S] [--list] -- <test command>
Each mutant flips one comparison, and/or, not, any/all, if/while test, bool or int on a changed
line of a non-test .py file, uncommitted and untracked work included. Mutants run in throwaway
git worktrees, never in the checkout. Exit 0: every mutant killed; 1: survivors; 2: setup error.
Needs Python 3 and git.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import queue
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

SWAP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
        ast.GtE: ast.Gt, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is}
# The test-file pattern review's size count uses, plus conftest.py.
TEST = re.compile(r"(^|/)(tests?/|test_[^/]*$|conftest\.py$)|_test\.|\.test\.|\.spec\.")
SKIP = re.compile(r"^\.workflow/|\.(md|txt)$")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def untracked(root):
    return git(root, "ls-files", "--others", "--exclude-standard").splitlines()


def changed(root, base, paths):
    """({.py path: changed line numbers}, [other changed code paths]) since base, working tree included."""
    new = set(untracked(root))
    names = git(root, "diff", "--name-only", "--diff-filter=AM", base).splitlines() + sorted(new)
    lines, other = {}, []
    for name in dict.fromkeys(names):
        if SKIP.search(name) or TEST.search(name) or paths and not any(name == p or name.startswith(p.rstrip("/") + "/") for p in paths):
            continue
        if not name.endswith(".py"):
            other.append(name)
        elif name in new:
            lines[name] = set(range(1, len((root / name).read_text().splitlines()) + 1))
        else:
            hunks = re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", git(root, "diff", "-U0", base, "--", name), re.M)
            lines[name] = {n for h in hunks for n in range(int(h[1]), int(h[1]) + int(h[2] or 1))}
    return lines, other


def mutants(root, name, wanted):
    src = (root / name).read_text()
    rows = src.splitlines(keepends=True)
    # AST columns are UTF-8 byte offsets; text edits need character offsets.
    char = lambda line, col: len(rows[line - 1].encode()[:col].decode())
    out = []
    for node in ast.walk(ast.parse(src, name)):
        new, target = [], node
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in SWAP:
                    ops = list(node.ops)
                    ops[i] = SWAP[type(op)]()
                    new.append((f"{type(op).__name__}->{SWAP[type(op)].__name__}",
                                ast.unparse(ast.Compare(node.left, ops, node.comparators))))
        elif isinstance(node, ast.BoolOp):
            other = ast.Or() if isinstance(node.op, ast.And) else ast.And()
            new.append((f"{type(node.op).__name__}->{type(other).__name__}", ast.unparse(ast.BoolOp(other, node.values))))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            new.append(("drop-not", ast.unparse(node.operand)))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("any", "all"):
            other = "all" if node.func.id == "any" else "any"
            new.append((f"{node.func.id}->{other}", ast.unparse(ast.Call(ast.Name(other), node.args, node.keywords))))
        elif isinstance(node, ast.Constant) and type(node.value) is bool:
            new.append((f"{node.value}->{not node.value}", repr(not node.value)))
        elif isinstance(node, ast.Constant) and type(node.value) is int:
            new.append((f"{node.value}->{node.value + 1}", repr(node.value + 1)))
        elif isinstance(node, (ast.If, ast.While)) and not isinstance(node.test, (ast.Compare, ast.BoolOp, ast.UnaryOp)):
            target = node.test
            new.append(("negate-test", f"not ({ast.get_source_segment(src, node.test)})"))
        if not new or target.lineno not in wanted:
            continue
        seg = (target.lineno, char(target.lineno, target.col_offset),
               target.end_lineno, char(target.end_lineno, target.end_col_offset))
        out.extend({"file": name, "line": seg[0], "seg": seg, "desc": desc, "text": f"({text})"} for desc, text in new)
    return out


def apply(src, seg, text):
    rows = src.splitlines(keepends=True)
    l1, c1, l2, c2 = seg
    return "".join(rows[:l1 - 1]) + rows[l1 - 1][:c1] + text + rows[l2 - 1][c2:] + "".join(rows[l2:])


def worktree(root, path):
    """A detached worktree at HEAD carrying the checkout's uncommitted and untracked files."""
    git(root, "worktree", "add", "-q", "--detach", str(path), "HEAD")
    for name in git(root, "diff", "--name-only", "HEAD").splitlines() + untracked(root):
        if (root / name).is_file():
            (path / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / name, path / name)
        else:
            (path / name).unlink(missing_ok=True)


def passes(command, cwd, timeout):
    """True when the command exits 0, False when it fails, None when it times out."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}  # a stale .pyc would hide a mutant
    if timeout:  # a CPU cap ends a looping mutant even when a hard kill of this script orphans it
        command = f"ulimit -t {int(2 * timeout) + 10}; {command}"
    proc = subprocess.Popen(command, shell=True, cwd=cwd, env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        return proc.wait(timeout=timeout) == 0
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="commit the change starts from")
    parser.add_argument("--path", action="append", default=[], help="only this file or folder, from the repo root")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--jobs", type=int, default=1, help="mutants run at once, one worktree each")
    parser.add_argument("--timeout", type=float, help="seconds per mutant; default 3x the clean run, at least 30")
    parser.add_argument("--list", action="store_true", help="print the mutants without running them")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- <test command>")
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        root = Path(git(args.repo, "rev-parse", "--show-toplevel").strip())
        git(root, "rev-parse", "--verify", "-q", f"{args.base}^{{commit}}")
        lines, other = changed(root, args.base, args.path)
        found = [m for name in sorted(lines) for m in mutants(root, name, lines[name])]
    except subprocess.CalledProcessError as error:
        print(f"mutate: {error.stderr.strip() or f'{args.base} is not a commit'}", file=sys.stderr)
        return 2
    except SyntaxError as error:
        print(f"mutate: {error.filename}:{error.lineno}: {error.msg}", file=sys.stderr)
        return 2
    for name in other:
        print(f"not mutated: {name} (not Python): invert one condition by hand (tests.md)")
    if args.list:
        for m in found:
            print(f"{m['file']}:{m['line']} {m['desc']}: {m['text']}")
        return 0
    if not command:
        print("mutate: give the test command after --", file=sys.stderr)
        return 2
    command = command[0] if len(command) == 1 else shlex.join(command)
    # A stopped run still removes its worktrees: SIGTERM unwinds through the finally below.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    tmp = Path(tempfile.mkdtemp(prefix="mutate-"))
    trees = []
    try:
        # A stop mid `git worktree add` would leave a worktree cleanup cannot remove; it lands after setup.
        signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})
        try:
            for i in range(max(1, min(args.jobs, len(found) or 1))):
                trees.append(tmp / f"w{i}")
                worktree(root, trees[-1])
        finally:
            signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGTERM})
        start = time.monotonic()
        if not passes(command, trees[0], None):
            print("mutate: the test command fails before any mutation", file=sys.stderr)
            return 2
        timeout = args.timeout or max(30.0, 3 * (time.monotonic() - start))
        free = queue.Queue()
        for tree in trees:
            free.put(tree)

        def run(m):
            tree = free.get()
            path = tree / m["file"]
            src = path.read_text()
            try:
                path.write_text(apply(src, m["seg"], m["text"]))
                return m, passes(command, tree, timeout)
            finally:
                path.write_text(src)
                free.put(tree)

        pool = ThreadPoolExecutor(len(trees))
        try:
            results = list(pool.map(run, found))
        finally:
            pool.shutdown(cancel_futures=True)
    finally:
        for tree in trees:
            subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", str(tree)], capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    survived = [m for m, result in results if result]
    timed_out = sum(result is None for _, result in results)
    for m in survived:
        print(f"survived {m['file']}:{m['line']} {m['desc']}: {m['text']}")
    print(f"mutants {len(results)} · killed {len(results) - len(survived)} · survived {len(survived)}"
          f" · timed out {timed_out} (counted killed)")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
