"""jflow.py escaped: record a bug found after done in the run that shipped it.

The record is one appended run.jsonl line with step "escaped"; summary counts them. Accepted
defects stay in spec.md's ## Accepted. .jflow/ mode only. Standard library, Python 3.9+.
"""
import datetime as dt
import json
import subprocess
from pathlib import Path

from jflow_gh import github_mode


def add_args(sub):
    p = sub.add_parser("escaped", help="append a bug found after done to .jflow/<slug>/run.jsonl")
    p.add_argument("slug")
    p.add_argument("text", help="one-line description of the bug")
    p.add_argument("--ref", help="optional reference: an issue, commit or URL")
    p.add_argument("--repo", default=".")


def run(a, refuse_secret, slug):
    refuse_secret([a.slug, a.text, a.ref, a.repo])
    p = subprocess.run(["git", "-C", a.repo, "rev-parse", "--show-toplevel", "HEAD"], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("escaped: not a git repo with a commit")
    top, sha = p.stdout.splitlines()
    repo = Path(top)
    if not slug.match(a.slug) or github_mode(a, repo):
        raise SystemExit("escaped works only on a .jflow/ slug, not in issue and pull request mode")
    run_dir = repo / ".jflow" / a.slug
    if not (run_dir / "spec.md").is_file():
        raise SystemExit(f"escaped: no .jflow/{a.slug}/spec.md")
    text = a.text.strip()
    if len(text.splitlines()) != 1:
        raise SystemExit("escaped needs a one-line description")
    entry = {"v": 1, "step": "escaped", "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "sha": sha, "text": text, **({"ref": a.ref} if a.ref else {})}
    with (run_dir / "run.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return 0
