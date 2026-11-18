"""Replay the check-reach proof against the named Git fixtures."""

from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / ".github/skills/jflow/scripts/jflow.py"
FIXTURE = "b5b2e13"
CHECKED_HEAD = "05054ca"


def run(repo, *args, check=True):
    return subprocess.run(args, cwd=repo, check=check, capture_output=True, text=True)


def cli(repo, *args):
    return run(repo, sys.executable, str(CLI), *args, check=False)


def change_defect(receipt, tag, broken=False):
    if tag:
        receipt, count = re.subn(r"(?m)^- 1\. ", f"- 1. [{tag}] ", receipt)
        assert count == 1
    if broken:
        receipt, count = re.subn(r"(?m)^\| 3 \| PROVED \|.*$", "| 3 | BROKEN | defect 1 |", receipt)
        assert count == 1
    return receipt


def proof(repo, row):
    if row == "7":
        passed, failed = [], []
        for folder in sorted((repo / ".jflow").iterdir()):
            if not folder.is_dir():
                continue
            result = cli(repo, "validate", folder.name, "check")
            if result.returncode:
                detail = (result.stderr or result.stdout).splitlines()[0]
                print(f"{folder.name}: exit {result.returncode}, {detail}")
            if folder.name != "check-reach":
                (failed if result.returncode else passed).append(folder.name)
        print(f"{len(passed)} of {len(passed) + len(failed)} old runs pass; failed: {', '.join(failed)}")
        return

    folder = repo / ".jflow/check-scope"
    allowed = 4 if row == "cap" else 9
    with (folder / "notes.md").open("a", encoding="utf-8") as notes:
        notes.write(f"\nChecks allowed: {allowed}\n")
    receipt = folder / "receipts/check-4.md"
    original = receipt.read_text(encoding="utf-8")
    if row in {"5", "punctuation"}:
        statuses = []
        tags = ("odd", "use", "edge") if row == "5" else ("needs-review",)
        for tag in tags:
            receipt.write_text(change_defect(original, tag), encoding="utf-8")
            result = cli(repo, "validate", "check-scope", "check")
            if result.returncode:
                print(result.stderr.strip() or result.stdout.strip())
            statuses.append(f"[{tag}] exits {result.returncode}")
        print(", ".join(statuses))
        return

    tag = {"1": "edge", "2": "use", "3": "edge", "4": None, "cap": "edge", "duplicate": "use"}[row]
    edited = change_defect(original, tag, broken=row == "3")
    if row == "duplicate":
        edited = edited.replace("\n## Maybes", "- 1. [edge] app.py: a second defect. Evidence: run, failed\n\n## Maybes")
    receipt.write_text(edited, encoding="utf-8")
    run(repo, "git", "add", ".jflow/check-scope")
    run(repo, "git", "commit", "-m", f"Exercise proof row {row}")
    if row == "duplicate":
        validated = cli(repo, "validate", "check-scope", "check")
        print(f"validate exits {validated.returncode}")
    args = () if row == "cap" else ("--json",)
    result = cli(repo, "next", "check-scope", *args)
    print(result.stderr.strip() or result.stdout.strip())
    result.check_returncode()
    if row == "cap":
        # Simulate the code commit option B tells the builder to make.
        path = repo / ".github/skills/jflow/scripts/jflow.py"
        with path.open("a", encoding="utf-8") as script:
            script.write("\n# Simulated fix commit\n")
        run(repo, "git", "commit", "-am", "Simulate following option B")
        after = cli(repo, "next", "check-scope")
        print("After option B's fix commit:")
        print(after.stderr.strip() or after.stdout.strip())
        after.check_returncode()


def main():
    cases = ("1", "2", "3", "4", "5", "7", "cap", "punctuation", "duplicate")
    if len(sys.argv) != 2 or sys.argv[1] not in cases:
        raise SystemExit(f"usage: drive.py {{{','.join(cases)}}}")
    row = sys.argv[1]
    with TemporaryDirectory(prefix="jflow-check-reach-") as scratch:
        repo = Path(scratch)
        run(ROOT, "git", "clone", "--shared", "--quiet", "--", str(ROOT), str(repo))
        run(repo, "git", "checkout", "--detach", CHECKED_HEAD if row == "7" else FIXTURE)
        run(repo, "git", "config", "user.name", "Jflow Proof")
        run(repo, "git", "config", "user.email", "jflow-proof@example.invalid")
        proof(repo, row)


if __name__ == "__main__":
    main()
