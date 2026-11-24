#!/usr/bin/env python3
"""Record, validate and summarize jflow runs. Usage: jflow.py COMMAND -h.

Standard library, Python 3.9+. Readers ignore unknown keys and steps.
"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FLOW = json.loads((SKILL / "flow.json").read_text("utf-8"))
STEPS = tuple(FLOW["steps"])
RULES = dict.fromkeys(("public_paid_needs_human", "checker_read_only", "no_secrets"), True)
BUILDER_STEPS = ("fix", "live", "accept", "done")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
DOC_EXT = re.compile(r"\.(md|mdx|txt|rst|adoc)$", re.I)
CODE_EXT = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|jsx|go|rs|java|kt|swift|rb|php|cs|c|h|cc|cpp|hpp|sh|bash|zsh|sql|"
                      r"css|scss|html|vue|svelte|lua|dart|scala|ex|exs|clj|pl|r|m)$", re.I)
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*$|_test\.[^/]+$|\.(test|spec)\.[^/]+$")


def secret(v):
    if isinstance(v, dict):
        return any(secret(k) or secret(x) for k, x in v.items())
    if isinstance(v, (list, tuple)):
        return any(secret(x) for x in v)
    return isinstance(v, str) and bool(re.search(
        r"(?<![\w-])(?:sk-ant-|sk-(?=[\w-]*\d|\w+(?![\w-]))[A-Za-z0-9_-]{20,}|gh[pousr]_|AKIA)|[A-Za-z0-9_+/=]{40,}", v))


def record_value(v):
    if secret(v):
        raise SystemExit("secret-like argument refused")
    return v


def seats(repo, explicit):
    def bad(c, m):
        if c:
            raise ValueError(m)

    cfg, ext = {}, explicit or os.environ.get("JFLOW_CONFIG")
    for p in [SKILL / "config.json", repo / ".jflow/config.json"] + ([Path(ext)] if ext else []):
        if p == repo / ".jflow/config.json" and not p.exists():
            continue
        try:
            d = json.loads(p.read_text("utf-8"))
            bad(secret(d), "secret-like value refused")
            bad(not isinstance(d, dict) or type(d.get("schema_version")) is not int or d["schema_version"] != 1, "schema_version must be 1")
            bad(set(d) - {"schema_version", "seats", "rules", "different_vendors", "other_vendor", "mode"}, "unknown config field")
            rules = d.get("rules", {})
            bad(not isinstance(rules, dict), "rules must be an object")
            for r, on in rules.items():
                bad(r not in RULES or on is not True, "locked rule " + (r if r in RULES else "unknown"))
            bad("different_vendors" in d and type(d["different_vendors"]) is not bool, "different_vendors must be boolean")
            entries = d.get("seats", {})
            bad(not isinstance(entries, dict) or set(entries) - set(STEPS), "seats must name flow steps")
            for e in list(entries.values()) + ([d["other_vendor"]] if "other_vendor" in d else []):
                pend = [e]
                while pend:
                    s = pend.pop()
                    bad(not isinstance(s, dict) or set(s) != {"model", "vendor", "effort", "fallback"}, "each seat needs model, vendor, effort and fallback")
                    bad(any(not isinstance(s[k], str) or not s[k].strip() for k in ("model", "vendor", "effort")), "seat model, vendor and effort must be nonempty strings")
                    if s["fallback"] is not None:
                        pend.append(s["fallback"])
            cfg.setdefault("seats", {}).update(entries)
            cfg.update({k: v for k, v in d.items() if k != "seats"})
        except (OSError, ValueError, RecursionError) as err:
            raise SystemExit(f"{p}: {err if type(err) is ValueError else 'cannot read valid config JSON'}")
    return cfg


def seat_for(repo, step, a):
    cfg, meta = seats(repo, a.config), FLOW["steps"][step]
    chosen = cfg["seats"].get(step, cfg["seats"][meta["seat"]])
    builder = a.builder_vendor or cfg["seats"]["build"]["vendor"]
    if step == "check" and cfg["different_vendors"] and chosen["vendor"] == builder:
        chosen = cfg["other_vendor"]
        if chosen["vendor"] == builder:
            raise SystemExit("other_vendor must differ from the builder vendor")
    return dict(chosen, **meta, step=step, rules=RULES)


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], check=check, capture_output=True, text=True)
    return p.stdout.strip() if check else p


def born(repo, path):
    return git(repo, "log", "-1", "--diff-filter=A", "--format=%H", "--", str(path))


def section(text, heading):
    m = re.search(rf"^## {heading}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return [l for l in (m.group(1).splitlines() if m else [])
            if l.startswith("- ") and not re.match(r"- (none\.?|<none\b[^>]*>)\s*$", l, re.I)]


def changed(repo, a, b):
    try:
        return bool(git(repo, "diff", "--name-only", f"{a}..{b}", "--", ".", ":(exclude).jflow"))
    except subprocess.CalledProcessError:
        return None


def receipts_of(run):
    return sorted(run.glob("receipts/check-*.md"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))


def receipt_fields(path):
    text, rows = path.read_text("utf-8"), {}
    for v in re.findall(r"^\|\s*\d+\s*\|\s*([A-Z]+)\s*\|", text, re.M):
        rows[v] = rows.get(v, 0) + 1
    sha = re.search(r"^# check-\d+ @ ([0-9a-f]{7,40})\b", text, re.M)
    return {"n": int(re.sub(r"\D", "", path.stem)), "sha": sha.group(1) if sha else None, "rows": rows,
            "defects": len([d for d in section(text, "Defects") if "carried from" not in d.lower()]),
            "maybes": len(section(text, "Maybes"))}


def read_records(run):
    p = run / "run.jsonl"
    return [json.loads(l) for l in p.read_text("utf-8").splitlines() if l.strip()] if p.exists() else []


def validate(repo, run, step):
    errs, path = [], run / "spec.md"

    def need(ok, n, msg):
        if not ok:
            errs.append(f"{path.relative_to(repo)}:{n}: {msg}")

    def read():
        try:
            return path.read_text("utf-8")
        except (OSError, UnicodeError):
            need(False, 1, "cannot read file")
            return ""

    def sha(v, n=1):
        need(re.fullmatch(r"[0-9a-f]{7,40}", v)
             and git(repo, "rev-parse", "--verify", v + "^{commit}", check=False).returncode == 0, n, "unknown commit sha")

    def body(t, h):
        on = False
        for n, l in enumerate(t.splitlines(), 1):
            if l.startswith("## "):
                on = l.strip() == "## " + h
            elif on and l.strip():
                yield n, l

    def table(lines, hdr):
        rows, seen, cols = {}, False, hdr.split("|")
        for n, l in lines:
            if not l.startswith("|"):
                continue
            cs = [c.strip() for c in re.split(r"(?<!\\)\|", l.strip())[1:-1]]
            if not seen:
                need(cs == cols, n, "expected columns " + hdr)
                seen = True
            elif all(re.fullmatch(r":?-+:?", c) for c in cs):
                continue
            elif len(cs) != len(cols) or not cs[0].isdigit():
                need(False, n, "bad table row")
            else:
                need(cs[0] not in rows, n, "duplicate row " + cs[0])
                rows[cs[0]] = (n, cs)
        need(rows, 1, "missing table rows")
        return rows

    spec = read()
    rows = table(body(spec, "Proof"), "#|Claim|Surface|Check|Pass signal|Kind|Base")
    if step == "spec":
        need(re.search(r"^Status: (ready|done)[ \t]*$", spec, re.M), 1, "invalid Status")
        base = re.search(r"^Base: (\S+)[ \t]*$", spec, re.M)
        sha(base[1] if base else "")
        for h in ("Problem", "Goals", "Non-goals", "Constraints", "Proof", "Human checks"):
            need(re.search(rf"^## {h}[ \t]*$", spec, re.M), 1, "missing section " + h)
        need(any(re.fullmatch(r"- Gate: .+", l) for _, l in body(spec, "Constraints")), 1, "missing Gate line")
        if (repo / "PRODUCT.md").exists():
            head = spec.split("\n## ")[0]
            m = re.search(r"^Serves: (.+?)[ \t]*$", head, re.M)
            outs, fence = ["none"], ""
            for l in (repo / "PRODUCT.md").read_text("utf-8").splitlines():
                f = re.match(r" {0,3}(`{3,}|~{3,}|<!--)", l)
                if fence:
                    fence *= not ("-->" in l if fence == "<!--" else re.fullmatch(rf" {{0,3}}{fence[0]}{{{len(fence)},}}\s*", l))
                elif f:
                    fence = "" if f[1] == "<!--" and "-->" in l else f[1]
                elif h := re.fullmatch(r" {0,3}###[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*", l):
                    outs.append(h[1])
            need(m and m[1] in outs, head[:m.start()].count("\n") + 1 if m else 1, "Serves names no ### outcome in PRODUCT.md")
        for n, cs in rows.values():
            k, b = cs[-2:]
            need(k in ("new", "keep", "live") and b == ("green" if k == "keep" else "red"), n, "invalid Kind or Base")
    elif step == "accept":
        for n, l in body(spec, "Accepted"):
            m = re.fullmatch(r'- (Row|Defect) (\d+) · .+ · ".+" · \d{4}-\d{2}-\d{2} · (\S+)', l)
            need(m, n, "invalid Accepted line")
            if m:
                sha(m[3], n)
                need(m[1] != "Row" or m[2] in rows, n, "Accepted names unknown row " + m[2])
    else:
        rs = receipts_of(run)
        path = rs[-1] if rs else run / "receipts/check-N.md"
        text = read()
        m = re.match(r"# check-(\d+) @ (\S+) · .+", text)
        need(m and path.stem == "check-" + m[1], 1, "missing receipt or bad header " + path.stem)
        if m:
            sha(m[2])
        need(not path.exists() or path.stat().st_size <= 3000, 1, "receipt over 3,000 bytes")
        if len(rs) > 1:
            rel, files = os.fsencode(run.relative_to(repo).as_posix()), []
            try:
                prev = born(repo, rs[-2]) or receipt_fields(rs[-2])["sha"]
                files = subprocess.check_output(
                    ["git", "-C", str(repo), "diff", "--name-only", "--no-renames", "-z", f"{prev}", "HEAD"],
                    stderr=subprocess.PIPE).split(b"\0")
            except (OSError, UnicodeError):
                need(False, 1, f"cannot read {rs[-2].stem}")
            except subprocess.CalledProcessError:
                pass
            need(any(f and (not f.startswith(b".jflow/") or f in (rel + b"/notes.md", rel + b"/spec.md")) for f in files),
                 1, f"no new input since {rs[-2].stem}: commit code, notes.md or spec.md first")
        need(re.findall(r"^## (.+)$", text, re.M) == ["Defects", "Maybes"], 1, "missing or extra section: Defects, Maybes")
        defs = set()
        for n, l in body(text, "Defects"):
            m = re.match(r"- (\d+)\. (?:\[([^]]*)\]\s)?.+? Evidence: (.+)$", l)
            need(m and m[1] not in defs and len(m[3]) <= 240 and m[2] in (None, "use", "edge") or re.fullmatch(
                r"- (none\.?|<none[^>]*>)", l, re.I), n, "invalid defect (or repeat), tag or Evidence >240")
            defs.add(m and m[1])
        vs = table(enumerate(text.split("\n## ", 1)[0].splitlines(), 1), "#|Verdict|Evidence")
        for k in rows.keys() - vs.keys():
            need(False, 1, "missing row " + k)
        acc = {m[1] for _, l in body(spec, "Accepted") if (m := re.fullmatch(r"- Row (\d+) ·.*· [0-9a-f]{7,40}", l))}
        for k, (n, cs) in vs.items():
            _, v, ev = cs
            need(k in rows and v in ("PROVED", "BROKEN", "BLOCKED", "UNREACHABLE", "WAITING", "ACCEPTED"), n, "unknown row or verdict " + k)
            need(0 < len(ev) <= 240, n, "Evidence empty or over 240")
            if v == "BROKEN" and re.fullmatch(r"(?i)defect \d+(,\s*defect \d+)*", ev):
                for d in re.findall(r"\d+", ev):
                    need(d in defs, n, f"unknown defect {d}")
            need(v != "ACCEPTED" or k in acc, n, "row " + k + " not under Accepted")
    return errs


def summary(repo, run):
    recs, spec = read_records(run), (run / "spec.md").read_text("utf-8")
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    if not base:
        raise SystemExit("summary: spec.md has no Base line")
    sp = str(run / "spec.md")
    dones = git(repo, "log", "--format=%H", "-G", "^Status: done", "--", sp).splitlines()
    end = dones[-1] + "^" if dones else "HEAD"
    ls = dict.fromkeys(("net_code", "tests", "docs", "other"), 0)
    for l in git(repo, "diff", "--numstat", f"{base.group(1)}..{end}", "--", ".", ":(exclude).jflow").splitlines():
        add, dele, p = l.split("\t", 2)
        if add != "-":
            ls["tests" if TEST_PATH.search(p) else "net_code" if CODE_EXT.search(p) else "docs" if DOC_EXT.search(p) else "other"] += int(add) - int(dele)
    proof = re.search(r"^## Proof\s*$(.*?)(?=^## |\Z)", spec, re.M | re.S)
    started = git(repo, "log", "--reverse", "--format=%cI", "--", sp).splitlines()
    ended = dt.datetime.fromisoformat(git(repo, "log", "-1", "--format=%cI", dones[-1])) if dones else dt.datetime.now(dt.timezone.utc)
    hours = round((ended - dt.datetime.fromisoformat(started[0])).total_seconds() / 3600, 1) if started else None
    checks = [receipt_fields(p) for p in receipts_of(run)]
    shas = [c["sha"] for c in checks] + [end]
    fixes = sum(1 for a, b in zip(shas, shas[1:]) if a and changed(repo, a, b))
    steps = [r for r in recs if r.get("step") in STEPS]
    sess = (max(1, sum(r["step"] == "spec" for r in steps)) + bool(checks or any(ls.values()))
            + len(checks) + sum(r["step"] in BUILDER_STEPS and r.get("session") == "fresh" for r in steps))
    return {"sessions": sess if steps else None, "checks": len(checks),
            "fix_rounds": max(fixes, sum(r["step"] == "fix" for r in steps)),
            "rows": len(re.findall(r"^\|\s*\d+\s*\|", proof.group(1), re.M)) if proof else 0,
            "accepted": len(section(spec, "Accepted")), "defects": sum(c["defects"] for c in checks),
            "first_check_clean": (checks[0]["defects"] == 0 and set(checks[0]["rows"]) <= {"PROVED", "WAITING", "ACCEPTED"}) if checks else None,
            **ls, "hours_spec_to_end": hours}


def line(s):
    sess = s["sessions"] if s["sessions"] is not None else "?"
    chk = "check clean" if s["defects"] == 0 else f"check {s['defects']} defects"
    return (f"jflow: {sess} sessions · {s['fix_rounds']} fix rounds · {s['rows']} rows · {s['accepted']} accepted"
            f" · {chk} · net code {s['net_code']:+d} · tests {s['tests']:+d} · docs {s['docs']:+d}")


def next_step(repo, run, a):
    slug = run.name
    spec = (run / "spec.md").read_text("utf-8") if (run / "spec.md").exists() else ""
    st = re.search(r"^Status:\s*(\w+)", spec, re.M)
    status = st.group(1) if st else None
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    base_sha = base.group(1) if base else None
    rel = run.relative_to(repo).as_posix()
    spec_rel, notes_rel = f"{rel}/spec.md", f"{rel}/notes.md"
    notes = git(repo, "show", f"HEAD:{notes_rel}", check=False).stdout

    def after(x, y):
        return bool(x and y) and not git(repo, "merge-base", "--is-ancestor", x, y, check=False).returncode

    def spec_body(rev):
        p = git(repo, "show", f"{rev}:{spec_rel}", check=False)
        return re.split(r"^## Accepted[ \t]*$", p.stdout, maxsplit=1, flags=re.M)[0].rstrip() if not p.returncode else None

    spec_c = next((c for c in git(repo, "log", "--format=%H", "--", spec_rel, check=False).stdout.splitlines()
                   if spec_body(c) != spec_body(c + "^")), None)
    all_paths = receipts_of(run)

    def in_scope(p, f):
        made = born(repo, p)
        if spec_c and made and (made == spec_c or not after(spec_c, made)):
            return False
        return not (base_sha and f["sha"] and not after(base_sha, f["sha"]))

    scoped = [(p, f) for p in all_paths for f in (receipt_fields(p),) if in_scope(p, f)]
    rpaths, receipts = [p for p, _ in scoped], [f for _, f in scoped]
    newest, next_n = (receipts[-1] if receipts else None), len(all_paths) + 1
    step, blocker, n, session, options, details, late, wp = None, None, None, None, [], [], False, None
    fix = f"Fix .jflow/{slug}/receipts/check-%s.md, then print the card."

    def constraint(name):
        v = re.search(rf"^- {name}:[ \t]*(.*?)\.?[ \t]*$", spec, re.M)
        v = v.group(1) if v else ""
        return "" if v.lower() in ("", "none", "nothing") else v

    pn, nl = git(repo, "show", f"{spec_c}^:{notes_rel}", check=False) if spec_c else None, notes.splitlines()
    new = [j for tag, _, _, j1, j2 in difflib.SequenceMatcher(None, pn.stdout.splitlines(), nl).get_opcodes()
           if tag[0] in "ir" for j in range(j1, j2)] if pn and not pn.returncode else range(len(nl))
    rnotes = "\n".join(nl[j] for j in new)

    def yes(pt):
        return re.search(rf"^Yes: {pt}\b", rnotes, re.M)

    shas = [base_sha] + [r["sha"] for r in receipts]
    counted = sum(1 for x, y in zip(shas, shas[1:]) if changed(repo, x, y) is not False)
    al = re.findall(r"^Checks allowed:\s*(\d+)", rnotes, re.M)
    allowed = int(al[-1]) if al else 3

    acceptances = [(m.group(1, 2), m.group(3), git(repo, "log", "-1", "--format=%H", "-S", l, "--", spec_rel))
                   for l in section(spec, "Accepted")
                   if (m := re.match(r"- (Row|Defect) (\d+) ·.*· ([0-9a-f]{7,40})\s*$", l))]

    def accepted_late():
        made = born(repo, rpaths[-1])
        return counted >= allowed and any(c and c != made and after(made, c) for *_, c in acceptances)

    if status == "done":
        why = "spec.md says Status: done"
    elif status != "ready" or not base:
        step, why = "spec", "no spec.md, or it is not ready"
    elif not receipts and changed(repo, spec_c or base_sha, "HEAD") is False:
        ask = constraint("Ask first")
        if ask and re.search(r"^## Approach", notes, re.M) and not yes("approach"):
            blocker = f"approve the approach in notes.md for Ask first: {ask}"
            options = [("It fits", "read ## Approach in notes.md first; I record your yes and build."),
                       ("Change it", "say what to change; I post a new approach.")]
            why, wp = "build posted its approach", "approach"
        else:
            step, why = "build", "no code commit since Base"
            session = "builder" if ask and yes("approach") else None
    elif not newest or (late := changed(repo, newest["sha"], "HEAD") is not False) and not accepted_late():
        step, n = "check", next_n
        why = "code changed since the newest receipt" if newest else "no check receipt yet"
    else:
        paths, shas_n, cache = {f["n"]: p for f, p in zip(receipts, rpaths)}, {f["n"]: f["sha"] or "-" for f in receipts}, {}

        def items(k):
            if k not in cache:
                t = paths[k].read_text("utf-8") if k in paths else ""
                d = {("Row", m.group(1)): m.group(0) for m in re.finditer(r"^\|\s*(\d+)\s*\|.*$", t, re.M)}
                d.update({("Defect", (re.findall(r"\d+", x) or ["?"])[0]): x for x in section(t, "Defects")})
                cache[k] = d
            return cache[k]

        def csrc(k, key):
            m = re.search(r"carried from check-(\d+)", items(k).get(key, ""), re.I)
            j = int(m.group(1)) if m else 0
            return j if 0 < j < k and key in items(j) else None

        def origin(k, key):
            j = csrc(k, key)
            return origin(j, key) if j else k

        def closed(k, key):
            sha, made = shas_n[k], born(repo, paths[k])
            if made and any(it == key and (nm.startswith(sha) or sha.startswith(nm)) and (
                not ad or after(made, ad)) for it, nm, ad in acceptances):
                return True
            j = csrc(k, key)
            return bool(j and closed(j, key))

        last = newest["n"]
        text, li = paths[last].read_text("utf-8"), items(last)
        rows = [(int(r), v) for r, v in re.findall(r"^\|\s*(\d+)\s*\|\s*([A-Z]+)\s*\|", text, re.M)
                if v != "ACCEPTED" and not closed(last, ("Row", r))]
        defs = [k for k in li if k[0] == "Defect" and not closed(last, k)]
        stuck = [f"Row {r}, {v}: {li[('Row', str(r))].split('|')[3].strip()}" for r, v in rows if v in ("BLOCKED", "UNREACHABLE")]
        name = f"check-{last}"
        edge = [k for k in defs if re.match(r"- \d+\. \[edge\]\s", li[k])]
        prev = receipts[-2]["n"] if len(receipts) >= 2 else None
        carried2 = [k for k in defs if k not in edge and prev and csrc(last, k) and csrc(prev, k) and origin(last, k) == origin(prev, k)]
        if late and (defs or {v for _, v in rows} - {"PROVED"}):
            step, n, why = "check", next_n, "code changed after an open receipt"
        elif any(v == "BROKEN" for _, v in rows) or [k for k in defs if k not in edge and k not in carried2]:
            step, n, why = "fix", last, f"{name} has BROKEN rows or open defects"
        elif carried2:
            blocker = f"{name}: defect {', '.join(k[1] for k in carried2)} carried unchanged across two checks"
            options = [("Accept", "I add them" + " and the [edge] defects" * bool(edge) + " under ## Accepted."),
                       ("Override and fix", "I fix them" + " and raise the check limit" * (counted >= allowed) + ".")]
            why = f"{name} has defects carried unchanged across two checks"
        elif stuck:
            blocker, details = f"{name} could not prove {len(stuck)} row{'s' * (len(stuck) > 1)}, and no fix can", stuck
            options = [("Supply what is missing", "give me what the rows above lack" + (
                "; for UNREACHABLE, delete the code or say what reaches it" * ("UNREACHABLE" in str(stuck)))
                + "; I hand you a fresh check."),
                ("Accept them unproved", "I add them" + " and the [edge] defects" * bool(edge) + " under ## Accepted.")]
            why = f"{name} has rows no fix can reach"
        elif edge:
            blocker = f"{name}: every open defect is [edge]: defect " + ", ".join(k[1] for k in edge)
            options = [("Accept them", "I add them under ## Accepted."),
                       ("Fix them", "I fix them" + " and raise the check limit" * (counted >= allowed) + ".")]
            why = f"{name} has only [edge] defects"
        elif any(v == "WAITING" for _, v in rows) and not re.search(r"^Live done:", rnotes, re.M):
            if constraint("Gate") and not yes("gate"):
                blocker = f"run the live gate, {constraint('Gate')}, or not"
                options = [("Run it", "I record your yes and run the live steps."),
                           ("Not yet", "nothing changes; the WAITING rows stay unproved.")]
                why, wp = f"{name} leaves only WAITING rows before the gate", "gate"
            else:
                step, why = "live", f"{name} has WAITING rows and notes.md has no Live done: line"
        elif any(v == "WAITING" for _, v in rows):
            step, n, why = "check", next_n, "live steps done; WAITING rows need a check"
        else:
            waits = [f"{h[:-1]}: {l[2:]}" for h, ls in (
                ("Human checks", section(spec, "Human checks")), ("Maybes", section(text, "Maybes"))) for l in ls]
            k = max([j for j, l in enumerate(nl) if l == "## Proposed edits"] or [len(nl)])
            bs = [j for j in range(k + 1, len(nl)) if nl[j][:2] == "- " and not any(l[:3] == "## " for l in nl[k + 1:j])]
            if waits and not yes("done"):
                blocker, details = "answer these before done", waits
                options = [("They hold", "do each one first; I record your yes and run done."),
                           ("One fails", "say what failed; I fix it.")]
                why, wp = f"{name} has every row proved and waits on the human", "done"
            elif bs and {k, *bs} & {*new} and not any(nl[j][:10] == "Yes: edits" for j in new if j > k):
                blocker, details = "approve the proposed edits", [nl[j][2:] for j in bs]
                options = [("Make them", "I record your yes; done makes them."),
                           ("Change them", "say what to change; I rewrite them.")]
                why, wp = f"{name}: done proposed edits", "edits"
            else:
                step, why = "done", f"{name} has every row proved"
    if counted >= allowed and (step == "fix" or step == "check" and late):
        open_ = [len(re.findall(r"^\|\s*\d+\s*\|\s*BROKEN\s*\|", t, re.M)) + len(section(t, "Defects"))
                 for t in (p.read_text("utf-8") for p in rpaths[-2:])]
        blocker = f"{counted} checks used of {allowed} and {step} is next" + (
            f"; BROKEN rows and defects went from {open_[0]} to {open_[1]}" if len(open_) == 2 else "")
        options = [("One more check", "I raise the limit" + " and fix" * (step == "fix")
                    + "; if that check finds a new problem, stop."), ("Stop here", "I accept what is open and move on.")]
        if len(open_) < 2 or open_[1] >= open_[0]:
            options.reverse()
        why, step, n = f"check cap reached before {step}", None, None
    if blocker:
        lines = [f"⏸️ {blocker[0].upper()}{blocker[1:]}."] + ([""] + [f"- {d}" for d in details] if details else [])
        for i, (label, say) in enumerate(options):
            lines += ["", ("**➡️ " if i == 0 else "**") + f"{'AB'[i]}. {label}**" + " (recommended)" * (i == 0) + ": " + say]
        blocker, step = "\n".join(lines + ["", "Reply A or B."]), "human"
    meta = FLOW["steps"].get(step, {})
    seat = seat_for(repo, step, a) if meta else None
    cmd = {"spec": f"jflow spec {slug}", "build": f"jflow build {slug}", "check": f"jflow check {slug}",
           "fix": fix % n, "live": f"Run the live steps of jflow build {slug}, then print the card.",
           "done": f"jflow done {slug}"}.get(step)
    return {"schema_version": 1, "slug": slug, "step": step, "n": n, "role": "human" if blocker else meta.get("role"),
            "model": {k: seat[k] for k in ("model", "vendor", "effort")} if seat else None,
            "command": cmd, "session": session or meta.get("session"), "blocker": blocker, "why": why, **({"wait_point": wp} if wp else {})}


def card(n):
    if n["blocker"]:
        return (f"Next: you decide. {n['blocker'].splitlines()[0][3:]} Send this in the builder session; it asks you"
                f" there:\n\n```text\njflow {n['slug']}\n```")
    if not n["step"]:
        return f"Nothing next: {n['why']}."
    m = f"{n['model']['model']} · {n['model']['effort']}"
    where = f"send this in the builder session ({m})" if n["session"] == "builder" else f"open a fresh session on {m} and send"
    return f"Next: {where}:\n\n```text\n{n['command']}\n```"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    rec, summ, val, seat, nxt = map(sub.add_parser, ("record", "summary", "validate", "seat", "next"))
    for p in (rec, summ, val, nxt):
        p.add_argument("slug")
    sys.path[:0] = [str(SKILL / "scripts")]
    import jflow_gh
    jflow_gh.add_args(sub, rec, summ, val)
    for p in (summ, nxt):
        p.add_argument("--json", action="store_true")
    nxt.add_argument("--ask", action="store_true")
    rec.add_argument("step", choices=STEPS)
    rec.add_argument("--model", required=True, type=record_value)
    rec.add_argument("--effort", required=True, type=record_value)
    rec.add_argument("--session", choices=("fresh", "builder"))
    val.add_argument("step", choices=("spec", "check", "accept"))
    seat.add_argument("step")
    for p in (seat, nxt):
        p.add_argument("--config")
        p.add_argument("--builder-vendor")
    for p in (rec, summ, seat, nxt, val):
        p.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    repo = Path(git(a.repo, "rev-parse", "--show-toplevel"))
    if a.cmd == "seat":
        if a.step not in STEPS:
            raise SystemExit("unknown flow step")
        print(json.dumps(seat_for(repo, a.step, a)))
        return 0
    hub = jflow_gh.Hub.of(a, repo, SLUG)
    repo, run = (hub.repo, hub.run) if hub else (repo, repo / ".jflow" / a.slug)
    if a.cmd == "note":
        return hub.note(a.file) or 0
    if a.cmd == "next":
        n = next_step(repo, run, a)
        hub and hub.tidy(n)
        print(json.dumps(n) if a.json else n["blocker"] if a.ask and n["blocker"] else card(n))
        return 0
    if a.cmd == "validate" or a.cmd == "record" and a.step in ("spec", "check", "accept"):
        errs = validate(repo, run, a.step)
        if errs:
            print("\n".join(errs), file=sys.stderr)
        if errs or a.cmd == "validate":
            return int(bool(errs))
    if not (run / "spec.md").exists():
        raise SystemExit(f"no {run / 'spec.md'}")
    if a.cmd == "summary":
        s = summary(repo, run)
        print(json.dumps(s) if a.json else line(s))
        return 0
    entry = {"v": 1, "step": a.step, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "sha": git(repo, "rev-parse", "HEAD"), "model": a.model, "effort": a.effort,
             "session": (a.session or "builder") if a.step in BUILDER_STEPS else "fresh",
             "skill": "jflow@" + hashlib.sha256((SKILL / "SKILL.md").read_bytes()).hexdigest()[:12]}
    if a.step == "check":
        entry.update(receipt_fields(receipts_of(run)[-1]))
    if a.step == "fix":
        entry["n"] = 1 + sum(1 for r in read_records(run) if r.get("step") == "fix")
    if a.step == "done":
        entry["summary"] = summary(repo, run)
    kept = [r for r in read_records(run) if not (a.step == "check" and r.get("step") == "check" and r.get("n") == entry["n"])]
    if hub:
        hub.post(a.step, entry)
    else:
        (run / "run.jsonl").write_text("".join(json.dumps(r) + "\n" for r in kept + [entry]), encoding="utf-8")
    print(line(entry["summary"]) if a.step == "done" else json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
