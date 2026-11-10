"""Checker driver for jflow-validate: `python3 .jflow/jflow-validate/drive.py [row|attack ...]`.

Clones the repo at HEAD into a temp folder, plants faults in copies of real runs there, and
prints one line per row. The clone keeps commit shas resolvable; this repo is never written.
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
BASE = "d53d8d1"
RUNS = ["drive-py-at-done", "jflow-config", "jflow-next", "receipt-evidence-cap", "wait-points"]
TMP = Path(tempfile.mkdtemp(prefix="jflow-validate-"))
CLONE = TMP / "clone"
subprocess.run(["git", "clone", "-q", str(REPO), str(CLONE)], check=True)
subprocess.run(["git", "-C", str(CLONE), "worktree", "add", "-q", str(TMP / "base"), BASE], check=True)
JF = CLONE / ".github/skills/jflow/scripts/jflow.py"
JF_BASE = TMP / "base/.github/skills/jflow/scripts/jflow.py"
SHA = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def jf(*args, script=JF):
    r = subprocess.run([sys.executable, str(script), *args, "--repo", str(CLONE)], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def copy(src, name, keep=None):
    """Copy run `src` to `name`; keep only receipts check-1..keep when given."""
    dst = CLONE / ".jflow" / name
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(CLONE / ".jflow" / src, dst)
    if keep is not None:
        for p in (dst / "receipts").glob("check-*.md"):
            if int(p.stem.split("-")[1]) > keep:
                p.unlink()
    return dst


def edit(path, old, new, count=1):
    text = path.read_text()
    assert old in text, (path, old)
    path.write_text(text.replace(old, new, count))


def row1():
    ok = total = 0
    for run in RUNS:
        total += 1
        rc, out = jf("validate", run, "spec")
        ok += rc == 0 and not out
        if rc or out:
            print("  fail spec", run, rc, out)
        for p in sorted((CLONE / ".jflow" / run / "receipts").glob("check-*.md")):
            k = int(p.stem.split("-")[1])
            copy(run, "r1", k)
            total += 1
            rc, out = jf("validate", "r1", "check")
            ok += rc == 0 and not out
            if rc or out:
                print("  fail", run, p.name, rc, out)
    print(f"1: {ok} of {total} rc=0 with no output")


SPEC_FAULTS = [
    ("Status", lambda s: edit(s, "Status: done", "Status: draft")),
    ("Base", lambda s: re_sub(s, r"^Base: \S+", "Base: deadbee")),
    ("section", lambda s: re_sub(s, r"^## Non-goals\n", "")),
    ("column", lambda s: edit(s, "| Pass signal |", "| Signal |")),
    ("Kind", lambda s: re_sub(s, r"\| new \| red \|", "| fresh | red |", 1)),
    ("new green", lambda s: re_sub(s, r"\| new \| red \|", "| new | green |", 1)),
    ("keep red", lambda s: re_sub(s, r"\| keep \| green \|", "| keep | red |", 1)),
    ("Gate", lambda s: re_sub(s, r"^- Gate: .*\n", "")),
]


def re_sub(path, pat, new, count=0):
    text = path.read_text()
    out, n = re.subn(pat, new, text, count=count, flags=re.M)
    assert n, (path, pat)
    path.write_text(out)


def row2():
    ok = 0
    for name, fault in SPEC_FAULTS:
        d = copy("wait-points", "r2")
        fault(d / "spec.md")
        rc, out = jf("validate", "r2", "spec")
        ok += rc == 1 and bool(out)
        print(f"  {name}: rc={rc} {out}")
    print(f"2: {ok} of {len(SPEC_FAULTS)} rc=1")


C = "receipts/check-1.md"
LONG = "`x` → " + "y" * 234  # 240 characters
RECEIPT_FAULTS = [
    ("header N", lambda d: edit(d / C, "# check-1 @", "# check-2 @")),
    ("sha", lambda d: edit(d / C, "@ 4121af0", "@ deadbee")),
    ("missing row", lambda d: re_sub(d / C, r"^\| 2 \|.*\n", "")),
    ("extra row", lambda d: edit(d / C, "| 9 | PROVED", "| 10 | PROVED | x |\n| 9 | PROVED")),
    ("verdict", lambda d: edit(d / C, "| 1 | PROVED", "| 1 | NOPE")),
    ("cell 241", lambda d: re_sub(d / C, r"^\| 1 \| PROVED \| .*\|$", "| 1 | PROVED | " + LONG + "z |")),
    ("defect 241", lambda d: re_sub(d / C, r"Evidence: .*$", "Evidence: " + LONG + "z")),
    ("defect K", lambda d: edit(d / C, "| 4 | BROKEN | defect 1 |", "| 4 | BROKEN | defect 7 |")),
    ("ACCEPTED", lambda d: edit(d / C, "| 1 | PROVED", "| 1 | ACCEPTED")),
    ("section", lambda d: edit(d / C, "## Maybes", "## Notes\n- x\n\n## Maybes")),
]


def row3():
    ok = 0
    for name, fault in RECEIPT_FAULTS:
        d = copy("wait-points", "r3", 1)
        fault(d)
        rc, out = jf("validate", "r3", "check")
        ok += rc == 1 and "check-1.md:" in out
        print(f"  {name}: rc={rc} {out}")
    d = copy("wait-points", "r3", 1)
    re_sub(d / C, r"^\| 1 \| PROVED \| .*\|$", "| 1 | PROVED | " + LONG + " |")
    rc, out = jf("validate", "r3", "check")
    print(f"3: {ok} of {len(RECEIPT_FAULTS)} rc=1 naming check-1.md:<line>; 240-char cell rc={rc} {out!r}")


def accept_copy(line):
    d = copy("wait-points", "r4")
    with open(d / "spec.md", "a") as f:
        f.write("\n## Accepted\n" + line + "\n")
    return jf("validate", "r4", "accept")


def row4():
    ok = 0
    for line in ['- Row 2 · missed · "fine" · 2026-11-10',
                 f'- Row 42 · missed · "fine" · 2026-11-10 · {SHA}',
                 '- Row 2 · missed · "fine" · 2026-11-10 · deadbee']:
        rc, out = accept_copy(line)
        ok += rc == 1
        print(f"  rc={rc} {out}")
    rc, out = accept_copy(f'- Row 2 · missed · "fine" · 2026-11-10 · {SHA}')
    print(f"4: {ok} of 3 rc=1; good line rc={rc} {out!r}")


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def row5():
    for step, fault in [("check", lambda d: edit(d / C, "| 1 | PROVED", "| 1 | NOPE")),
                        ("spec", lambda d: edit(d / "spec.md", "Status: done", "Status: draft"))]:
        d = copy("wait-points", "r5", 1)
        fault(d)
        before = digest(d / "run.jsonl")
        rc, out = jf("record", "r5", step, "--model", "m", "--effort", "e")
        print(f"  broken {step}: rc={rc} same={digest(d / 'run.jsonl') == before} {out}")
    lines = []
    for script in (JF, JF_BASE):
        d = copy("wait-points", "r5", 1)
        rc, out = jf("record", "r5", "check", "--model", "m", "--effort", "e", script=script)
        recs = [json.loads(l) for l in (d / "run.jsonl").read_text().splitlines() if l.strip()]
        lines.append((rc, len(recs), [{k: v for k, v in r.items() if k not in ("at", "skill")} for r in recs]))
    print(f"5: valid receipt HEAD rc={lines[0][0]} n={lines[0][1]}, Base rc={lines[1][0]} n={lines[1][1]}, same={lines[0][2] == lines[1][2]}")


def row6():
    d = copy("wait-points", "r6")
    edit(d / "receipts/check-2.md", "| 2 | PROVED", "| 2 | NOPE")
    n0 = len((d / "run.jsonl").read_text().splitlines())
    rc, out = jf("record", "r6", "build", "--model", "m", "--effort", "e")
    last = (d / "run.jsonl").read_text().splitlines()
    print(f"6: rc={rc} lines {n0} -> {len(last)} last step={json.loads(last[-1])['step']} {out}")


def row7():
    same = total = 0
    for run in RUNS + ["jflow-validate"]:
        for cmd in ("next", "summary"):
            total += 1
            a, b = jf(cmd, run, "--json"), jf(cmd, run, "--json", script=JF_BASE)
            same += a == b
            if a != b:
                print("  differ", cmd, run, a, b)
    print(f"7: {same} of {total} byte-identical")


def attack():
    """Defect-citation shapes on BROKEN rows, HEAD validate."""
    for cell in ["defect 1, defect 9", "defect 9, defect 1", "defect 1,defect 9", "Defect 1, defect 9",
                 "defect 1 and defect 9", "defects 1, 9", "defect 1, 9", "defect 01", "defect 1",
                 "`grep defect 9 x` → 1 line"]:
        d = copy("wait-points", "ra", 1)
        edit(d / C, "| 4 | BROKEN | defect 1 |", f"| 4 | BROKEN | {cell} |")
        rc, out = jf("validate", "ra", "check")
        print(f"  {cell!r}: rc={rc} {out}")


ROWS = {"1": row1, "2": row2, "3": row3, "4": row4, "5": row5, "6": row6, "7": row7, "attack": attack}
try:
    for key in sys.argv[1:] or list(ROWS):
        ROWS[key]()
finally:
    shutil.rmtree(TMP, ignore_errors=True)
