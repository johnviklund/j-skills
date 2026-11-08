"""Checker proofs. Run from the repository root with row7 or receipt-sha."""

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


if __name__ == "__main__":
    {"row7": row7, "receipt-sha": receipt_sha}[sys.argv[1]]()
