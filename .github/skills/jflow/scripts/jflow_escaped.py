"""jflow.py escaped: record a bug found after done in the run that shipped it.

The record is one appended run.jsonl line with step "escaped"; summary counts them. Accepted
defects stay in spec.md's ## Accepted. .jflow/ mode only. Standard library, Python 3.9+.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from jflow_gh import github_mode

COMMIT_REF = re.compile(r"(?:https?://\S+/commit/)?([0-9a-f]{40})", re.I)


def _add_options(p):
    p.add_argument("slug")
    p.add_argument("text", help="one-line description of the bug")
    p.add_argument("--ref", action="append", default=[], help="optional reference: an issue, commit or URL")
    p.add_argument("--repo", action="append", default=[])


def add_args(sub):
    _add_options(sub.add_parser("escaped", help="append a bug found after done to .jflow/<slug>/run.jsonl"))


def _ref_is_secret(ref, repo, is_secret):
    if not is_secret(ref):
        return False
    m = COMMIT_REF.fullmatch(ref)
    if m and subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", m[1] + "^{commit}"],
        capture_output=True, text=True,
    ).returncode == 0:
        return False
    return True


def run(argv, is_secret, slug):
    raw = sys.argv[1:] if argv is None else list(argv)
    if raw[:1] != ["escaped"]:
        return None

    class _Parser(argparse.ArgumentParser):
        def error(self, msg):
            raise SystemExit("secret-like argument refused" if is_secret(msg) else f"escaped: {msg}")

    p = _Parser(prog="jflow.py escaped", description="append a bug found after done to .jflow/<slug>/run.jsonl")
    _add_options(p)
    a = p.parse_args(raw[1:])
    if is_secret([a.slug, a.text, a.repo]):
        raise SystemExit("secret-like argument refused")
    if any(is_secret(r) and not COMMIT_REF.fullmatch(r) for r in a.ref):
        raise SystemExit("secret-like argument refused")
    if len(a.ref) > 1:
        raise SystemExit("escaped: --ref may be given only once")
    if len(a.repo) > 1:
        raise SystemExit("escaped: --repo may be given only once")
    repo_arg = a.repo[0] if a.repo else "."
    ref = a.ref[0] if a.ref else None
    g = subprocess.run(["git", "-C", repo_arg, "rev-parse", "--show-toplevel", "HEAD"], capture_output=True, text=True)
    if g.returncode or "\n" not in g.stdout[:-1]:
        raise SystemExit("escaped: not a git repo with a commit")
    top, sha = g.stdout[:-1].rsplit("\n", 1)
    repo = Path(top)
    if ref and _ref_is_secret(ref, repo, is_secret):
        raise SystemExit("secret-like argument refused")
    if not slug.match(a.slug) or github_mode(a, repo):
        raise SystemExit("escaped works only on a .jflow/ slug, not in issue and pull request mode")
    run_dir = repo / ".jflow" / a.slug
    if not (run_dir / "spec.md").is_file():
        raise SystemExit(f"escaped: no .jflow/{a.slug}/spec.md")
    text = a.text.strip()
    if len(text.splitlines()) != 1:
        raise SystemExit("escaped needs a one-line description")
    entry = {"v": 1, "step": "escaped", "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "sha": sha, "text": text, **({"ref": ref} if ref else {})}
    log = run_dir / "run.jsonl"
    need_nl = log.is_file() and log.stat().st_size > 0 and log.read_bytes()[-1:] != b"\n"
    with log.open("a", encoding="utf-8") as f:
        f.write(("\n" if need_nl else "") + json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return 0
