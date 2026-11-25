"""jflow.py escaped: record a bug found after done in the run that shipped it.

The record is one appended run.jsonl line with step "escaped"; summary counts them. Accepted
defects stay in spec.md's ## Accepted. .jflow/ mode only. Standard library, Python 3.9+.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

from jflow_gh import github_mode

HEX40 = re.compile(r"[0-9a-f]{40}", re.I)
REV40 = re.compile(r"(?:[A-Za-z0-9_.-]{1,39}:)?[0-9a-f]{40}(?:[~^]\d*)*", re.I)
COMMIT_SEGS = ("commit", "commits", "tree", "blob")


def _add_options(p):
    p.add_argument("slug")
    p.add_argument("text", help="one-line description of the bug")
    p.add_argument("--ref", action="append", default=[], help="optional reference: an issue, commit or URL")
    p.add_argument("--repo", action="append", default=[])


def add_args(sub):
    _add_options(sub.add_parser("escaped", help="append a bug found after done to .jflow/<slug>/run.jsonl"))


def _path_is_secret(path, is_secret):
    return any(is_secret(part) for part in re.split(r"[/\\]+", path))


def _url_ref_is_secret(ref, is_secret):
    try:
        u = urllib.parse.urlsplit(ref)
        host = u.hostname or ""
        _ = u.port
    except ValueError:
        if is_secret(ref):
            return True
        raise SystemExit("escaped: invalid URL in --ref")
    if u.username is not None or u.password is not None or "@" in u.netloc:
        return True
    if is_secret([host, u.query, u.fragment]):
        return True
    segs = u.path.split("/")
    for i, seg in enumerate(segs):
        if is_secret(seg):
            prev = segs[i - 1].lower() if i > 0 else ""
            if REV40.fullmatch(urllib.parse.unquote(seg)) and prev in COMMIT_SEGS:
                continue
            parts = re.split(r"\.{2,3}", seg) if prev == "compare" else []
            if len(parts) == 2 and all(REV40.fullmatch(urllib.parse.unquote(x)) or not is_secret(x) for x in parts):
                continue
            return True
    return False


def _ref_is_secret(ref, repo, is_secret):
    if re.match(r"https?://", ref, re.I):
        return _url_ref_is_secret(ref, is_secret)
    if not is_secret(ref):
        return False
    if HEX40.fullmatch(ref) and repo is not None and subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", ref + "^{commit}"],
        capture_output=True,
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
    if is_secret([a.slug, a.text]) or any(_path_is_secret(r, is_secret) for r in a.repo):
        raise SystemExit("secret-like argument refused")
    if any(_ref_is_secret(r, None, is_secret) and not HEX40.fullmatch(r) for r in a.ref):
        raise SystemExit("secret-like argument refused")
    if len(a.ref) > 1:
        raise SystemExit("escaped: --ref may be given only once")
    if len(a.repo) > 1:
        raise SystemExit("escaped: --repo may be given only once")
    repo_arg = a.repo[0] if a.repo else "."
    ref = a.ref[0] if a.ref else None
    g = subprocess.run(["git", "-C", repo_arg, "rev-parse", "--show-toplevel", "HEAD"], capture_output=True)
    if g.returncode or not g.stdout.endswith(b"\n") or b"\n" not in g.stdout[:-1]:
        raise SystemExit("escaped: not a git repo with a commit")
    top_b, sha_b = g.stdout[:-1].rsplit(b"\n", 1)
    repo, sha = Path(os.fsdecode(top_b)), sha_b.decode("ascii")
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
