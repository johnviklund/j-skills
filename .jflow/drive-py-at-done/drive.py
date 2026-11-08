"""Checker proofs. Run from the repository root with a named proof."""

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path.cwd()


def git(repo, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check, capture_output=True, text=True,
    )


def row7():
    spec = importlib.util.spec_from_file_location(
        "jflow", ROOT / ".github/skills/jflow/scripts/jflow.py"
    )
    jflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(jflow)
    with tempfile.TemporaryDirectory(prefix="jflow-delete-") as directory:
        repo = Path(directory)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Checker")
        git(repo, "config", "user.email", "checker@example.invalid")
        (repo / "app.py").write_text("print('app')\n")
        driver = repo / ".jflow/x/drive.py"
        driver.parent.mkdir(parents=True)
        driver.write_text("print('proof')\n")
        git(repo, "add", "app.py", ".jflow/x/drive.py")
        git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")
        git(repo, "rm", ".jflow/x/drive.py")
        git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "remove driver")
        result = jflow.changed(repo, "HEAD~1", "HEAD")
        assert result is False, result
        print(result)


def receipt_sha():
    receipt = ".jflow/receipt-evidence-cap/receipts/check-1.md"
    driver = ".jflow/receipt-evidence-cap/drive.py"
    text = (ROOT / receipt).read_text()
    sha = re.search(r"^# check-1 @ ([0-9a-f]+)", text).group(1)
    result = git(ROOT, "show", f"{sha}:{driver}", check=False)
    print(f"receipt header {sha}: git show exits {result.returncode}")
    assert result.returncode != 0
    print(result.stderr.strip())
    containing = git(ROOT, "log", "--diff-filter=A", "--format=%H", "--", receipt).stdout.strip()
    result = git(ROOT, "show", f"{containing}:{driver}")
    assert result.stdout
    print("receipt-containing commit: driver restored successfully")


def receipt_replay():
    receipt = ".jflow/receipt-evidence-cap/receipts/check-1.md"
    driver = ".jflow/receipt-evidence-cap/drive.py"
    containing = git(ROOT, "log", "-1", "--format=%H", "--", receipt).stdout.strip()
    restored = git(ROOT, "show", f"{containing}:{driver}").stdout
    with tempfile.TemporaryDirectory(prefix="jflow-replay-") as directory:
        copy = Path(directory) / "drive.py"
        copy.write_text(restored)
        result = subprocess.run(
            [sys.executable, str(copy), "row4"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        assert "'PROVED': 1, 'BROKEN': 1, 'BLOCKED': 1" in result.stdout, result.stdout
    print("receipt's own commit: restored driver row4 exits 0")


def replay_history():
    with tempfile.TemporaryDirectory(prefix="jflow-history-") as directory:
        repo = Path(directory)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Checker")
        git(repo, "config", "user.email", "checker@example.invalid")
        run = repo / ".jflow/x"
        (run / "receipts").mkdir(parents=True)
        for n in (1, 2):
            (run / "drive.py").write_text(f"print('version {n}')\n")
            (run / f"receipts/check-{n}.md").write_text(f"check {n}\n")
            git(repo, "add", ".jflow")
            git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", f"check {n}")
        git(repo, "rm", ".jflow/x/drive.py")
        git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "done")
        for n in (1, 2):
            receipt = f".jflow/x/receipts/check-{n}.md"
            sha = git(repo, "log", "-1", "--format=%H", "--", receipt).stdout.strip()
            source = git(repo, "show", f"{sha}:.jflow/x/drive.py").stdout
            copy = repo / "drive.py"
            copy.write_text(source)
            result = subprocess.run(
                [sys.executable, str(copy)],
                cwd=repo, check=True, capture_output=True, text=True,
            )
            assert result.stdout.strip() == f"version {n}", result.stdout
        assert not (run / "drive.py").exists()
    print("after deletion: check-1 replays version 1; check-2 replays version 2")


if __name__ == "__main__":
    {
        "row7": row7, "receipt-sha": receipt_sha,
        "receipt-replay": receipt_replay, "replay-history": replay_history,
    }[sys.argv[1]]()
