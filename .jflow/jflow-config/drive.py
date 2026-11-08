#!/usr/bin/env python3
"""Checker driver for jflow-config Proof rows 1-7. Run from anywhere: python3 drive.py [row ...]"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/skills/jflow/scripts/jflow.py"
FLOW = json.loads((ROOT / ".github/skills/jflow/flow.json").read_text())
PY = os.environ.get("PY", sys.executable)


def repo():
    d = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q", str(d)], check=True)
    subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                    "--allow-empty", "-m", "init"], check=True)
    return d


def run(d, *args, env=None):
    e = {k: v for k, v in os.environ.items() if k != "JFLOW_CONFIG"}
    e.update(env or {})
    return subprocess.run([PY, str(SCRIPT), *args, "--repo", str(d)], capture_output=True, text=True, env=e)


def seat(model, vendor="v", effort="high", fallback=None):
    return dict(model=model, vendor=vendor, effort=effort, fallback=fallback)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data))


def out(r):
    return json.loads(r.stdout) if r.returncode == 0 else f"exit {r.returncode}: {r.stderr.strip()}"


def row1():
    d = repo()
    for s in ("spec", "build", "fix", "done", "check"):
        o = out(run(d, "seat", s))
        print(s, o["model"], o["effort"], o["fallback"])


def row2():
    d = repo()
    write(d / ".jflow/config.json", {"schema_version": 1, "seats": {"build": seat("repo-b")}})
    env = d / "env.json"
    write(env, {"schema_version": 1, "seats": {"check": seat("env-c", vendor="w")}})
    flag = d / "flag.json"
    write(flag, {"schema_version": 1, "seats": {"check": seat("flag-c", vendor="w")}})
    e = {"JFLOW_CONFIG": str(env)}
    for s in ("build", "check", "spec"):
        print(s, out(run(d, "seat", s, env=e))["model"])
    print("check --config", out(run(d, "seat", "check", "--config", str(flag), env=e))["model"])


def row3():
    d = repo()
    for bad in ("{bad", {"schema_version": 1, "seats": {"build": seat("m", effort=5)}}):
        write(d / ".jflow/config.json", bad)
        r = run(d, "seat", "build")
        print(r.returncode, repr(r.stdout), r.stderr.strip())


def row4():
    d = repo()
    base = {"schema_version": 1, "seats": {"build": seat("gpt-6.1-sol", vendor="openai")}}
    write(d / ".jflow/config.json", base)
    o = out(run(d, "seat", "check"))
    print("on:", o["model"], o["effort"])
    write(d / ".jflow/config.json", dict(base, different_vendors=False))
    o = out(run(d, "seat", "check"))
    print("off:", o["model"], o["effort"])


def row5():
    d = repo()
    print("rules:", out(run(d, "seat", "build"))["rules"])
    for rule in ("public_paid_needs_human", "checker_read_only", "no_secrets"):
        write(d / ".jflow/config.json", {"schema_version": 1, "rules": {rule: False}})
        r = run(d, "seat", "build")
        print(rule, r.returncode, repr(r.stdout), r.stderr.strip())


def row6():
    vals = ["sk-ant-" + "a" * 24, "ghp_" + "b" * 36, "AKIA" + "C" * 16, "aB3dE6gH9jK2mN5pQ8sT1vW4yZ7cF0iL3oR6uX9z"]
    d = repo()
    for v in vals:
        write(d / ".jflow/config.json", {"schema_version": 1, "seats": {"build": seat(v)}})
        r = run(d, "seat", "build")
        print("config", v[:6], r.returncode, "echoed" if v in r.stdout + r.stderr else "not echoed", r.stderr.strip())
    d = repo()
    write(d / ".jflow/t/spec.md", "Status: ready\nBase: HEAD\n")
    log = d / ".jflow/t/run.jsonl"
    write(log, "unchanged\n")
    for v in vals:
        r = run(d, "record", "t", "spec", "--model", v, "--effort", "high")
        print("record", v[:6], r.returncode, "echoed" if v in r.stdout + r.stderr else "not echoed",
              "log unchanged" if log.read_text() == "unchanged\n" else "LOG CHANGED")


def row7():
    d = repo()
    for s, meta in FLOW["steps"].items():
        o = out(run(d, "seat", s))
        print(s, o["role"] == meta["role"], o["model"])
    r = run(d, "seat", "bogus")
    print("bogus", r.returncode, r.stderr.strip())


if __name__ == "__main__":
    for n in sys.argv[1:] or [str(i) for i in range(1, 8)]:
        print(f"--- row {n}")
        globals()[f"row{n}"]()
