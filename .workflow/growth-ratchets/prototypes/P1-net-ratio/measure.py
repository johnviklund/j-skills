"""P1 - which done tickets in cx-intelligence would each ratio rule flag? Read-only; usage: measure.py REPO"""
import re, subprocess, sys, glob, os
repo = sys.argv[1]
RECEIPTS = r"\.(md|txt)$|^[.]workflow/"
TEST_FILE = r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*$|_test\.[^/]*$|\.(test|spec)\.[^/]*$"
def git(*a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
def stats(sha):
    ca = cd = ta = td = 0
    for row in git("diff", "--numstat", f"{sha}^", sha).splitlines():
        a, d, p = row.split("\t", 2)
        if a == "-" or re.search(RECEIPTS, p): continue
        if re.search(TEST_FILE, p): ta += int(a); td += int(d)
        else: ca += int(a); cd += int(d)
    return ca, cd, ta, td
rows = []
for plan in sorted(glob.glob(f"{repo}/.workflow/*/plan.md")):
    slug = plan.split("/")[-2]; text = open(plan).read()
    if not re.search(r"^Created:\s*2026-10-(09|1\d)", text, re.M) and "2026-10-1" not in text[:300]: continue
    dm = re.search(r"^## Deviations\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    dev = dm.group(1) if dm else ""
    for blk in re.split(r"^(?=### T\d+ )", text, flags=re.M):
        m = re.match(r"### (T\d+) ", blk)
        lm = re.search(r"Lane: (\w+)", blk); sm = re.search(r"^Status: done @ ([0-9a-f]{7,40})", blk, re.M)
        if not (m and lm and sm): continue
        tid, lane, sha = m.group(1), lm.group(1), sm.group(1)
        if lane not in ("logic", "contract"): continue
        ca, cd, ta, td = stats(sha)
        rows.append((slug, tid, lane, ca, cd, ta, td, bool(re.search(r"\b%s\b" % tid, dev))))
fa = fn = fh = 0
print(f"{'run':34}{'tk':4}{'code+':>6}{'code-':>6}{'test+':>6}{'test-':>6}  added-rule  net-rule  hybrid  deviated")
for slug, tid, lane, ca, cd, ta, td, dv in rows:
    added = ta >= 50 and ta > 1.5 * ca
    tn, cn = ta - td, ca - cd
    net = tn >= 50 and tn > 1.5 * max(cn, 0)
    hyb = tn >= 50 and tn > 1.5 * ca
    fa += added; fn += net; fh += hyb
    if added or net or hyb or dv:
        print(f"{slug:34}{tid:4}{ca:6}{cd:6}{ta:6}{td:6}  {'FLAG' if added else '-':10}  {'FLAG' if net else '-':8}  {'FLAG' if hyb else '-':6}  {'skips' if dv else ''}")
print(f"tickets {len(rows)} · added-rule flags {fa} · net-rule flags {fn} · hybrid (tests net vs code added) flags {fh}")
runs = {}
for slug, tid, lane, ca, cd, ta, td, dv in rows:
    r = runs.setdefault(slug, [0, 0, 0, 0]); r[0] += ca - cd; r[1] += ta - td; r[2] += 1; r[3] += dv
print("run-level net (logic+contract tickets): slug · code net · tests net · tickets · deviated")
for s, r in runs.items(): print(f"  {s:34}{r[0]:6}{r[1]:6}{r[2]:4}{r[3]:4}")
print("run-level hybrid: tests net vs 1.5x code added (floor 100)")
agg = {}
for slug, tid, lane, ca, cd, ta, td, dv in rows:
    a = agg.setdefault(slug, [0, 0]); a[0] += ca; a[1] += ta - td
for s, (ca, tn) in agg.items():
    print(f"  {s:34} code+ {ca:5} tests net {tn:5}  {'FLAG' if tn >= 100 and tn > 1.5 * ca else '-'}")
