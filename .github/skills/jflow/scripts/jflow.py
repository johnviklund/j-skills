#!/usr/bin/env python3
"""Record, validate and summarize jflow runs. Usage: jflow.py COMMAND -h.

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
FLOW = json.loads((SKILL / "flow.json").read_text("utf-8"))
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
            data = json.loads(path.read_text("utf-8"))
            if secret(data):
                raise ValueError("secret-like value refused")
            if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
                raise ValueError("schema_version must be 1")
            if set(data) - {"schema_version", "seats", "rules", "different_vendors", "other_vendor", "mode"}:
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


def born(repo, path):
    return git(repo, "log", "-1", "--diff-filter=A", "--format=%H", "--", str(path))


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


def receipts_of(run):
    return sorted(run.glob("receipts/check-*.md"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))


def receipt_fields(path):
    text = path.read_text("utf-8")
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
    return [json.loads(l) for l in path.read_text("utf-8").splitlines() if l.strip()]


def validate(repo, run, step):
    errors, path = [], run / "spec.md"

    def need(ok, n, message):
        if not ok:
            errors.append(f"{path.relative_to(repo)}:{n}: {message}")

    def read():
        try:
            return path.read_text("utf-8")
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
        if (repo / "PRODUCT.md").exists():
            head = spec.split("\n## ")[0]
            m = re.search(r"^Serves: (.+?)[ \t]*$", head, re.M)
            outcomes, fence = ["none"], ""
            for l in (repo / "PRODUCT.md").read_text("utf-8").splitlines():
                f = re.match(r" {0,3}(`{3,}|~{3,}|<!--)", l)
                if fence:  # CommonMark comments and fences
                    fence *= not ("-->" in l if fence == "<!--" else re.fullmatch(rf" {{0,3}}{fence[0]}{{{len(fence)},}}\s*", l))
                elif f:
                    fence = "" if f[1] == "<!--" and "-->" in l else f[1]
                elif h := re.fullmatch(r" {0,3}###[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*", l):
                    outcomes.append(h[1])
            need(m and m[1] in outcomes,
                 head[:m.start()].count("\n") + 1 if m else 1, "Serves names no ### outcome in PRODUCT.md")
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
        need(m and path.stem == "check-" + m[1], 1, "missing receipt or bad header " + path.stem)
        if m:
            sha(m[2])
        need(not path.exists() or path.stat().st_size <= 3000, 1, "receipt over 3,000 bytes")
        if len(receipts) > 1:
            # Compare with the prior receipt's commit, or its header SHA if uncommitted.
            rel, files = os.fsencode(run.relative_to(repo).as_posix()), []
            try:
                prev = (born(repo, receipts[-2])
                        or receipt_fields(receipts[-2])["sha"])
                # A tree diff sees merge commits and both sides of a rename.
                files = subprocess.check_output(
                    ["git", "-C", str(repo), "diff", "--name-only", "--no-renames", "-z", f"{prev}", "HEAD"],
                    stderr=subprocess.PIPE,
                ).split(b"\0")
            except (OSError, UnicodeError):
                need(False, 1, f"cannot read {receipts[-2].stem}")
            except subprocess.CalledProcessError:
                pass
            need(any(f and (not f.startswith(b".jflow/") or f in (rel + b"/notes.md", rel + b"/spec.md"))
                     for f in files), 1,
                 f"no new input since {receipts[-2].stem}: commit code, notes.md or spec.md first")
        need(re.findall(r"^## (.+)$", text, re.M) == ["Defects", "Maybes"],
             1, "missing or extra section: Defects, Maybes")
        defects = set()
        for n, line in body(text, "Defects"):
            m = re.match(r"- (\d+)\. (?:\[([^]]*)\]\s)?.+? Evidence: (.+)$", line)
            need(m and m[1] not in defects and len(m[3]) <= 240 and m[2] in (None, "use", "edge") or re.fullmatch(
                r"- (none\.?|<none[^>]*>)", line, re.I), n, "invalid defect (or repeat), tag or Evidence >240")
            defects.add(m and m[1])
        verdicts = table(enumerate(text.split("\n## ", 1)[0].splitlines(), 1), "#|Verdict|Evidence")
        for key in rows.keys() - verdicts.keys():
            need(False, 1, "missing row " + key)
        accepted = {m[1] for _, l in body(spec, "Accepted") if (m := re.fullmatch(r"- Row (\d+) ·.*· [0-9a-f]{7,40}", l))}
        for key, (n, cells) in verdicts.items():
            _, verdict, evidence = cells
            need(key in rows and verdict in ("PROVED", "BROKEN", "BLOCKED", "UNREACHABLE", "WAITING", "ACCEPTED"),
                 n, "unknown row or verdict " + key)
            need(0 < len(evidence) <= 240, n, "Evidence empty or over 240")
            if verdict == "BROKEN" and re.fullmatch(r"(?i)defect \d+(,\s*defect \d+)*", evidence):
                for d in re.findall(r"\d+", evidence):
                    need(d in defects, n, f"unknown defect {d}")
            need(verdict != "ACCEPTED" or key in accepted, n, "row " + key + " not under Accepted")
    return errors


def summary(repo, run):
    records = read_records(run)
    spec = (run / "spec.md").read_text("utf-8")
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    if not base:
        raise SystemExit("summary: spec.md has no Base line")
    spec_path = str(run / "spec.md")
    # Stop before the done commit's WORKLOG/TODO edits.
    done_commits = git(repo, "log", "--format=%H", "-G", "^Status: done", "--", spec_path).splitlines()
    end = done_commits[-1] + "^" if done_commits else "HEAD"
    lines = dict.fromkeys(("net_code", "tests", "docs", "other"), 0)
    for line in git(repo, "diff", "--numstat", f"{base.group(1)}..{end}", "--", ".", ":(exclude).jflow").splitlines():
        added, deleted, path = line.split("\t", 2)
        if added == "-":
            continue
        lines["tests" if TEST_PATH.search(path) else "net_code" if CODE_EXT.search(path)
              else "docs" if DOC_EXT.search(path) else "other"] += int(added) - int(deleted)
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
    sessions = (max(1, sum(r["step"] == "spec" for r in steps)) + bool(checks or any(lines.values()))
                + len(checks) + sum(r["step"] in BUILDER_STEPS and r.get("session") == "fresh" for r in steps))
    return {"sessions": sessions if steps else None,
            "checks": len(checks), "fix_rounds": max(fixes, sum(r["step"] == "fix" for r in steps)),
            "rows": len(re.findall(r"^\|\s*\d+\s*\|", proof.group(1), re.M)) if proof else 0,
            "accepted": len(section(spec, "Accepted")), "defects": sum(c["defects"] for c in checks),
            "first_check_clean": (checks[0]["defects"] == 0 and set(checks[0]["rows"]) <= {"PROVED", "WAITING", "ACCEPTED"}) if checks else None,
            **lines, "hours_spec_to_end": hours}


def line(s):
    sessions = s["sessions"] if s["sessions"] is not None else "?"
    check = "check clean" if s["defects"] == 0 else f"check {s['defects']} defects"
    return (f"jflow: {sessions} sessions · {s['fix_rounds']} fix rounds · {s['rows']} rows · {s['accepted']} accepted"
            f" · {check} · net code {s['net_code']:+d} · tests {s['tests']:+d} · docs {s['docs']:+d}")


def next_step(repo, run, a):
    slug = run.name
    spec, notes = ((run / f).read_text("utf-8") if (run / f).exists() else "" for f in ("spec.md", "notes.md"))
    status = re.search(r"^Status:\s*(\w+)", spec, re.M)
    status = status.group(1) if status else None
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    receipts = [receipt_fields(p) for p in receipts_of(run)]
    newest = receipts[-1] if receipts else None
    step, blocker, n, session, options, details, late = None, None, None, None, [], [], False
    fix = f"Fix .jflow/{slug}/receipts/check-%s.md, then print the card."

    def constraint(name):
        """The spec's '- Gate: ...' or '- Ask first: ...' value; '' for none or nothing."""
        value = re.search(rf"^- {name}:[ \t]*(.*?)\.?[ \t]*$", spec, re.M)
        value = value.group(1) if value else ""
        return "" if value.lower() in ("", "none", "nothing") else value

    def yes(point):
        return re.search(rf"^Yes: {point}\b", notes, re.M)

    # Cap: a check counts when code changed since the receipt before it, or Base.
    shas = [base.group(1) if base else None] + [r["sha"] for r in receipts]
    counted = sum(1 for x, y in zip(shas, shas[1:]) if changed(repo, x, y) is not False)
    allowed = re.findall(r"^Checks allowed:\s*(\d+)", notes, re.M)
    allowed = int(allowed[-1]) if allowed else 3

    acceptances = []
    for l in section(spec, "Accepted"):
        m = re.match(r"- (Row|Defect) (\d+) ·.*· ([0-9a-f]{7,40})\s*$", l)
        if m:
            added = git(repo, "log", "-1", "--format=%H", "-S", l, "--", str(run / "spec.md"))
            acceptances.append((m.group(1, 2), m.group(3), added))

    def after(a, b):
        return not subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b]).returncode

    def accepted_late():
        made = born(repo, receipts_of(run)[-1])
        return counted >= allowed and any(c and c != made and after(made, c) for *_, c in acceptances)

    if status == "done":
        why = "spec.md says Status: done"
    elif status != "ready" or not base:
        step, why = "spec", "no spec.md, or it is not ready"
    elif not receipts and changed(repo, base.group(1), "HEAD") is False:
        ask = constraint("Ask first")
        if ask and re.search(r"^## Approach", notes, re.M) and not yes("approach"):
            blocker = f"approve the approach in notes.md for Ask first: {ask}"
            options = [("It fits", "read ## Approach in notes.md first; I record your yes and build."),
                       ("Change it", "say what to change; I post a new approach.")]
            why = "build posted its approach"
        else:
            step, why = "build", "no code commit since Base"
            session = "builder" if ask and yes("approach") else None
    elif not newest or (late := changed(repo, newest["sha"], "HEAD") is not False) and not accepted_late():
        step, n = "check", len(receipts) + 1
        why = "code changed since the newest receipt" if newest else "no check receipt yet"
    else:
        paths = {f["n"]: p for f, p in zip(receipts, receipts_of(run))}
        def closed(k, key):
            # Acceptances name the source check's sha and follow its receipt commit.
            carried = re.search(r"carried from check-(\d+)", items(k)[key], re.I)
            if carried and int(carried.group(1)) < k and key in items(int(carried.group(1))):
                return closed(int(carried.group(1)), key)
            sha = receipt_fields(paths[k])["sha"] or "-"
            created = born(repo, paths[k])
            return bool(created) and any(item == key and (named.startswith(sha) or sha.startswith(named)) and (
                not added or after(created, added)) for item, named, added in acceptances)

        def items(k):
            """Receipt lines keyed ("Row", "3") or ("Defect", "1")."""
            text = paths[k].read_text("utf-8") if k in paths else ""
            lines = {("Row", m.group(1)): m.group(0) for m in re.finditer(r"^\|\s*(\d+)\s*\|.*$", text, re.M)}
            lines.update({("Defect", (re.findall(r"\d+", d) or ["?"])[0]): d for d in section(text, "Defects")})
            return lines

        last = newest["n"]
        text = paths[last].read_text("utf-8")
        rows = [(int(r), v) for r, v in re.findall(r"^\|\s*(\d+)\s*\|\s*([A-Z]+)\s*\|", text, re.M)
                if not closed(last, ("Row", r))]
        defects = [key for key in items(last) if key[0] == "Defect" and not closed(last, key)]
        stuck = [f"Row {r}, {v}: {items(last)[('Row', str(r))].split('|')[3].strip()}"
                 for r, v in rows if v in ("BLOCKED", "UNREACHABLE")]
        name = f"check-{newest['n']}"
        edge = [k for k in defects if re.match(r"- \d+\. \[edge\]\s", items(last)[k])]
        if late and (defects or {v for _, v in rows} - {"PROVED"}):
            step, n, why = "check", len(receipts) + 1, "code changed after an open receipt"
        elif any(v == "BROKEN" for _, v in rows) or defects != edge:
            step, n, why = "fix", newest["n"], f"{name} has BROKEN rows or open defects"
        elif stuck:  # before [edge] defects
            blocker, details = f"{name} could not prove {len(stuck)} row{'s' * (len(stuck) > 1)}, and no fix can", stuck
            options = [("Supply what is missing", "give me what the rows above lack" + (
                "; for UNREACHABLE, delete the code or say what reaches it" * ("UNREACHABLE" in str(stuck)))
                + "; I hand you a fresh check."),
                ("Accept them unproved", "I add them" + " and the [edge] defects" * bool(edge) + " under ## Accepted.")]
            why = f"{name} has rows no fix can reach"
        elif edge:
            step = "edge"
        elif any(v == "WAITING" for _, v in rows) and not re.search(r"^Live done:", notes, re.M):
            if constraint("Gate") and not yes("gate"):
                blocker = f"run the live gate, {constraint('Gate')}, or not"
                options = [("Run it", "I record your yes and run the live steps."),
                           ("Not yet", "nothing changes; the WAITING rows stay unproved.")]
                why = f"{name} leaves only WAITING rows before the gate"
            else:
                step, why = "live", f"{name} has WAITING rows and notes.md has no Live done: line"
        elif any(v == "WAITING" for _, v in rows):
            step, n, why = "check", len(receipts) + 1, "live steps done; WAITING rows need a check"
        else:
            waits = [f"{h[:-1]}: {l[2:]}" for h, ls in (
                ("Human checks", section(spec, "Human checks")),
                ("Maybes", section(text, "Maybes"))) for l in ls]
            if waits and not yes("done"):
                blocker, details = "answer these before done", waits
                options = [("They hold", "do each one first; I record your yes and run done."),
                           ("One fails", "say what failed; I fix it.")]
                why = f"{name} has every row proved and waits on the human"
            else:
                step, why = "done", f"{name} has every row proved"
    if counted >= allowed and (step == "fix" or step == "check" and late):
        # Closing: fewer BROKEN rows and defects than the receipt before.
        open_ = [len(re.findall(r"^\|\s*\d+\s*\|\s*BROKEN\s*\|", t, re.M)) + len(section(t, "Defects"))
                 for t in (p.read_text("utf-8") for p in receipts_of(run)[-2:])]
        blocker = f"{counted} checks used of {allowed} and {step} is next" + (
            f"; BROKEN rows and defects went from {open_[0]} to {open_[1]}" if len(open_) == 2 else "")
        options = [("One more check", "I raise the limit" + " and fix" * (step == "fix")
                    + "; if that check finds a new problem, stop."), ("Stop here", "I accept what is open and move on.")]
        if len(open_) < 2 or open_[1] >= open_[0]:
            options.reverse()
        why, step, n = f"check cap reached before {step}", None, None
    if step == "edge":
        blocker = f"check-{last}: every open defect is [edge]: defect " + ", ".join(k[1] for k in edge)
        options = [("Accept them", "I add them under ## Accepted."),
                   ("Fix them", "I fix them" + " and raise the check limit" * (counted >= allowed) + ".")]
        why = f"check-{last} has only [edge] defects"
    if blocker:
        # Asked and acted on in the builder session only.
        lines = [f"⏸️ {blocker[0].upper()}{blocker[1:]}."] + ([""] + [f"- {d}" for d in details] if details else [])
        for i, (label, say) in enumerate(options):
            lines += ["", ("**➡️ " if i == 0 else "**") + f"{'AB'[i]}. {label}**" + " (recommended)" * (i == 0) + ": " + say]
        blocker = "\n".join(lines + ["", "Reply A or B."])
        step = "human"
    meta = FLOW["steps"].get(step, {})
    seat = seat_for(repo, step, a) if meta else None
    command = {"spec": f"jflow spec {slug}", "build": f"jflow build {slug}", "check": f"jflow check {slug}",
               "fix": fix % n,
               "live": f"Run the live steps of jflow build {slug}, then print the card.",
               "done": f"jflow done {slug}"}.get(step)
    return {"schema_version": 1, "slug": slug, "step": step, "n": n, "role": "human" if blocker else meta.get("role"),
            "model": {k: seat[k] for k in ("model", "vendor", "effort")} if seat else None,
            "command": command, "session": session or meta.get("session"), "blocker": blocker, "why": why}


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
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    rec, summ, val, seat, nxt = map(sub.add_parser, ("record", "summary", "validate", "seat", "next"))
    for p in (rec, summ, val, nxt):
        p.add_argument("slug")
    import jflow_gh
    jflow_gh.add_args(sub, rec, summ, val)
    for p in (summ, nxt):
        p.add_argument("--json", action="store_true")
    nxt.add_argument("--ask", action="store_true", help="print a stop as its question")
    rec.add_argument("step", choices=STEPS)
    rec.add_argument("--model", required=True, type=record_value)
    rec.add_argument("--effort", required=True, type=record_value)
    rec.add_argument("--session", choices=("fresh", "builder"), help="fresh: a builder step in a new session")
    val.add_argument("step", choices=("spec", "check", "accept"))
    seat.add_argument("step")
    for p in (seat, nxt):
        p.add_argument("--config")
        p.add_argument("--builder-vendor", help="builder vendor, if not as configured")
    for p in (rec, summ, seat, nxt, val):
        p.add_argument("--repo", default=".")
    a = parser.parse_args(argv)
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
    # Re-recording replaces the check's line.
    kept = [r for r in read_records(run) if not (a.step == "check" and r.get("step") == "check"
                                                  and r.get("n") == entry["n"])]
    if hub:
        hub.post(a.step, entry)
    else:
        (run / "run.jsonl").write_text("".join(json.dumps(r) + "\n" for r in kept + [entry]), encoding="utf-8")
    print(line(entry["summary"]) if a.step == "done" else json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
