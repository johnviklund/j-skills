"""check-run.py driven as a subprocess on fixture runs in temp git repos."""
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "check-run.py")
RUN = os.path.join(".workflow", "x")

HEADER = "Command: workflow {cmd} x\nCreated: {created}\nBase: {base}\nInputs: none\nStatus: complete\n"
BRIEF = HEADER.format(cmd="brainstorm", created="2026-10-09", base="{base}") + """
## Problem
p
## Outcome
o
## Behaviours
""" + "".join(f"- B{i} — situation → result\n" for i in range(1, 6)) + """
## Decisions
- D1 — d
## Test seams
- s
## Out of scope
- n

Docs read: none
"""
TICKET = """
### {id} — Ticket
Delivers: {delivers} · Blocked by: none · Lane: logic · Budget: code +20 · tests +30
Seam: s
- [ ] {accept}
Verify: `true` (pre: fails)
Skills: none · Status: todo
"""
PLAN_TAIL = "\n## Coverage\nc\n## Risks\nr\n## TODO impacts\nnone\n## Product doc impacts\nnone\n"


def plan(created="2026-10-09", accept="situation → result", t2_budget=True):
    t2 = TICKET.format(id="T2", delivers="B4, B5", accept="situation → result")
    if not t2_budget:
        t2 = t2.replace(" · Budget: code +20 · tests +30", "")
    return (HEADER.format(cmd="plan", created=created, base="{base}") + "Size: code 10 · tests 5\n"
            + "## Findings\nf\n## Tickets\n"
            + TICKET.format(id="T1", delivers="B1, B2, B3", accept=accept) + t2 + PLAN_TAIL)


def check(files):
    """Commit `files` (run-relative path -> text, `{base}` filled in) into a fresh repo; return check-run's output."""
    with tempfile.TemporaryDirectory() as repo:
        git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True)
        git("-c", "init.defaultBranch=main", "init", "-q")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
        base = git("rev-parse", "--short", "HEAD").stdout.strip()
        for rel, text in files.items():
            path = os.path.join(repo, RUN, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.replace("{base}", base))
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "run")
        r = subprocess.run([sys.executable, SCRIPT, "--repo", repo, "x"], capture_output=True, text=True)
        return r.stdout + r.stderr


class BudgetTests(unittest.TestCase):
    def test_budget_plan_with_size_and_budgets_is_clean(self):
        self.assertIn("0 errors · 0 warnings", check({"brainstorm.md": BRIEF, "plan.md": plan()}))

    def test_budget_missing_on_logic_ticket_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t2_budget=False)})
        self.assertIn("T2: no Budget:", out)

    def test_budget_acceptance_line_over_40_words_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(accept=" ".join(["word"] * 41))})
        self.assertIn("T1: acceptance line has 41 words", out)

    def test_budget_plan_created_before_the_gate_is_not_checked(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(created="2026-10-08", t2_budget=False)})
        self.assertIn("0 errors · 0 warnings", out)


if __name__ == "__main__":
    unittest.main()
