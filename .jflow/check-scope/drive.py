#!/usr/bin/env python3
"""Run receipt checks against the historical jflow-size-room receipt."""

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ".github/skills/jflow/scripts/jflow.py"
RUN = Path(".jflow/jflow-size-room")
FIRST_RECEIPT = RUN / "receipts/check-1.md"


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)


def validate(repo, receipt_size=None, newline=b"\n"):
    template = (repo / FIRST_RECEIPT).read_bytes().replace(b"# check-1 @", b"# check-2 @", 1)
    template = template.replace(b"\n", newline)
    if receipt_size is not None:
        # A Markdown comment adds bytes while leaving the receipt's verdicts intact.
        start, end = newline + b"<!-- ", b" -->" + newline
        template += start + b"x" * (receipt_size - len(template) - len(start) - len(end)) + end
        assert len(template) == receipt_size
    (repo / RUN / "receipts/check-2.md").write_bytes(template)
    result = subprocess.run(
        [sys.executable, SCRIPT, "validate", "jflow-size-room", "check"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    outcome = " ".join((result.stdout + result.stderr).split())
    label = f"{receipt_size} bytes" if receipt_size is not None else "validate"
    print(f"{label}: exit {result.returncode}: {outcome}")
    return result.returncode


def commit(repo, path):
    git("add", "--", str(path), cwd=repo)
    git("-c", "user.name=jflow", "-c", "user.email=jflow@example.invalid",
        "commit", "--quiet", "--no-gpg-sign", "-m", "Supply scratch input", cwd=repo)


def historical_runs():
    runs = sorted(run for run in (ROOT / ".jflow").iterdir() if run.is_dir() and run.name != "check-scope")
    failed = []
    for run in runs:
        result = subprocess.run(
            [sys.executable, SCRIPT, "validate", run.name, "check"], cwd=ROOT, capture_output=True,
        )
        if result.returncode:
            failed.append(run.name)
    print(f"{len(runs) - len(failed)} of {len(runs)} historical runs pass. Failed: {', '.join(failed)}")
    return int(len(runs) != 9 or failed != ["corrections-bad-records"])


def main(row):
    if row == "8":
        return historical_runs()
    with tempfile.TemporaryDirectory(prefix="jflow-check-scope-") as temp:
        repo = Path(temp) / "repo"
        first_commit = git("log", "-1", "--format=%H", "--diff-filter=A", "--", str(FIRST_RECEIPT))
        git("clone", "--quiet", str(ROOT), str(repo))
        git("checkout", "--quiet", "--detach", first_commit.decode().strip(), cwd=repo)
        if row in ("3", "4", "crlf"):
            with (repo / RUN / "notes.md").open("a") as notes:
                notes.write("\nScratch proof input.\n")
            commit(repo, RUN / "notes.md")
        if row == "other-receipt":
            unrelated = repo / ".jflow/jflow-next/receipts/check-1.md"
            with unrelated.open("a") as receipt:
                receipt.write("\n")
            commit(repo, unrelated)
        if row == "uncommitted":
            git("reset", "--quiet", "HEAD^", cwd=repo)
        (repo / SCRIPT).write_bytes(git("show", f"HEAD:{SCRIPT}"))

        if row == "4":
            above_limit = validate(repo, 3001)
            at_limit = validate(repo, 3000)
            return int(above_limit == 0 or at_limit != 0)
        if row == "crlf":
            return validate(repo, 3001, newline=b"\r\n")
        status = validate(repo)
        if row in ("2", "3"):
            return int((status == 0) != (row == "3"))
        return status


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("2", "3", "4", "8", "crlf", "other-receipt", "uncommitted"):
        sys.exit("Usage: drive.py {2|3|4|8|crlf|other-receipt|uncommitted}")
    sys.exit(main(sys.argv[1]))
