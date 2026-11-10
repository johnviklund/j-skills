#!/usr/bin/env python3
"""Record, validate and summarize jflow runs.

  jflow.py record <slug> <step> --model M --effort E [--session fresh|builder] [--repo DIR]
  jflow.py summary <slug> [--repo DIR] [--json]
  jflow.py validate <slug> <spec|check|accept> [--repo DIR]
  jflow.py seat <step> [--repo DIR] [--config FILE] [--builder-vendor V]
  jflow.py next <slug> [--repo DIR] [--config FILE] [--builder-vendor V] [--json]

Standard library, Python 3.9+. Readers ignore unknown keys and steps.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FLOW = json.loads((SKILL / "flow.json").read_text(encoding="utf-8"))
STEPS = tuple(FLOW["steps"])
RULES = dict.fromkeys(("public_paid_needs_human", "checker_read_only", "no_secrets"), True)
BUILDER_STEPS = ("fix", "live", "accept", "done")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
DOC_EXT = re.compile(r"\.(md|mdx|txt|rst|adoc)$", re.I)
CODE_EXT = re.compile(r"\.(py|js|mjs|cjs|ts|tsx|jsx|go|rs|java|kt|swift|rb|php|cs|c|h|cc|cpp|hpp|sh|bash|zsh|sql|"
                      r"css|scss|html|vue|svelte|lua|dart|scala|ex|exs|clj|pl|r|m)$", re.I)
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*$|_test\.[^/]+$|\.(test|spec)\.[^/]+$")


def secret(value):
    if isinstance(value, dict):
        return any(secret(k) or secret(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(secret(v) for v in value)
    # Generic sk- needs 20 characters and a digit or no inner hyphen; bare tokens need 40.
    return isinstance(value, str) and bool(re.search(
        r"(?<![\w-])(?:sk-ant-|sk-(?=[\w-]*\d|\w+(?![\w-]))[A-Za-z0-9_-]{20,}|gh[pousr]_|AKIA)|[A-Za-z0-9_+/=]{40,}", value))


def record_value(value):
    if secret(value):
        raise SystemExit("secret-like argument refused")
    return value


def seats(repo, explicit):
    config = {}
    external = explicit or os.environ.get("JFLOW_CONFIG")
    paths = [SKILL / "config.json", repo / ".jflow/config.json"] + ([Path(external)] if external else [])
    for path in paths:
        if path == repo / ".jflow/config.json" and not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if secret(data):
                raise ValueError("secret-like value refused")
            if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
                raise ValueError("schema_version must be 1")
            if set(data) - {"schema_version", "seats", "rules", "different_vendors", "other_vendor"}:
                raise ValueError("unknown config field")
            rules = data.get("rules", {})
            if not isinstance(rules, dict):
                raise ValueError("rules must be an object")
            for rule, enabled in rules.items():
                if rule not in RULES or enabled is not True:
                    raise ValueError("locked rule " + (rule if rule in RULES else "unknown"))
            if "different_vendors" in data and type(data["different_vendors"]) is not bool:
                raise ValueError("different_vendors must be boolean")
            entries = data.get("seats", {})
            if not isinstance(entries, dict) or set(entries) - set(STEPS):
                raise ValueError("seats must name flow steps")
            for entry in list(entries.values()) + ([data["other_vendor"]] if "other_vendor" in data else []):
                pending = [entry]
                while pending:
                    seat = pending.pop()
                    if not isinstance(seat, dict) or set(seat) != {"model", "vendor", "effort", "fallback"}:
                        raise ValueError("each seat needs model, vendor, effort and fallback")
                    if any(not isinstance(seat[k], str) or not seat[k].strip() for k in ("model", "vendor", "effort")):
                        raise ValueError("seat model, vendor and effort must be nonempty strings")
                    if seat["fallback"] is not None:
                        pending.append(seat["fallback"])
            config.setdefault("seats", {}).update(entries)
            config.update({k: v for k, v in data.items() if k != "seats"})
        except (OSError, ValueError, RecursionError) as error:
            # Decoder errors may contain secrets.
            message = str(error) if type(error) is ValueError else "cannot read valid config JSON"
            raise SystemExit(f"{path}: {message}")
    return config


def seat_for(repo, step, a):
    config = seats(repo, a.config)
    meta = FLOW["steps"][step]
    chosen = config["seats"].get(step, config["seats"][meta["seat"]])
    builder = a.builder_vendor or config["seats"]["build"]["vendor"]
    if step == "check" and config["different_vendors"] and chosen["vendor"] == builder:
        chosen = config["other_vendor"]
        if chosen["vendor"] == builder:
            raise SystemExit("other_vendor must differ from the builder vendor")
    return dict(chosen, **meta, step=step, rules=RULES)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def section(text, heading):
    """Section bullets excluding none placeholders."""
    match = re.search(rf"^## {heading}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    lines = [l for l in (match.group(1).splitlines() if match else []) if l.startswith("- ")]
    return [l for l in lines if not re.match(r"- (none\.?|<none\b[^>]*>)\s*$", l, re.I)]


def changed(repo, a, b):
    """Code changed outside .jflow/, or None for unknown commits."""
    try:
        return bool(git(repo, "diff", "--name-only", f"{a}..{b}", "--", ".", ":(exclude).jflow"))
    except subprocess.CalledProcessError:
        return None


def check_fields(run):
    receipts = receipts_of(run)
    if not receipts:
        raise SystemExit("record check: no receipts/check-N.md yet; write the receipt first")
    return receipt_fields(receipts[-1])


def receipts_of(run):
    return sorted(run.glob("receipts/check-*.md"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))


def receipt_fields(path):
    text = path.read_text(encoding="utf-8")
    rows = {}
    for verdict in re.findall(r"^\|\s*\d+\s*\|\s*([A-Z]+)\s*\|", text, re.M):
        rows[verdict] = rows.get(verdict, 0) + 1
    sha = re.search(r"^# check-\d+ @ ([0-9a-f]{7,40})\b", text, re.M)
    return {"n": int(re.sub(r"\D", "", path.stem)), "sha": sha.group(1) if sha else None, "rows": rows,
            # A defect carried over from an earlier check was counted there.
            "defects": len([d for d in section(text, "Defects") if "carried from" not in d.lower()]),
            "maybes": len(section(text, "Maybes"))}


def read_records(run):
    path = run / "run.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def validate(repo, run, step):
    errors, path = [], run / "spec.md"

    def need(ok, n, message):
        if not ok:
            errors.append(f"{path.relative_to(repo)}:{n}: {message}")

    def read():
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            need(False, 1, "cannot read file")
            return ""

    def sha(value, n=1):
        need(re.fullmatch(r"[0-9a-f]{7,40}", value) and subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", value + "^{commit}"],
            capture_output=True).returncode == 0, n, "unknown commit sha")

    def body(text, heading):
        active = False
        for n, line in enumerate(text.splitlines(), 1):
            if line.startswith("## "):
                active = line.strip() == "## " + heading
            elif active and line.strip():
                yield n, line

    def table(lines, header):
        rows, seen = {}, False
        for n, line in lines:
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if not seen:
                need(cells == header.split("|"), n, "expected columns " + header)
                seen = True
            elif all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            elif len(cells) != len(header.split("|")) or not cells[0].isdigit():
                need(False, n, "bad table row")
            else:
                need(cells[0] not in rows, n, "duplicate row " + cells[0])
                rows[cells[0]] = (n, cells)
        need(rows, 1, "missing table rows")
        return rows

    spec = read()
    rows = table(body(spec, "Proof"), "#|Claim|Surface|Check|Pass signal|Kind|Base")
    if step == "spec":
        need(re.search(r"^Status: (ready|done)[ \t]*$", spec, re.M), 1, "invalid Status")
        base = re.search(r"^Base: (\S+)[ \t]*$", spec, re.M)
        sha(base[1] if base else "")
        for heading in ("Problem", "Goals", "Non-goals", "Constraints", "Proof", "Human checks"):
            need(re.search(rf"^## {heading}[ \t]*$", spec, re.M), 1, "missing section " + heading)
        need(any(re.fullmatch(r"- Gate: .+", l) for _, l in body(spec, "Constraints")), 1, "missing Gate line")
        for n, cells in rows.values():
            kind, base = cells[-2:]
            need(kind in ("new", "keep", "live") and base == ("green" if kind == "keep" else "red"),
                 n, "invalid Kind or Base")
    elif step == "accept":
        for n, line in body(spec, "Accepted"):
            m = re.fullmatch(r'- (Row|Defect) (\d+) · .+ · ".+" · \d{4}-\d{2}-\d{2} · (\S+)', line)
            need(m, n, "invalid Accepted line")
            if m:
                sha(m[3], n)
                need(m[1] != "Row" or m[2] in rows, n, "Accepted names unknown row " + m[2])
    else:
        receipts = receipts_of(run)
        path = receipts[-1] if receipts else run / "receipts/check-N.md"
        text = read()
        m = re.match(r"# check-(\d+) @ (\S+) · .+", text)
        need(m and path.stem == "check-" + m[1], 1, "missing receipt or mismatched header " + path.stem)
        if m:
            sha(m[2])
        headings = re.findall(r"^## (.+)$", text, re.M)
        need(headings == ["Defects", "Maybes"], 1, "missing or extra section: Defects, Maybes required")
        defects = set()
        for n, line in body(text, "Defects"):
            if re.fullmatch(r"- (none\.?|<none[^>]*>)", line, re.I):
                continue
            m = re.match(r"- (\d+)\. .+? Evidence: (.+)$", line)
            need(m and len(m[2]) <= 240, n, "invalid defect or Evidence exceeds 240 characters")
            if m:
                defects.add(m[1])
        verdicts = table(enumerate(text.split("\n## ", 1)[0].splitlines(), 1), "#|Verdict|Evidence")
        for key in rows.keys() - verdicts.keys():
            need(False, 1, "missing row " + key)
        accepted = {m[1] for _, l in body(spec, "Accepted") if (m := re.fullmatch(r"- Row (\d+) ·.*· [0-9a-f]{7,40}", l))}
        for key, (n, cells) in verdicts.items():
            _, verdict, evidence = cells
            need(key in rows and verdict in ("PROVED", "BROKEN", "BLOCKED", "UNREACHABLE", "WAITING", "ACCEPTED"),
                 n, "unknown row or verdict " + key)
            need(0 < len(evidence) <= 240, n, "Evidence empty or exceeds 240 characters")
            for defect in re.findall(r"\bdefect (\d+)\b", evidence, re.I):
                need(defect in defects, n, "unknown defect " + defect)
            need(verdict != "ACCEPTED" or key in accepted, n, "row " + key + " not under Accepted")
    return errors


def summary(repo, run):
    records = read_records(run)
    spec = (run / "spec.md").read_text(encoding="utf-8")
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    if not base:
        raise SystemExit("summary: spec.md has no Base line")
    spec_path = str(run / "spec.md")
    # Exclude the done commit's WORKLOG/TODO edits and later work from finished runs.
    done_commits = git(repo, "log", "--format=%H", "-G", "^Status: done", "--", spec_path).splitlines()
    end = done_commits[-1] + "^" if done_commits else "HEAD"
    code = tests = docs = other = 0
    for line in git(repo, "diff", "--numstat", f"{base.group(1)}..{end}", "--", ".", ":(exclude).jflow").splitlines():
        added, deleted, path = line.split("\t", 2)
        if added == "-":
            continue
        delta = int(added) - int(deleted)
        if TEST_PATH.search(path):
            tests += delta
        elif CODE_EXT.search(path):
            code += delta
        elif DOC_EXT.search(path):
            docs += delta
        else:
            other += delta
    proof = re.search(r"^## Proof\s*$(.*?)(?=^## |\Z)", spec, re.M | re.S)
    started = git(repo, "log", "--reverse", "--format=%cI", "--", spec_path).splitlines()
    ended = dt.datetime.fromisoformat(git(repo, "log", "-1", "--format=%cI", done_commits[-1])) if done_commits \
        else dt.datetime.now(dt.timezone.utc)
    hours = round((ended - dt.datetime.fromisoformat(started[0])).total_seconds() / 3600, 1) if started else None
    # Count checks predating run.jsonl too.
    checks = [receipt_fields(p) for p in receipts_of(run)]
    # Git also counts unrecorded fixes.
    shas = [c["sha"] for c in checks] + [end]
    fixes = sum(1 for a, b in zip(shas, shas[1:]) if a and changed(repo, a, b))
    steps = [r for r in records if r.get("step") in STEPS]
    # Include re-specs and fresh builder restarts.
    sessions = (max(1, sum(r["step"] == "spec" for r in steps)) + bool(checks or code or tests or docs or other)
                + len(checks) + sum(r["step"] in BUILDER_STEPS and r.get("session") == "fresh" for r in steps))
    return {"sessions": sessions if steps else None,
            "checks": len(checks), "fix_rounds": max(fixes, sum(r["step"] == "fix" for r in steps)),
            "rows": len(re.findall(r"^\|\s*\d+\s*\|", proof.group(1), re.M)) if proof else 0,
            "accepted": len(section(spec, "Accepted")), "defects": sum(c["defects"] for c in checks),
            "first_check_clean": (checks[0]["defects"] == 0 and set(checks[0]["rows"]) <= {"PROVED", "WAITING", "ACCEPTED"}) if checks else None,
            "net_code": code, "tests": tests, "docs": docs, "other": other,
            "hours_spec_to_end": hours}


def line(s):
    sessions = s["sessions"] if s["sessions"] is not None else "?"
    check = "check clean" if s["defects"] == 0 else f"check {s['defects']} defects"
    return (f"jflow: {sessions} sessions · {s['fix_rounds']} fix rounds · {s['rows']} rows · {s['accepted']} accepted"
            f" · {check} · net code {s['net_code']:+d} · tests {s['tests']:+d} · docs {s['docs']:+d}")


def next_step(repo, run, a):
    slug = run.name
    spec = (run / "spec.md").read_text(encoding="utf-8") if (run / "spec.md").exists() else ""
    status = re.search(r"^Status:\s*(\w+)", spec, re.M)
    status = status.group(1) if status else None
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    notes = (run / "notes.md").read_text(encoding="utf-8") if (run / "notes.md").exists() else ""
    receipts = [receipt_fields(p) for p in receipts_of(run)]
    newest = receipts[-1] if receipts else None
    step, blocker, n, session = None, None, None, None

    def constraint(name):
        """The spec's '- Gate: ...' or '- Ask first: ...' value; '' for none or nothing."""
        value = re.search(rf"^- {name}:[ \t]*(.*?)\.?[ \t]*$", spec, re.M)
        value = value.group(1) if value else ""
        return "" if value.lower() in ("", "none", "nothing") else value

    def yes(point):
        return re.search(rf"^Yes: {point}\b", notes, re.M)

    if status == "done":
        why = "spec.md says Status: done"
    elif status != "ready" or not base:
        step, why = "spec", "no spec.md, or it is not ready"
    elif not receipts and changed(repo, base.group(1), "HEAD") is False:
        ask = constraint("Ask first")
        if ask and re.search(r"^## Approach", notes, re.M) and not yes("approach"):
            blocker = f"approve the approach in notes.md for Ask first: {ask}; a yes is a Yes: approach line in notes.md"
            why = "build posted its approach"
        else:
            step, why = "build", "no code commit since Base"
            session = "builder" if ask and yes("approach") else None
    elif not newest or changed(repo, newest["sha"], "HEAD") is not False:
        step, n = "check", len(receipts) + 1
        why = "code changed since the newest receipt" if newest else "no check receipt yet"
    else:
        paths = {f["n"]: p for f, p in zip(receipts, receipts_of(run))}
        acceptances = []
        for l in section(spec, "Accepted"):
            m = re.match(r"- (Row|Defect) (\d+) ·.*· ([0-9a-f]{7,40})\s*$", l)
            if m:
                added = git(repo, "log", "-1", "--format=%H", "-S", l, "--", str(run / "spec.md"))
                acceptances.append((m.group(1, 2), m.group(3), added))

        def closed(k, key):
            # Acceptances name the source check's sha and follow its receipt commit.
            carried = re.search(r"carried from check-(\d+)", items(k)[key], re.I)
            if carried and int(carried.group(1)) < k and key in items(int(carried.group(1))):
                return closed(int(carried.group(1)), key)
            sha = receipt_fields(paths[k])["sha"] or "-"
            created = git(repo, "log", "-1", "--diff-filter=A", "--format=%H", "--", str(paths[k]))
            return bool(created) and any(item == key and (named.startswith(sha) or sha.startswith(named)) and (
                not added or subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", created, added]
                                            ).returncode == 0) for item, named, added in acceptances)

        def items(k):
            """Receipt lines keyed ("Row", "3") or ("Defect", "1")."""
            text = paths[k].read_text(encoding="utf-8") if k in paths else ""
            lines = {("Row", m.group(1)): m.group(0) for m in re.finditer(r"^\|\s*(\d+)\s*\|.*$", text, re.M)}
            lines.update({("Defect", (re.findall(r"\d+", d) or ["?"])[0]): d for d in section(text, "Defects")})
            return lines

        last = newest["n"]
        rows = [(int(r), v) for r, v in re.findall(r"^\|\s*(\d+)\s*\|\s*([A-Z]+)\s*\|",
                                                   paths[last].read_text(encoding="utf-8"), re.M)
                if not closed(last, ("Row", r))]
        defects = [key for key in items(last) if key[0] == "Defect" and not closed(last, key)]
        stuck = [f"row {r} {v}" for r, v in rows if v in ("BLOCKED", "UNREACHABLE")]
        name = f"check-{newest['n']}"
        if any(v == "BROKEN" for _, v in rows) or defects:
            step, n, why = "fix", newest["n"], f"{name} has BROKEN rows or open defects"
        elif stuck:
            blocker = f"{name}: {', '.join(stuck)}; decide per references/check.md"
            why = f"{name} has rows no fix can reach"
        elif any(v == "WAITING" for _, v in rows) and not re.search(r"^Live done:", notes, re.M):
            if constraint("Gate") and not yes("gate"):
                blocker = f"run the live gate, {constraint('Gate')}, or not; a yes is a Yes: gate line in notes.md"
                why = f"{name} leaves only WAITING rows before the gate"
            else:
                step, why = "live", f"{name} has WAITING rows and notes.md has no Live done: line"
        elif any(v == "WAITING" for _, v in rows):
            step, n, why = "check", len(receipts) + 1, "live steps done; WAITING rows need a check"
        else:
            waits = [f"{h}: {'; '.join(l[2:] for l in ls)}" for h, ls in (
                ("Human checks", section(spec, "Human checks")),
                ("Maybes", section(paths[last].read_text(encoding="utf-8"), "Maybes"))) if ls]
            if waits and not yes("done"):
                blocker = f"answer before done, {'. '.join(waits)}; a yes is a Yes: done line in notes.md"
                why = f"{name} has every row proved and waits on the human"
            else:
                step, why = "done", f"{name} has every row proved"
    # Cap: a check counts when code changed since the receipt before it, or Base.
    shas = [base.group(1) if base else None] + [r["sha"] for r in receipts]
    counted = sum(1 for x, y in zip(shas, shas[1:]) if changed(repo, x, y) is not False)
    allowed = re.search(r"^Checks allowed:\s*(\d+)", notes, re.M)
    allowed = int(allowed.group(1)) if allowed else 3
    if counted >= allowed and (step == "fix" or step == "check" and newest
                               and changed(repo, newest["sha"], "HEAD") is not False):
        blocker = f"{counted} checks used of {allowed} and {step} is next; add Checks allowed: N to notes.md, or stop"
        why, step, n = f"check cap reached before {step}", None, None
    if blocker:
        step = "human"
    meta = FLOW["steps"].get(step, {})
    seat = seat_for(repo, step, a) if meta else None
    command = {"spec": f"jflow spec {slug}", "build": f"jflow build {slug}", "check": f"jflow check {slug}",
               "fix": f"Fix .jflow/{slug}/receipts/check-{n}.md, then print the card.",
               "live": f"Run the live steps of jflow build {slug}, then print the card.",
               "done": f"jflow done {slug}"}.get(step)
    return {"schema_version": 1, "slug": slug, "step": step, "n": n, "role": "human" if blocker else meta.get("role"),
            "model": {k: seat[k] for k in ("model", "vendor", "effort")} if seat else None,
            "command": command, "session": session or meta.get("session"), "blocker": blocker, "why": why}


def card(n):
    if n["blocker"]:
        return f"The human decides: {n['blocker']}."
    if not n["step"]:
        return f"Nothing next: {n['why']}."
    session = "builder session" if n["session"] == "builder" else n["session"]
    return (f"Model: {n['model']['model']} · {n['model']['effort']}. Session: {session}.\n\n"
            f"```text\n{n['command']}\n```")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("slug")
    rec.add_argument("step", choices=STEPS)
    rec.add_argument("--model", required=True, type=record_value)
    rec.add_argument("--effort", required=True, type=record_value)
    rec.add_argument("--session", choices=("fresh", "builder"), help="fresh: a builder step in a new session")
    summ = sub.add_parser("summary")
    summ.add_argument("slug")
    summ.add_argument("--json", action="store_true")
    val = sub.add_parser("validate")
    val.add_argument("slug")
    val.add_argument("step", choices=("spec", "check", "accept"))
    seat = sub.add_parser("seat")
    seat.add_argument("step")
    nxt = sub.add_parser("next")
    nxt.add_argument("slug")
    nxt.add_argument("--json", action="store_true")
    for p in (seat, nxt):
        p.add_argument("--config")
        p.add_argument("--builder-vendor", help="actual builder vendor when its session differs from config")
    for p in (rec, summ, seat, nxt, val):
        p.add_argument("--repo", default=".")
    a = parser.parse_args(argv)
    if a.cmd == "seat":
        if a.step not in STEPS:
            raise SystemExit("unknown flow step")
        print(json.dumps(seat_for(Path(git(a.repo, "rev-parse", "--show-toplevel")), a.step, a)))
        return 0
    if not SLUG.match(a.slug):
        raise SystemExit(f"bad slug: {a.slug}")
    repo = Path(git(a.repo, "rev-parse", "--show-toplevel"))
    run = repo / ".jflow" / a.slug
    if a.cmd == "next":
        n = next_step(repo, run, a)
        print(json.dumps(n) if a.json else card(n))
        return 0
    if a.cmd == "validate" or a.cmd == "record" and a.step in ("spec", "check", "accept"):
        errors = validate(repo, run, a.step)
        if errors:
            print("\n".join(errors), file=sys.stderr)
        if errors or a.cmd == "validate":
            return int(bool(errors))
    if not (run / "spec.md").exists():
        raise SystemExit(f"no {run / 'spec.md'}")
    if a.cmd == "summary":
        s = summary(repo, run)
        print(json.dumps(s) if a.json else line(s))
        return 0
    skill = SKILL / "SKILL.md"
    entry = {"v": 1, "step": a.step, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "sha": git(repo, "rev-parse", "HEAD"), "model": a.model, "effort": a.effort,
             "session": (a.session or "builder") if a.step in BUILDER_STEPS else "fresh",
             "skill": "jflow@" + hashlib.sha256(skill.read_bytes()).hexdigest()[:12]}
    if a.step == "check":
        entry.update(check_fields(run))
    if a.step == "fix":
        entry["n"] = 1 + sum(1 for r in read_records(run) if r.get("step") == "fix")
    if a.step == "done":
        entry["summary"] = summary(repo, run)
    # Re-recording replaces the check's line.
    kept = [r for r in read_records(run) if not (a.step == "check" and r.get("step") == "check"
                                                  and r.get("n") == entry["n"])]
    (run / "run.jsonl").write_text("".join(json.dumps(r) + "\n" for r in kept + [entry]), encoding="utf-8")
    print(line(entry["summary"]) if a.step == "done" else json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
