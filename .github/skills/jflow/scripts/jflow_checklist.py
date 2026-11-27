"""jflow.py checklist: print the RELIABILITY.md items that the diff Base..HEAD triggers.

An item is a Markdown checklist line with indented fields:

    - [ ] Retries must stay bounded
      Paths: src/net/**/*.py, *.retry.ts
      Match: \\bretry\\(
      Check: every retry loop has a max attempt count and a backoff
      Incident: https://github.com/org/repo/issues/12

Paths are globs (* stays inside one folder, ** crosses folders, [ch] is a class, a glob without /
matches the file name anywhere). Match is a Python regex searched in each added or removed line.
With both, one changed file must match Paths and have a changed line that matches Match. Items
start with -, * or +.
Standard library, Python 3.9+.
"""
import re
import subprocess
from pathlib import Path

ITEM = re.compile(r"^[-*+] \[[ xX]\] (.+)$")
FIELD = re.compile(r"^\s+(Paths|Match|Check|Incident):\s*(.*)$")
LINK = re.compile(r"https?://\S+|(?:[\w.-]+/[\w.-]+)?#\d+")


def add_args(sub):
    p = sub.add_parser("checklist", help="print the RELIABILITY.md items the run's diff triggers")
    p.add_argument("slug", nargs="?", help="the run whose spec's Base: starts the diff")
    p.add_argument("--base", help="the commit the diff starts from, instead of a slug")
    p.add_argument("--repo", default=".")
    p.add_argument("--config")


def glob_re(glob):
    out = "" if "/" in glob.strip("/") else "(?:.*/)?"
    for part in re.split(r"(\*\*/?|\*|\?|\[!?\]?[^]]*\])", glob.strip("/")):
        if part[:1] == "[" and len(part) > 2:  # a class, as git reads one: [ch], [a-z], [!0-9], [^0-9]
            neg = part[1] in "!^"
            out += ("[^/" if neg else "[") + part[1 + neg:-1].replace("\\", "\\\\").replace("[", "\\[") + "]"
        else:
            out += {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}.get(part, re.escape(part))
    return re.compile(out + r"\Z")


def parse(text):
    """Items as dicts; SystemExit naming the item for one that is incomplete or has a bad regex."""
    items, cur = [], None
    for n, line in enumerate(text.splitlines(), 1):
        if m := ITEM.match(line):
            cur = {"title": m[1].strip(), "line": n}
            items.append(cur)
        elif cur and (f := FIELD.match(line)):
            cur[f[1]] = f[2].strip()
        elif not line.startswith((" ", "\t")) and line.strip():
            cur = None
    for it in items:
        where = f"RELIABILITY.md:{it['line']}: item {it['title']!r}"
        if not (it.get("Paths") or it.get("Match")):
            raise SystemExit(f"{where} has no trigger: add Paths:, Match: or both")
        if not it.get("Check"):
            raise SystemExit(f"{where} has no Check:")
        if not LINK.search(it.get("Incident", "")):
            raise SystemExit(f"{where} has no Incident: link (a URL or #N)")
        try:
            it["re"] = re.compile(it["Match"]) if it.get("Match") else None
        except re.error as error:
            raise SystemExit(f"{where} has an invalid Match: regex: {error}")
        it["globs"] = [glob_re(g) for g in re.split(r"[,\s]+", it.get("Paths", "")) if g]
    return items


def git(repo, *args):
    r = subprocess.run(["git", "--literal-pathspecs", "-C", str(repo), "-c", "core.quotePath=false", *args], capture_output=True)
    if r.returncode:
        raise SystemExit("checklist: git " + args[0] + " failed: "
                         + (r.stderr.decode("utf-8", "replace").strip().splitlines() or ["?"])[0])
    return r.stdout.decode("utf-8", "surrogateescape")


def changed_lines(repo, base, path):
    out = git(repo, "diff", "--no-ext-diff", "--no-color", "--no-renames", "-U0", f"{base}..HEAD", "--", path)
    hunks = out.split("\n@@", 1)[1:]  # file headers such as "--- a/x" come before the first hunk
    return [ln[1:] for ln in "".join(hunks).splitlines() if ln[:1] in "+-"]


def run(repo, base, spec=None):
    if spec is not None:
        m = re.search(r"^Base:\s*([0-9a-f]{7,40})\s*$", spec, re.M)
        if not m:
            raise SystemExit("checklist: the run's spec has no Base: sha")
        base = base or m[1]
    if not base:
        raise SystemExit("checklist needs a slug or --base")
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", base + "^{commit}"],
                      capture_output=True).returncode:
        raise SystemExit(f"checklist: Base {base[:40]!r} is not a commit in this repo")
    f = Path(repo) / "RELIABILITY.md"
    if not f.is_file():
        print("checklist: no RELIABILITY.md, nothing to check")
        return 0
    items = parse(f.read_text("utf-8"))
    files = [p for p in git(repo, "diff", "--no-renames", "--name-only", "-z", f"{base}..HEAD").split("\0") if p]
    lines, hits = {}, []
    for it in items:
        for p in files:
            if it["globs"] and not any(g.match(p) for g in it["globs"]):
                continue
            if it["re"]:
                if p not in lines:
                    lines[p] = changed_lines(repo, base, p)
                ln = next((ln for ln in lines[p] if it["re"].search(ln)), None)
                if ln is None:
                    continue
                hits.append((it, f"{p}: {ln.strip()[:120]}"))
            else:
                hits.append((it, p))
            break
    print(f"checklist: {len(hits)} of {len(items)} RELIABILITY.md items match {base[:12]}..HEAD")
    for it, why in hits:
        print(f"\n- [ ] {it['title']}\n  Check: {it['Check']}\n  Incident: {it['Incident']}\n  Matched: {why}")
    return 0
