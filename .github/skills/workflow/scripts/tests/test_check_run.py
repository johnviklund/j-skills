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


def check(files, ticket=None, args=("x",)):
    """Commit `ticket` (repo-relative path -> text) as T1's commit, then `files` (run-relative path -> text,
    `{base}` and `{t1}` filled in) into a fresh repo; return the output of check-run with `args`."""
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
        r = subprocess.run([sys.executable, SCRIPT, "--repo", repo, *args], capture_output=True, text=True)
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


def sized(budgets):
    delivers = ["B1, B2", "B3", "B4", "B5"]
    tickets = "".join(TICKET.format(id=f"T{i}", delivers=d, accept="situation → result")
                      .replace("code +20", f"code +{b}") for i, (d, b) in enumerate(zip(delivers, budgets), 1))
    return (HEADER.format(cmd="plan", created="2026-10-09", base="{base}") + "Size: code 10 · tests 5\n"
            + "## Findings\nf\n## Tickets\n" + tickets + PLAN_TAIL)


class SizingTests(unittest.TestCase):
    def test_sizing_median_under_40_warns_to_merge(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": sized([20, 30, 30, 50])})
        self.assertRegex(out, r"(?m)^warn .*median code Budget 30 over 4 tickets.*merge")

    def test_sizing_right_sized_plan_only_notes_the_median(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": sized([60, 80, 80, 120])})
        self.assertNotRegex(out, r"(?m)^warn .*median code Budget")
        self.assertRegex(out, r"(?m)^note .*median code Budget 80 over 4 tickets")

    def test_sizing_six_acceptance_lines_are_valid(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(accept="a → b" + "\n- [ ] a → b" * 5)})
        self.assertIn("· 0 errors", out)

    def test_sizing_seven_acceptance_lines_is_an_error(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(accept="a → b\n- [ ] a → b" + "\n- [ ] a → b" * 5)})
        self.assertRegex(out, r"(?m)^ERROR .*T1: 7 acceptance lines; a ticket has 1-6")


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

    def test_budget_values_zero_still_warns_on_overrun(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True).replace("code +20 · tests +30", "code +0 · tests +0", 1)}, self.BIG)
        self.assertIn("T1: net +101 lines, over 2× budget +0", out)

    def test_budget_values_empty_warns_as_missing(self):
        for lane in ("logic", "contract"):
            with self.subTest(lane):
                text = f"Lane: {lane} · Budget:".join(plan().rsplit("Lane: logic · Budget: code +20 · tests +30", 1))
                self.assertIn("T2: no Budget:", check({"brainstorm.md": BRIEF, "plan.md": text}))

    def test_budget_values_zero_with_only_receipts_is_clean(self):
        plan_text = plan(t1_done=True).replace("code +20 · tests +30", "code +0 · tests +0", 1)
        out = check({"brainstorm.md": BRIEF, "plan.md": plan_text}, {"notes/t1-verification.md": lines(101)})
        self.assertIn("0 errors · 0 warnings", out)


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

    def test_operator_risk_empty_warns(self):
        for name in ("plan.md", "patch_plan.md"):
            with self.subTest(name):
                out = check({"brainstorm.md": BRIEF, name: plan(risk="cheap").replace("Risk: cheap", "Risk:")})
                self.assertIn("T3: operator ticket has no Risk:", out)
                self.assertRegex(out, r"(?m)^== x · complete · \d+ errors")


def review(size="", created="2026-10-09"):
    return (HEADER.format(cmd="review", created=created, base="{base}") + "\n## Coverage\n"
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


class CycleTests(unittest.TestCase):
    SIZE = "Size: +40 code · +60 tests · ratio 1.5 · net +100 · over 1,000: none\n"
    LATER = "\n## Cycle 2 findings\n\n## Cycle 2 verdict\nfix\n\n## Cycle 3 findings\n{approval}\n## Cycle 3 verdict\nship\n"

    def run_review(self, created="2026-10-10", approval=""):
        text = review(self.SIZE, created) + self.LATER.format(approval=approval)
        return check({"brainstorm.md": BRIEF, "plan.md": plan(), "review.md": text})

    def test_cycle_three_without_approval_is_an_error(self):
        self.assertRegex(self.run_review(), r"(?m)^ERROR .*Cycle 3 approved by human:")

    def test_cycle_three_with_approval_is_clean(self):
        out = self.run_review(approval="Cycle 3 approved by human: 2026-10-10\n")
        self.assertNotIn("Cycle 3 approved", out)
        self.assertIn("0 errors", out)

    def test_cycle_three_created_before_the_gate_is_not_checked(self):
        out = self.run_review(created="2026-10-09")
        self.assertNotIn("Cycle 3 approved", out)
        self.assertIn("0 errors", out)


DONE_WRAP = HEADER.format(cmd="wrap", created="2026-10-09", base="{base}").replace("complete", "done") + "\nsummary\n"


class WrapTests(unittest.TestCase):
    def test_wrap_done_without_retired_is_an_error(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(), "wrap.md": DONE_WRAP})
        self.assertRegex(out, r"(?m)^ERROR .*wrap.md has no Retired: line")

    def test_wrap_done_with_retired_is_clean(self):
        files = {"brainstorm.md": BRIEF, "plan.md": plan(), "wrap.md": DONE_WRAP + "Retired: none — nothing obsolete\n"}
        worklog = {"WORKLOG.md": "## 2026-10-09 · x · shipped · m\n- Seats: 0 m\n- Skills: workflow@abc\n"}
        self.assertIn("0 errors", check(files, worklog))

    DONE = {"brainstorm.md": BRIEF, "plan.md": plan(), "wrap.md": DONE_WRAP + "Retired: none — nothing obsolete\n"}
    REVIEWED = "Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)\n"

    def worklog(self, header="GPT-6.1 Sol (writer) + Claude Opus 5.5 (reviewer)", seats=True):
        body = f"## 2026-10-09 · x · shipped · {header}\n- Commits: abc\n"
        if seats:
            body += "- Seats: 0 m · 2 m · 3 m · 4 m\n- Skills: workflow@abc\n"
        return {"WORKLOG.md": "# Worklog\n\n" + body + "\n## 2026-10-08 · y · older · m\n- Seats: 0 m\n"}

    def test_wrap_worklog_entry_with_seats_is_clean(self):
        self.assertIn("0 errors", check(self.DONE, self.worklog(), args=("--all",)))

    def test_wrap_worklog_entry_missing_is_an_error(self):
        out = check(self.DONE, {"WORKLOG.md": "# Worklog\n"}, args=("--all",))
        self.assertRegex(out, r"(?m)^ERROR .*WORKLOG.md has no entry for x")

    def test_wrap_worklog_entry_without_seats_is_an_error(self):
        out = check(self.DONE, self.worklog(seats=False), args=("--all",))
        self.assertRegex(out, r"(?m)^ERROR WORKLOG.md:3 .*entry for x has no Seats: line")
        self.assertRegex(out, r"(?m)^ERROR WORKLOG.md:3 .*entry for x has no Skills: line")

    def test_wrap_worklog_unrecorded_reviewer_named_in_review_is_an_error(self):
        size = "Size: +40 code · +60 tests · ratio 1.5 · net +100 · over 1,000: none\n"
        files = dict(self.DONE, **{"review.md": review(size).replace("Independence: cross-vendor\n", self.REVIEWED)})
        out = check(files, self.worklog(header="GPT-6.1 Sol (writer) + reviewer model unrecorded"), args=("--all",))
        self.assertRegex(out, r"(?m)^ERROR WORKLOG.md:3 .*says unrecorded, but review.md names the reviewer")

    def test_wrap_all_warns_on_a_test_reading_the_run_folder(self):
        pin = {"tests/test_x.py": f"open('{RUN}/data.json')\n", "src/x.py": f"open('{RUN}/data.json')\n"}
        out = check({"brainstorm.md": BRIEF, "plan.md": plan()}, pin, args=("--all",))
        self.assertRegex(out, r"(?m)^warn  tests/test_x.py  reads a path inside .workflow")
        self.assertNotIn("src/x.py", out)


if __name__ == "__main__":
    unittest.main()
