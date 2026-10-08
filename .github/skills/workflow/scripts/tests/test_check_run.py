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
OPERATOR = """
### T3 — Probe
Delivers: B5 · Blocked by: none · Lane: operator{risk}
Seam: s
- [ ] the receipt shows ok
Verify: receipt: receipts/t3.txt — ok (pre: no receipt)
Skills: none · Status: awaiting-human
"""
PLAN_TAIL = "\n## Coverage\nc\n## Risks\nr\n## TODO impacts\nnone\n## Product doc impacts\nnone\n"


def plan(created="2026-10-09", accept="situation → result", t2_budget=True, t1_done=False, deviation=False,
         risk=None):
    t1 = TICKET.format(id="T1", delivers="B1, B2, B3", accept=accept)
    if t1_done:
        t1 = t1.replace("Status: todo", "Status: done @ {t1}\nWriter: m")
    t2 = TICKET.format(id="T2", delivers="B4, B5", accept="situation → result")
    if not t2_budget:
        t2 = t2.replace(" · Budget: code +20 · tests +30", "")
    return (HEADER.format(cmd="plan", created=created, base="{base}") + "Size: code 10 · tests 5\n"
            + "## Findings\nf\n## Tickets\n" + t1 + t2
            + ("" if risk is None else OPERATOR.format(risk=risk and " · Risk: " + risk)) + PLAN_TAIL
            + ("## Deviations\n- T1: the parser needed a second pass\n" if deviation else ""))


def lines(n):
    return "".join(f"x{i}\n" for i in range(n))


def check(files, ticket=None):
    """Commit `ticket` (repo-relative path -> text) as T1's commit, then `files` (run-relative path -> text,
    `{base}` and `{t1}` filled in) into a fresh repo; return check-run's output."""
    with tempfile.TemporaryDirectory() as repo:
        git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True)
        git("-c", "init.defaultBranch=main", "init", "-q")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
        base = git("rev-parse", "--short", "HEAD").stdout.strip()
        t1 = base
        if ticket:
            write(repo, ticket)
            git("add", "-A")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "T1")
            t1 = git("rev-parse", "--short", "HEAD").stdout.strip()
        write(repo, {os.path.join(RUN, rel): text.replace("{base}", base).replace("{t1}", t1)
                     for rel, text in files.items()})
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "run")
        r = subprocess.run([sys.executable, SCRIPT, "--repo", repo, "x"], capture_output=True, text=True)
        return r.stdout + r.stderr


def write(repo, files):
    for rel, text in files.items():
        path = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


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


class OverrunTests(unittest.TestCase):
    BIG = {"src/app.py": lines(101)}
    TEST_HEAVY = {"src/app.py": lines(12), "tests/test_app.py": lines(178)}

    def test_overrun_net_lines_over_twice_budget_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True)}, self.BIG)
        self.assertIn("T1: net +101 lines, over 2× budget +50", out)

    def test_overrun_with_a_deviation_line_is_quiet(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True, deviation=True)}, self.BIG)
        self.assertNotIn("over 2× budget", out)
        self.assertIn("0 errors · 0 warnings", out)

    def test_overrun_tests_over_three_times_code_is_an_error(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True)}, self.TEST_HEAVY)
        self.assertRegex(out, r"(?m)^ERROR .*T1: tests \+178 over 3× code \+12")

    def test_overrun_plan_created_before_the_gate_is_not_checked(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(created="2026-10-08", t1_done=True)}, self.TEST_HEAVY)
        self.assertIn("0 errors", out)


class OperatorTests(unittest.TestCase):
    PROBE = {"scripts/test_probe.py": "x\n"}

    def test_operator_cheap_ticket_with_a_script_test_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(risk="cheap"), **self.PROBE})
        self.assertIn("T3: cheap operator ticket adds scripts/test_probe.py", out)

    def test_operator_costly_ticket_may_test_its_script(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(risk="costly"), **self.PROBE})
        self.assertIn("0 errors · 0 warnings", out)

    def test_operator_ticket_without_risk_warns(self):
        self.assertIn("T3: operator ticket has no Risk:", check({"brainstorm.md": BRIEF, "plan.md": plan(risk="")}))


def review(size=""):
    return (HEADER.format(cmd="review", created="2026-10-09", base="{base}") + "\n## Coverage\n"
            + "- [x] T1 — acceptance 1/1 tested and passing\n" + size
            + "Independence: cross-vendor\n\n## Cycle 1 findings\n\n## Cycle 1 verdict\nship as-is\n")


class ReviewTests(unittest.TestCase):
    def test_review_coverage_without_size_is_an_error(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(), "review.md": review()})
        self.assertRegex(out, r"(?m)^ERROR .*Coverage has no Size: line")

    def test_review_coverage_with_size_is_clean(self):
        size = "Size: +40 code · +60 tests · ratio 1.5 · net +100 · over 1,000: none\n"
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(), "review.md": review(size)})
        self.assertIn("0 errors", out)


if __name__ == "__main__":
    unittest.main()
