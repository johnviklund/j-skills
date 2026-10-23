"""P1 - what would a run-level tests/code gate flag? Read-only; usage: measure.py REPO [REPO...]
Range per run: plan.md Base .. its last `done @` ticket sha. Receipts and .workflow/ excluded."""
import re, subprocess, sys, glob
RECEIPTS = r"\.(md|txt)$|^[.]workflow/"
TEST_FILE = r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*$|_test\.[^/]*$|\.(test|spec)\.[^/]*$"
def git(repo, *a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
for repo in sys.argv[1:]:
    print(f"== {repo}\n{'run':36}{'code+':>7}{'codeN':>7}{'testN':>7}{'ratio':>7}  A(N/added)  B(N/net)  ticket-errors")
    for plan in sorted(glob.glob(f"{repo}/.workflow/*/plan.md")):
        t = open(plan).read()
        if not re.search(r"^Created:\s*2026-10-(1[7-9]|2\d)", t, re.M): continue
        base = re.search(r"^Base:\s*([0-9a-f]{7,40})", t, re.M)
        shas = re.findall(r"^Status: done @ ([0-9a-f]{7,40})", t, re.M)
        if not base or not shas: continue
        last = max(shas, key=lambda s: int(git(repo, "rev-list", "--count", s) or 0))
        ca = cd = tn = 0
        for row in git(repo, "diff", "--numstat", base.group(1), last).splitlines():
            a, d, p = row.split("\t", 2)
            if a == "-" or re.search(RECEIPTS, p): continue
            if re.search(TEST_FILE, p): tn += int(a) - int(d)
            else: ca += int(a); cd += int(d)
        cn = ca - cd
        A = tn >= 100 and tn > 1.5 * ca
        B = tn >= 100 and tn > 1.5 * max(cn, 0)
        waived = len(re.findall(r"Ratio waived:\s*T\d+", t))
        print(f"{plan.split('/')[-2]:36}{ca:7}{cn:7}{tn:7}{(tn / ca if ca else 0):7.2f}  {'FLAG' if A else '-':10}  {'FLAG' if B else '-':8}  waivers {waived}")
