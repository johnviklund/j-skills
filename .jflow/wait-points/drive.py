"""Exercise the public CLI in disposable Git repos. Run from the repo root."""
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
SKILL = ROOT / ".github/skills/jflow"
SCRIPT = SKILL / "scripts/jflow.py"
BASE = "43121e6"


def call(args, cwd=ROOT):
    return subprocess.check_output([str(a) for a in args], cwd=cwd, text=True)


class Repo:
    def __init__(self, directory, ask="nothing", gate="none", checks="none"):
        self.path = Path(directory)
        self.git("init", "-q")
        self.git("config", "user.name", "fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.path / "app.py").write_text("x = 1\n")
        self.commit()
        base = self.git("rev-parse", "HEAD").strip()
        self.run = self.path / ".jflow/demo"
        (self.run / "receipts").mkdir(parents=True)
        (self.run / "spec.md").write_text(
            f"# demo\nStatus: ready\nBase: {base}\n\n## Constraints\n"
            f"- Ask first: {ask}\n- Gate: {gate}\n\n## Proof\n"
            "| # | Claim | Surface | Check | Pass signal | Kind | Base |\n"
            "|---|---|---|---|---|---|---|\n"
            "| 1 | a | CLI | run | ok | new | red |\n"
            "| 2 | b | CLI | run | ok | keep | green |\n\n"
            f"## Human checks\n- {checks}\n")
        self.commit()

    def git(self, *args):
        return call(["git", *args], self.path)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture", "--allow-empty")

    def notes(self, text):
        (self.run / "notes.md").write_text(text)
        self.commit()

    def built(self):
        (self.path / "app.py").write_text("x = 2\n")
        self.commit()

    def receipt(self, verdict="PROVED", maybe="none"):
        sha = self.git("rev-parse", "HEAD").strip()
        (self.run / "receipts/check-1.md").write_text(
            f"# check-1 @ {sha} · fixture\n| # | Verdict | Evidence |\n|---|---|---|\n"
            f"| 1 | {verdict} | observed |\n| 2 | PROVED | observed |\n\n"
            f"## Defects\n- none\n\n## Maybes\n- {maybe}\n")
        self.commit()

    def next(self, step, session=None, contains=None):
        args = [sys.executable, SCRIPT, "next", "demo", "--repo", self.path]
        value = json.loads(call(args + ["--json"]))
        assert value["step"] == step, value
        assert value["session"] == session, value
        card = call(args)
        if step == "human":
            assert value["role"] == "human" and value["model"] is None and value["command"] is None, value
            assert contains in value["blocker"], value
            assert card.startswith("The human decides:"), card
        return value


def proof(row):
    with tempfile.TemporaryDirectory() as directory:
        if row == 1:
            r = Repo(directory, gate="publish the release to npm")
            r.built()
            r.receipt("WAITING")
            r.next("human", contains="publish the release to npm")
            r.notes('Yes: gate · "go" · 2026-11-09\n')
            r.next("live", "builder")
            result = "human names gate; card human; committed yes -> live/builder"
        elif row in (2, 5):
            r = Repo(directory, ask="the config.json shape")
            r.next("build", "fresh")
            r.notes("## Approach\nKeep the existing config fields.\n")
            r.next("human", contains="the config.json shape")
            if row == 5:
                r.notes("## Approach\nKeep existing fields.\nYes: gate\nYes: done\n- the human said Yes: approach\n")
                r.next("human", contains="the config.json shape")
                result = "other yes lines and quoted approach -> human"
            else:
                r.notes('## Approach\nKeep existing fields.\nYes: approach · "go" · 2026-11-09\n')
                r.next("build", "builder")
                result = "build/fresh -> human names approach -> build/builder"
        elif row in (3, 4):
            r = Repo(directory, checks="try it on the laptop" if row == 3 else "none")
            r.built()
            r.receipt(maybe="slow on big repos" if row == 4 else "none")
            r.next("human", contains="try it on the laptop" if row == 3 else "slow on big repos")
            r.notes('Yes: done · "go" · 2026-11-09\n')
            r.next("done", "builder")
            result = "human names " + ("human checks" if row == 3 else "maybes") + "; yes -> done"
        elif row == 6:
            r = Repo(directory)
            r.next("build", "fresh")
            r.built()
            r.next("check", "fresh")
            r.receipt()
            r.next("done", "builder")
            spec = r.run / "spec.md"
            spec.write_text(spec.read_text().replace("- none\n", "- try it on the laptop\n"))
            r.receipt("BROKEN")
            r.next("fix", "builder")
            r.receipt("WAITING")
            r.notes("Live done: 2026-11-09\n")
            r.next("check", "fresh")
            result = "build, check, done, fix, check; no human stops"
        else:
            raise ValueError(row)
    print(f"row {row}: PASS; {result}")


def compatibility():
    assert sys.version_info[:2] == (3, 9), sys.version
    call([sys.executable, "-m", "unittest", "discover", "-s", SKILL / "scripts/tests"])
    with tempfile.TemporaryDirectory() as directory:
        archive = subprocess.check_output(["git", "archive", BASE, ".github/skills/jflow"], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(directory)
        old = Path(directory) / ".github/skills/jflow/scripts/jflow.py"
        commands = [("summary", "jflow-config", "--json"), ("seat", "check"),
                    ("seat", "check", "--builder-vendor", "openai")]
        for args in commands:
            before = call([sys.executable, old, *args, "--repo", ROOT])
            after = call([sys.executable, SCRIPT, *args, "--repo", ROOT])
            assert before == after, (args, before, after)
    print("row 8: PASS; Python 3.9 tests OK; summary and both seats match Base byte for byte")


def budget():
    paths = [SKILL / "scripts/jflow.py", SKILL / "scripts/tests"]
    output = call(["git", "diff", "--numstat", BASE, "--", *paths])
    print(output, end="")
    growth = [int(line.split()[0]) - int(line.split()[1]) for line in output.splitlines()]
    files = [SKILL / name for name in ("SKILL.md", "flow.json", "config.json", "scripts/jflow.py")]
    files += [p for p in (SKILL / "references").rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    assert len(growth) == 2 and growth[1] <= growth[0] and size <= 50000, (growth, size)
    print(f"row 9: PASS; script net +{growth[0]}, tests net +{growth[1]}; agent files {size} bytes")


def attack():
    for maybe in ("none", "None.", "<none>", "<none, or for the human only>",
                  "None of the Windows flows were exercised.",
                  "none, except Windows is untested", "None: Windows is untested",
                  "The Windows flows were not exercised."):
        with tempfile.TemporaryDirectory() as directory:
            r = Repo(directory)
            r.built()
            r.receipt(maybe=maybe)
            value = json.loads(call([sys.executable, SCRIPT, "next", "demo", "--repo", r.path, "--json"]))
            placeholder = maybe in ("none", "None.", "<none>", "<none, or for the human only>")
            assert value["step"] == ("done" if placeholder else "human"), value
            if not placeholder:
                assert maybe in value["blocker"], value
            print(f"Maybes '- {maybe}' -> {value['step']}; blocker={value['blocker']}")
    print("attack: PASS; 4 placeholders -> done; 4 real warnings -> human with warning")


if __name__ == "__main__":
    if sys.argv[1] == "attack":
        attack()
    elif sys.argv[1] == "8":
        compatibility()
    elif sys.argv[1] == "9":
        budget()
    else:
        proof(int(sys.argv[1]))
