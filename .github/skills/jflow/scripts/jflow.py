#!/usr/bin/env python3
"""jflow run record: one JSON line per step in .jflow/<slug>/run.jsonl, and the run's summary.

  jflow.py record <slug> <step> --model M --effort E [--session fresh|builder] [--repo DIR]
  jflow.py summary <slug> [--repo DIR] [--json]
  jflow.py seat <step> [--repo DIR] [--config FILE] [--builder-vendor V]

Standard library only, Python 3.8+. Readers ignore keys and steps they do not know, so drivers
such as a conductor may append their own lines, for example a step "decision".
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
    # Generic sk- needs 20 payload characters to avoid short names; bare tokens need 40.
    return isinstance(value, str) and bool(re.search(r"(?<![\w-])(?:sk-ant-|sk-[A-Za-z0-9_-]{20,}|gh[pousr]_|AKIA)|[A-Za-z0-9_+/=]{40,}", value))


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


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def section(text, heading):
    """Bullet lines under '## heading', minus a placeholder such as '- none' or '- <none ...>'."""
    match = re.search(rf"^## {heading}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    lines = [l for l in (match.group(1).splitlines() if match else []) if l.startswith("- ")]
    return [l for l in lines if not re.match(r"- <?none\b", l, re.I)]


def changed(repo, a, b):
    """True when code outside .jflow/ changed between two commits; None when one is unknown."""
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


def summary(repo, run):
    records = read_records(run)
    spec = (run / "spec.md").read_text(encoding="utf-8")
    base = re.search(r"^Base:\s*(\S+)", spec, re.M)
    if not base:
        raise SystemExit("summary: spec.md has no Base line")
    spec_path = str(run / "spec.md")
    # A finished run ends just before the commit that set Status: done: what done measured, before its
    # own WORKLOG and TODO edits. Later commits belong to other work.
    done_commits = git(repo, "log", "--format=%H", "-S", "Status: done", "--", spec_path).splitlines()
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
    # Receipts are the truth for checks, so runs from before run.jsonl still count.
    checks = [receipt_fields(p) for p in receipts_of(run)]
    # Git counts what an agent can forget to record: a fix round is code changed after a check.
    shas = [c["sha"] for c in checks] + [end]
    fixes = sum(1 for a, b in zip(shas, shas[1:]) if a and changed(repo, a, b))
    steps = [r for r in records if r.get("step") in STEPS]
    # Spec, build and each check are fresh sessions; records add a re-spec or a builder that restarted.
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


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    values = [v for i, v in enumerate(args) if not v.startswith("--repo=") and (not i or args[i - 1] != "--repo")]
    if args and args[0] == "record" and secret(values):
        raise SystemExit("secret-like argument refused")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("slug")
    rec.add_argument("step", choices=STEPS)
    rec.add_argument("--model", required=True)
    rec.add_argument("--effort", required=True)
    rec.add_argument("--session", choices=("fresh", "builder"), help="fresh: a builder step in a new session")
    summ = sub.add_parser("summary")
    summ.add_argument("slug")
    summ.add_argument("--json", action="store_true")
    seat = sub.add_parser("seat")
    seat.add_argument("step")
    seat.add_argument("--config")
    seat.add_argument("--builder-vendor", help="actual builder vendor when its session differs from config")
    for p in (rec, summ, seat):
        p.add_argument("--repo", default=".")
    a = parser.parse_args(argv)
    if a.cmd == "seat":
        if a.step not in STEPS:
            raise SystemExit("unknown flow step")
        config = seats(Path(git(a.repo, "rev-parse", "--show-toplevel")), a.config)
        meta = FLOW["steps"][a.step]
        chosen = config["seats"].get(a.step, config["seats"][meta["seat"]])
        builder = a.builder_vendor or config["seats"]["build"]["vendor"]
        if a.step == "check" and config["different_vendors"] and chosen["vendor"] == builder:
            chosen = config["other_vendor"]
            if chosen["vendor"] == builder:
                raise SystemExit("other_vendor must differ from the builder vendor")
        print(json.dumps(dict(chosen, **meta, step=a.step, rules=RULES)))
        return 0
    if not SLUG.match(a.slug):
        raise SystemExit(f"bad slug: {a.slug}")
    repo = Path(git(a.repo, "rev-parse", "--show-toplevel"))
    run = repo / ".jflow" / a.slug
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
    # Recording a check again, after its receipt changed, replaces that check's line.
    kept = [r for r in read_records(run) if not (a.step == "check" and r.get("step") == "check"
                                                  and r.get("n") == entry["n"])]
    (run / "run.jsonl").write_text("".join(json.dumps(r) + "\n" for r in kept + [entry]), encoding="utf-8")
    print(line(entry["summary"]) if a.step == "done" else json.dumps(entry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
