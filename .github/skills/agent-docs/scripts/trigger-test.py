#!/usr/bin/env python3
"""Check which skills each CLI loads for a set of prompts.

Each case runs once per CLI in a fresh empty folder, so no repo context leaks in. The script
reads each run's event stream and records every skill the agent loaded, then checks it against
the case's expectation.

Cases file: one case per line, an expectation and a prompt separated by a tab.
    plain<TAB>Explain in simple terms what a git rebase does.
    !plain<TAB>Give me the output as plain text: the three primary colors.
`NAME` means the skill must load; `!NAME` means it must not. Blank lines and lines starting
with # are skipped.

Usage:
    trigger-test.py CASES [--cli claude,codex,copilot] [--model CLI=MODEL ...] [--keep DIR]

Exit code 0 when every case passes on every CLI, 1 when any fails, 2 on bad input.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

# A cold CLI start plus one skill load and a short answer took 20 to 90 s in testing on
# 2026-10-03; 300 s leaves room for a slow model without hanging the whole run.
TIMEOUT_S = 300
# Six runs at once kept all three CLIs under their rate limits in that test.
PARALLEL = 6
ALL_CLIS = ["claude", "codex", "copilot"]

# Skill loads show up as a skill-tool call ({"skill": "plain"}, Claude Code and Copilot) or as a
# read of the skill's SKILL.md (Codex, and Copilot's file view). Plugin skills may carry a
# "plugin:" prefix, which is dropped.
SKILL_CALL = re.compile(r'"skill"\s*:\s*"(?:[\w-]+:)?([\w.-]+)"')
SKILL_READ = re.compile(r'skills/([\w.-]+)/SKILL\.md')


def command(cli, prompt, model):
    """The non-interactive, read-only command for one CLI."""
    if cli == "claude":
        cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--allowedTools", "Skill Read Glob Grep"]
        return cmd + (["--model", model] if model else [])
    if cli == "codex":
        cmd = ["codex", "exec", "--json", "--skip-git-repo-check", "-s", "read-only"]
        return cmd + (["-m", model] if model else []) + [prompt]
    if cli == "copilot":
        cmd = ["copilot", "-p", prompt, "--output-format", "json", "--allow-all-tools"]
        return cmd + (["--model", model] if model else [])
    raise ValueError(cli)


def run_case(cli, case_no, prompt, model, keep_dir):
    """Run one prompt on one CLI. Returns (skills loaded, error or None)."""
    work = tempfile.mkdtemp(prefix=f"trigger-{cli}-")
    try:
        proc = subprocess.run(command(cli, prompt, model), cwd=work, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=TIMEOUT_S)
        out = proc.stdout + proc.stderr
        if keep_dir:
            with open(os.path.join(keep_dir, f"{cli}-case{case_no}.jsonl"), "w") as f:
                f.write(out)
        skills = set(SKILL_CALL.findall(out)) | set(SKILL_READ.findall(out))
        error = None if proc.returncode == 0 else f"exit {proc.returncode}: {out.strip()[-200:]}"
        return skills, error
    except subprocess.TimeoutExpired:
        return set(), f"timed out after {TIMEOUT_S} s"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def read_cases(path):
    cases = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" not in line:
            sys.exit(f"{path}:{n}: expected 'NAME<TAB>prompt' or '!NAME<TAB>prompt', got: {line[:60]}")
        expect, prompt = line.split("\t", 1)
        must_load = not expect.startswith("!")
        cases.append((expect.lstrip("!").strip(), must_load, prompt.strip()))
    if not cases:
        sys.exit(f"{path}: no cases found")
    return cases


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cases")
    ap.add_argument("--cli", default=",".join(ALL_CLIS), help="comma-separated, default all three")
    ap.add_argument("--model", action="append", default=[], metavar="CLI=MODEL",
                    help="model for one CLI, repeatable; default is each CLI's own default")
    ap.add_argument("--keep", metavar="DIR", help="save each run's raw output here")
    args = ap.parse_args()

    clis = [c.strip() for c in args.cli.split(",") if c.strip()]
    unknown = [c for c in clis if c not in ALL_CLIS]
    if unknown:
        print(f"unknown CLI: {', '.join(unknown)}; choose from {', '.join(ALL_CLIS)}")
        sys.exit(2)
    missing = [c for c in clis if not shutil.which(c)]
    if missing:
        print(f"not installed: {', '.join(missing)}; skipping it. Use --cli to choose.")
        clis = [c for c in clis if c not in missing]
    models = dict(m.split("=", 1) for m in args.model if "=" in m)
    if args.keep:
        os.makedirs(args.keep, exist_ok=True)

    cases = read_cases(args.cases)
    jobs = [(cli, n, case) for n, case in enumerate(cases, 1) for cli in clis]
    with ThreadPoolExecutor(PARALLEL) as pool:
        results = list(pool.map(
            lambda j: run_case(j[0], j[1], j[2][2], models.get(j[0]), args.keep), jobs))

    failed = 0
    for (cli, n, (skill, must_load, prompt)), (skills, error) in zip(jobs, results):
        loaded = skill in skills
        ok = error is None and loaded == must_load
        failed += not ok
        want = f"loads {skill}" if must_load else f"skips {skill}"
        got = ", ".join(sorted(skills)) or "no skill"
        print(f"{'PASS' if ok else 'FAIL'}  {cli:8} case {n}: {want:22} got: {got}")
        if error:
            print(f"      {error}")
        if not ok:
            print(f"      prompt: {prompt[:100]}")
    print(f"\n{len(jobs) - failed}/{len(jobs)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
