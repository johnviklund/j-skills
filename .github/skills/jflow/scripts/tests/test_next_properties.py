"""Property tests: random run folders in real git repos, checked against the rules of jflow.py next.

JFLOW_PROP_SEED sets the first seed (default 1) and JFLOW_PROP_RUNS the run count (default 50).
Run i uses seed SEED + i, so a failure's seed reruns alone with JFLOW_PROP_RUNS=1.
"""
import importlib.util
import json
import os
import random
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / "jflow.py"
_spec = importlib.util.spec_from_file_location("jflow_under_test", SCRIPT)
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)
SEED = int(os.environ.get("JFLOW_PROP_SEED", "1"))
RUNS = int(os.environ.get("JFLOW_PROP_RUNS", "50"))
VERDICTS = ["PROVED", "BROKEN", "BLOCKED", "UNREACHABLE", "WAITING"]
MAYBES = ["- <none>", "- none", "- None of the retries are logged", "- slow on a cold cache"]
KINDS = {"approach": "approve the approach", "cap": "checks used of", "stuck": "could not prove",
         "edge": "every open defect is [edge]", "gate": "the live gate", "done": "answer these before done"}


def generate(rng, repo):
    """Build a random run in repo; return its summary with the step the rules expect."""
    def g(*args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c",
                               "commit.gpgsign=false", "-C", str(repo), *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    version = [0]

    def commit(msg, code=False):
        if code:
            version[0] += 1
            (repo / "app.py").write_text(f"v = {version[0]}\n")
        g("add", "-A")
        g("commit", "-qm", msg)
        return g("rev-parse", "HEAD")

    pick = rng.choice
    g("init", "-q")
    base = commit("base", True)
    run = repo / ".jflow" / "p"
    (run / "receipts").mkdir(parents=True)
    d = {"ask": pick(["nothing", "the schema"]), "gate": pick(["none", "deploy"]),
         "human": pick([[], ["try it on a phone"]]), "approach": rng.random() < .5,
         "yes": [p for p in ("approach", "gate", "done") if rng.random() < .4],
         "allowed": [rng.randint(1, 5) for _ in range(pick([0, 0, 1, 2]))], "live_done": rng.random() < .25}
    notes = (["# notes"] + [f'Yes: {p} · "yes" · 2026-11-22' for p in d["yes"]]
             + [f"Checks allowed: {c}" for c in d["allowed"]] + ["Live done: 2026-11-22"] * d["live_done"]
             + ["## Approach", "- plan"] * d["approach"])
    (run / "notes.md").write_text("\n".join(notes) + "\n")
    spec = (f"# p\nStatus: ready\nBase: {base}\n\n## Constraints\n- Ask first: {d['ask']}.\n- Gate: {d['gate']}.\n\n"
            "## Human checks\n" + ("\n".join(f"- {h}" for h in d["human"]) or "- none") + "\n")
    (run / "spec.md").write_text(spec)
    commit("spec")
    if rng.random() < .2:  # no build yet
        d["expected"] = ("human:approach" if d["ask"] != "nothing" and d["approach"] and "approach" not in d["yes"]
                         else "build")
        return d

    k = rng.randint(1, 4)
    pool = pick([["PROVED"], ["PROVED", "WAITING"], ["PROVED", "BLOCKED", "UNREACHABLE"], VERDICTS])
    shas, versions, counts, carries, accepted = [], [], [], [], []

    def accept(lines, msg):
        accepted.extend(lines)
        if lines:
            (run / "spec.md").write_text(spec + "\n## Accepted\n" + "\n".join(accepted) + "\n")
            commit(msg)

    for n in range(1, k + 1):
        sha = commit(f"code {n}", True) if rng.random() < (.8 if n == 1 else .5) else g("rev-parse", "HEAD")
        rows = [(r, pick(pool if n == k else VERDICTS)) for r in range(1, rng.randint(2, 4) + 1)]
        tags = [pick(["use", "edge", None]) for _ in range(pick([0, 0, 1, 2]))]
        carried = {i: rng.randint(1, n - 1) for i in range(1, len(tags) + 1) if n > 1 and rng.random() < .3}
        maybe = pick(MAYBES)
        acc = {}
        if n == k:
            mode = pick(["none", "all", "mixed"])
            keys = [("Row", r) for r, v in rows if v != "PROVED"] + [("Defect", i) for i in range(1, len(tags) + 1)]
            acc = {key: "ok" if mode == "all" else pick(["ok", "sha", "early", "prose", None])
                   for key in keys if mode != "none"}
            acc = {key: v for key, v in acc.items() if v}

            def line(key, v):
                src = carried.get(key[1]) if key[0] == "Defect" and v == "ok" else None
                named = shas[src - 1] if src else base if v == "sha" else sha
                head = f"Defect 99 · same as {key[0]} {key[1]}" if v == "prose" else f"{key[0]} {key[1]} · {v}"
                return f'- {head} · "fine" · 2026-11-22 · {named[:pick([7, 40])]}'

            accept([line(key, v) for key, v in acc.items() if v == "early"], "accept early")
        defects = [f"- {i}. " + (f"[{t}] " if t else "") + f"miss {i}"
                   + (f" (carried from check-{carried[i]})" if i in carried else "") + ". Evidence: x"
                   for i, t in enumerate(tags, 1)]
        (run / f"receipts/check-{n}.md").write_text(
            f"# check-{n} @ {sha} · m · high\n| # | Verdict | Evidence |\n|---|---|---|\n"
            + "".join(f"| {r} | {v} | ev {r} |\n" for r, v in rows)
            + "\n## Defects\n" + ("\n".join(defects) or "- none") + f"\n\n## Maybes\n{maybe}\n")
        commit(f"check {n}")
        shas.append(sha)
        versions.append(version[0])
        counts.append(len(tags))
        carries.append(carried)
    late = rng.random() < 1 / 3
    if late:
        commit("late code", True)
    accept([line(key, v) for key, v in acc.items() if v != "early"], "accept")

    # The oracle, from what was generated.
    def origin(n, i):  # the check a carried defect resolves to: back through each source that has it
        j = carries[n - 1].get(i)
        return origin(j, i) if j and i <= counts[j - 1] else n

    closed = {key for key, v in acc.items() if v == "ok" and (
        key[0] == "Row" or shas[origin(k, key[1]) - 1] == shas[carried.get(key[1], k) - 1])}
    open_rows = [v for r, v in rows if ("Row", r) not in closed]
    open_tags = [t for i, t in enumerate(tags, 1) if ("Defect", i) not in closed]
    counted = sum(a != b for a, b in zip([1] + versions, versions))
    allowed = d["allowed"][-1] if d["allowed"] else 3
    cap = counted >= allowed
    after = any(v != "early" for v in acc.values())
    real_maybe = MAYBES.index(maybe) >= 2
    if late and (not (cap and after) or open_tags or set(open_rows) - {"PROVED"}):
        step = "check"
    elif "BROKEN" in open_rows or set(open_tags) - {"edge"}:
        step = "fix"
    elif {"BLOCKED", "UNREACHABLE"} & set(open_rows):
        step = "human:stuck"
    elif open_tags:
        step = "human:edge"
    elif "WAITING" in open_rows and not d["live_done"]:
        step = "human:gate" if d["gate"] != "none" and "gate" not in d["yes"] else "live"
    elif "WAITING" in open_rows:
        step = "check"
    else:
        step = "human:done" if (d["human"] or real_maybe) and "done" not in d["yes"] else "done"
    if cap and (step == "fix" or step == "check" and late):
        step = "human:cap"
    d.update(receipts=k, versions=versions, late=late, rows=rows, defects=defects, maybe=maybe,
             accepted=accepted, counted=counted, expected=step)
    return d


class NextProperties(unittest.TestCase):
    def test_generated_runs_follow_next_rules(self):
        for seed in range(SEED, SEED + RUNS):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp).resolve()
                d = generate(random.Random(seed), repo)
                n = J.next_step(repo, repo / ".jflow" / "p", SimpleNamespace(config=None, builder_vendor=None))
                got = n["step"] if not n["blocker"] else "human:" + next(
                    (k for k, phrase in KINDS.items() if phrase in n["blocker"].lower()), "?")
                self.assertEqual(got, d["expected"], f"\nseed {seed}: rerun with JFLOW_PROP_SEED={seed} "
                                 f"JFLOW_PROP_RUNS=1\nwhy: {n['why']}\nrun: {json.dumps(d, indent=1)}")


if __name__ == "__main__":
    unittest.main()
