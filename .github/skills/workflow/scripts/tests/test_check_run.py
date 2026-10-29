"""check-run.py driven as a subprocess on fixture runs in temp git repos."""
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "check-run.py")
RUN = os.path.join(".workflow", "x")

HEADER = "Command: workflow {cmd} x\nCreated: {created}\nBase: {base}\nInputs: none\nStatus: complete\n"
BRIEF = HEADER.format(cmd="brainstorm", created="2026-10-09 · m", base="{base}") + """
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
Delivers: {delivers} · Blocked by: none · Lane: logic · Budget: code +20 · tests +30 · why: fixture
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
    created += "" if "·" in created else " · m"
    return (HEADER.format(cmd="plan", created=created, base="{base}") + "Size: code 10 · tests 5\n"
            + "## Findings\nf\n## Tickets\n" + t1 + t2
            + ("" if risk is None else OPERATOR.format(risk=risk and " · Risk: " + risk)) + PLAN_TAIL
            + ("## Deviations\n- T1: the parser needed a second pass\n" if deviation else ""))


def lines(n):
    return "".join(f"x{i}\n" for i in range(n))


def check(files, ticket=None, args=("x",), seed=None, dirty=None):
    """Commit `ticket` dicts in order, then run-relative `files`, filling `{base}`, `{t1}`, `{t2}`.
    Return the subprocess output from check-run with `args`."""
    with tempfile.TemporaryDirectory() as repo:
        git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True)
        git("-c", "init.defaultBranch=main", "init", "-q")
        write(repo, seed or {})
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
        base = git("rev-parse", "--short", "HEAD").stdout.strip()
        shas = {"t1": base}
        for i, changes in enumerate(ticket if isinstance(ticket, list) else [ticket], 1):
            if not changes:
                continue
            write(repo, changes)
            git("add", "-A")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", f"T{i}")
            shas[f"t{i}"] = git("rev-parse", "--short", "HEAD").stdout.strip()
        t1 = shas["t1"]
        write(repo, {os.path.join(RUN, rel): text.replace("{base}", base).replace("{t1}", t1).replace("{t2}", shas.get("t2", t1))
                     for rel, text in files.items()})
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "run")
        write(repo, {os.path.join(RUN, rel): text.replace("{base}", base).replace("{t1}", t1)
                     for rel, text in (dirty or {}).items()})
        r = subprocess.run([sys.executable, SCRIPT, "--repo", repo, *args], capture_output=True, text=True)
        return r.stdout + r.stderr


def write(repo, files):
    for rel, text in files.items():
        path = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


class SeatTests(unittest.TestCase):
    def test_patch_ticket_needs_fixes_metadata(self):
        ticket = TICKET.format(id="C1-T1", delivers="B1", accept="fixed")
        for status, fixes, expected in [("complete", "", "ERROR"), ("drafting", "", "warn "),
                                         ("complete", "Fixes: C1-1 (P1)\n", None)]:
            with self.subTest(status=status, fixes=fixes):
                patch = HEADER.format(cmd="review", created="now", base="{base}").replace("complete", status)
                out = check({"brainstorm.md": BRIEF, "patch_plan.md": patch + ticket + fixes})
                diagnostic = "C1-T1: needs `Fixes: C<n>-<m> (P#)`"
                if expected:
                    self.assertTrue(any(line.startswith(expected) and diagnostic in line for line in out.splitlines()), out)
                else:
                    self.assertNotIn(diagnostic, out)
                    self.assertIn("0 errors · 0 warnings", out)

    def test_brief_trust_boundaries_are_optional(self):
        for section in ("", "## Trust boundaries\n- External request → protected file write\n"):
            with self.subTest(section=section):
                brief = BRIEF.replace("## Test seams", section + "## Test seams")
                out = check({"brainstorm.md": brief, "plan.md": plan()})
                self.assertIn("0 errors · 0 warnings", out)

    def test_brief_and_plan_name_their_model_on_created(self):
        for created, status, warns in (("2026-10-09 · ", "complete", True), ("2026-10-09 · m", "complete", False),
                                       ("2026-10-09 · ", "done", False)):
            with self.subTest(created=created, status=status):
                brief = BRIEF.replace("Created: 2026-10-09 · m", "Created: " + created).replace("complete", status)
                out = check({"brainstorm.md": brief, "plan.md": plan(created=created)}, args=("--all",))
                self.assertEqual(out.count("Created has no model"), 2 if warns else 0, out)


class LimitTests(unittest.TestCase):
    def test_brief_limits(self):
        for count, approval, error in ((9, "", True), (9, "2026-10-18", False),
                                       (8, "", False), (4, "", False), (1, "", False)):
            with self.subTest(count=count, approval=approval):
                brief = BRIEF.replace("2026-10-09", "2026-10-08")
                start, end = brief.index("- B1"), brief.index("## Decisions")
                brief = brief[:start] + "".join(f"- B{i} — input → output\n" for i in range(1, count + 1)) + brief[end:]
                out = check({"brainstorm.md": brief + f"\nSplit declined by human: {approval}\n"})
                if error:
                    self.assertRegex(out, r"(?m)^ERROR .*9 behaviours.*8")
                else:
                    self.assertNotRegex(out, r"(?m)^(ERROR|warn).*behaviours")
                    self.assertIn("0 errors", out)

    def test_parked_brief_uses_the_same_limit(self):
        brief = BRIEF.replace("Status: complete", "Status: parked")
        brief = brief.replace("## Decisions", "".join(f"- B{i} — input → output\n" for i in range(6, 10)) + "## Decisions")
        out = check({"brainstorm.md": brief + "\n## Parked\nResume on request\n"})
        self.assertRegex(out, r"(?m)^ERROR .*9 behaviours; at most 8")

    def test_parked_draft_brief_warns_on_missing_sections(self):
        brief = BRIEF.replace("Status: complete", "Status: parked").replace("## Outcome\no\n", "")
        out = check({"brainstorm.md": brief + "\n## Parked\nResume on request\n"})
        self.assertRegex(out, r"(?m)^warn .*missing section `## Outcome`")
        self.assertIn("0 errors · 1 warnings", out)

    def test_plan_limits(self):
        for count, approval, created, error in ((21, "", "2026-10-18", True),
                (20, "", "2026-10-18", False), (21, "2026-10-18", "2026-10-18", False),
                (21, "", "2026-10-08", True)):
            with self.subTest(count=count, approval=approval, created=created):
                text = sized([60] * 4).replace("2026-10-09", created)
                text = text.replace("- [ ] situation → result\n", "- [ ] situation → result\n" * 5)
                text = text.replace("## Coverage", "- [ ] extra → result\n## Coverage", count - 20)
                brief = BRIEF.replace("2026-10-09", created)
                out = check({"brainstorm.md": brief, "plan.md": text + f"\nSplit declined by human: {approval}\n"})
                if error:
                    self.assertRegex(out, r"(?m)^ERROR .*21 acceptance lines.*20")
                else:
                    self.assertIn("0 errors", out)


class RatioTests(unittest.TestCase):
    def test_growth_net_ratio(self):
        for added, deleted, code, removed, expected in ((201, 305, 89, 313, None),
                (252, 128, 134, 0, None), (90, 0, 60, 0, None), (49, 0, 0, 0, None),
                (130, 10, 60, 0, "120 over 1.5× code +60 (allowed 90)"),
                (91, 0, 60, 0, "91 over 1.5× code +60 (allowed 90)"), (50, 0, 0, 0, "50 over 1.5× code +0 (allowed 0)")):
            with self.subTest(added=added, deleted=deleted, code=code):
                out = check({"brainstorm.md": BRIEF, "plan.md": plan(created="2026-10-19", t1_done=True)},
                            {"src/app.py": lines(code), "tests/test_app.py": lines(added)},
                            seed={"src/app.py": "old\n" * removed, "tests/test_app.py": "old\n" * deleted})
                if expected:
                    self.assertIn("T1: tests net +" + expected, out)
                    self.assertRegex(out, r"(?m)^warn .*T1: tests net")
                else:
                    self.assertIn("0 errors", out)

    def test_growth_budget_waivers(self):
        for deviation, waived in (("Budget waived: T1 — reason", True), ("T1 note", False),
                ("Ratio waived: T1 — wrong kind", False)):
            with self.subTest(deviation=deviation):
                text = plan(created="2026-10-19", t1_done=True) + "## Deviations\n- " + deviation + "\n"
                text = text.replace("tests +30", "tests +30 · why: fixture")
                out = check({"brainstorm.md": BRIEF, "plan.md": text}, {"src/app.py": lines(101)})
                self.assertRegex(out, r"(?m)^" + ("note " if waived else "warn ") + r".*T1:.*net \+101.*budget \+50")
                self.assertIn("0 errors · 0 warnings" if waived else "0 errors · 1 warnings", out)

    def test_committed_test_ratio(self):
        for lane, tests, created, warning in (("logic", 76, "2026-10-18", True),
                ("contract", 76, "2026-10-18", True), ("logic", 75, "2026-10-18", False),
                ("contract", 75, "2026-10-18", False), ("contract", 76, "2026-10-08", True),
                ("contract", 178, "2026-10-08", True), ("mechanical", 178, "2026-10-18", False)):
            with self.subTest(lane=lane, tests=tests, created=created):
                text = plan(created=created, t1_done=True, deviation=True).replace("Lane: logic", f"Lane: {lane}")
                out = check({"brainstorm.md": BRIEF, "plan.md": text},
                            {"src/app.py": lines(50), "tests/test_app.py": lines(tests)})
                self.assertEqual(out.count(f"T1: tests net +{tests} over 1.5× code +50"), int(warning))
                self.assertIn("0 errors", out)

    def test_run_ratio_at_completion(self):
        for tests, status, error in ((151, "done @ {t1}\nWriter: m", True),
                (151, "done @ {t1} · T2 delegated on 2026-10-02\nWriter: m", True),
                (151, "done @ {t1} (proof in receipts/t2.md)\nWriter: m", True),
                (150, "done @ {t1}\nWriter: m", False), (151, "todo", False),
                (151, "awaiting-human", False)):
            with self.subTest(tests=tests, status=status):
                text = plan(t1_done=True).replace("done @ {t1}", "done @ {t2}").replace("Status: todo", "Status: " + status)
                out = check({"brainstorm.md": BRIEF, "plan.md": text, "scripts/later.py": lines(1000)},
                            [{"src/app.py": lines(60), "src/old.py": ""}, {"src/app.py": lines(100), "tests/test_app.py": lines(tests),
                              "notes/receipt.txt": lines(1000)}], seed={"src/old.py": lines(200)})
                self.assertEqual(out.count("run: tests net +151 over 1.5× code added +100 (allowed 150)"), int(error))
                self.assertIn("1 errors" if error else "0 errors", out)

    def test_run_ratio_floor_and_waiver(self):
        for tests, deviation, error, warning in ((99, "", False, False), (100, "", True, False),
                (151, "Ratio waived: run — fixture rewrite", False, True),
                (151, "Ratio waived: T1 — wrong key", True, False),
                (151, "Budget waived: run — wrong kind", True, False),
                (151, "Ratio waived: run —", True, False),
                (151, "\n## Other\nRatio waived: run — outside section", True, False)):
            with self.subTest(tests=tests, deviation=deviation):
                text = plan(t1_done=True).replace("Status: todo", "Status: done @ {t1}\nWriter: m")
                out = check({"brainstorm.md": BRIEF, "plan.md": text + "## Deviations\n- " + deviation + "\n"},
                            {"src/app.py": lines(100 if tests == 151 else 0), "tests/test_app.py": lines(tests)})
                self.assertEqual(out.count(f"run: tests net +{tests}"), int(error or warning))
                self.assertIn("1 errors" if error else "0 errors", out)
                if warning:
                    self.assertRegex(out, r"(?m)^warn .*run: tests net \+151.*fixture rewrite")

    def test_budget_ratio_reason(self):
        for created, why, warning in (("2026-10-18", "", True),
                ("2026-10-18", " · why: x", False), ("2026-10-18", "\nwhy: x", True),
                ("2026-10-08", "", True)):
            with self.subTest(created=created, why=why):
                text = plan(created=created)
                text = text.replace("code +20 · tests +30 · why: fixture", f"code +60 · tests +120{why}", 1)
                out = check({"brainstorm.md": BRIEF, "plan.md": text})
                if warning:
                    self.assertRegex(out, r"(?m)^warn .*T1:.*tests \+120.*code \+60")
                else:
                    self.assertIn("0 errors · 0 warnings", out)


class BudgetTests(unittest.TestCase):
    def test_budget_plan_with_size_and_budgets_is_clean(self):
        self.assertIn("0 errors · 0 warnings", check({"brainstorm.md": BRIEF, "plan.md": plan()}))

    def test_budget_missing_on_logic_ticket_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t2_budget=False)})
        self.assertIn("T2: no Budget:", out)

    def test_budget_acceptance_line_over_40_words_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(accept=" ".join(["word"] * 41))})
        self.assertIn("T1: acceptance line has 41 words", out)

    def test_budget_old_plan_without_budget_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(created="2026-10-08", t2_budget=False)})
        self.assertIn("T2: no Budget: line", out)


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

    def test_overrun_net_lines_over_twice_budget_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True)}, self.BIG)
        self.assertIn("T1: net +101 lines, over 2× budget +50", out)

    def test_overrun_bare_deviation_still_warns(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True, deviation=True)}, self.BIG)
        self.assertIn("T1: net +101 lines, over 2× budget +50", out)
        self.assertIn("0 errors · 1 warnings", out)

    def test_budget_values_zero_still_warns_on_overrun(self):
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True).replace("code +20 · tests +30", "code +0 · tests +0", 1)}, self.BIG)
        self.assertIn("T1: net +101 lines, over 2× budget +0", out)

    def test_budget_values_empty_warns_as_missing(self):
        for lane in ("logic", "contract"):
            with self.subTest(lane):
                text = f"Lane: {lane} · Budget:".join(plan().replace(" · why: fixture", "").rsplit("Lane: logic · Budget: code +20 · tests +30", 1))
                self.assertIn("T2: no Budget:", check({"brainstorm.md": BRIEF, "plan.md": text}))

    def test_budget_values_zero_with_only_receipts_is_clean(self):
        plan_text = plan(t1_done=True).replace("code +20 · tests +30", "code +0 · tests +0", 1)
        out = check({"brainstorm.md": BRIEF, "plan.md": plan_text}, {"notes/t1-verification.md": lines(101)})
        self.assertIn("0 errors · 0 warnings", out)


class TestSmellTests(unittest.TestCase):
    def smells(self, ticket):
        return check({"brainstorm.md": BRIEF, "plan.md": plan(t1_done=True)}, ticket)

    def test_smell_test_importing_a_test_warns(self):
        for line in ("from test_orders import build_order", "from tests.test_orders import x", "import test_orders"):
            with self.subTest(line):
                out = self.smells({"src/app.py": "x\n", "tests/test_cart.py": line + "\n"})
                self.assertIn("T1: tests/test_cart.py imports a test module", out)

    def test_smell_test_reading_sql_text_warns(self):
        out = self.smells({"tests/test_sql.py": 'SQL = (ROOT / "orders.sql").read_text()\n'})
        self.assertIn("T1: tests/test_sql.py reads SQL source text", out)

    def test_smell_fixture_imports_and_code_files_are_clean(self):
        out = self.smells({"tests/test_cart.py": "from fixtures.orders import build_order\n",
                           "src/load.py": 'import test_utils\nQ = open("orders.sql").read()\n'})
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
    def test_review_open_finding_note_tracks_resolution(self):
        for resolved, note in (("—", "1 open `fix now` finding(s)"),
                               ("@ {base}", "no open `fix now` finding")):
            with self.subTest(resolved=resolved):
                finding = f"### P1 — Open\n- Disposition: fix now\n- Resolved: {resolved}\n"
                text = review().replace("## Cycle 1 verdict", finding + "## Cycle 1 verdict")
                out = check({"brainstorm.md": BRIEF, "plan.md": plan(), "review.md": text})
                self.assertIn(note, out)
                self.assertEqual(out.count("open `fix now` finding(s)"), int(resolved == "—"))

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

    def test_cycle_three_old_review_still_needs_approval(self):
        out = self.run_review(created="2026-10-09")
        self.assertRegex(out, r"(?m)^ERROR .*cycle 3 needs")


DONE_WRAP = HEADER.format(cmd="wrap", created="2026-10-09", base="{base}").replace("complete", "done") + "\nsummary\n"


class WrapTests(unittest.TestCase):
    def test_done_ticket_shas_still_warn(self):
        for name in ("plan.md", "patch_plan.md"):
            for sha in ("deadbee", "{t1}"):
                with self.subTest(name=name, sha=sha):
                    text = plan(t1_done=True).replace("{t1}", sha)
                    out = check({"brainstorm.md": BRIEF.replace("Status: complete", "Status: done"),
                                 name: text}, args=("--all",))
                    self.assertIn("0 errors", out)
                    self.assertEqual(out.count("T1: done @ deadbee is not a commit"), int(sha == "deadbee"))
                    self.assertEqual(out.count("warn  "), int(sha == "deadbee"))

    def test_done_resolved_shas_still_warn_without_rule_checks(self):
        for pointer in ("## Cycle 1 findings\n### P1 — Fixed\n- Disposition: fix now\n- Resolved: @ {sha}\n",
                        "## Resolved\n| Finding | Fix |\n| C1-1 | @ {sha} |\n"):
            for sha in ("deadbee", "{t1}"):
                with self.subTest(pointer=pointer, sha=sha):
                    out = check({"brainstorm.md": BRIEF.replace("Status: complete", "Status: done"),
                                 "review.md": review() + pointer.replace("{sha}", sha)}, args=("--all",))
                    self.assertIn("0 errors", out)
                    self.assertEqual(out.count("warn  "), int(sha == "deadbee"))
                    self.assertEqual(out.count("@ deadbee is not a commit"), int(sha == "deadbee"))
                    self.assertNotIn("Size:", out)

    def test_done_brief_skips_rules_only_once_committed(self):
        brief = BRIEF.replace("## Decisions", "".join(f"- B{i} — input → output\n" for i in range(6, 10)) + "## Decisions")
        for state in ("committed", "modified", "untracked", "ignored"):
            with self.subTest(state=state):
                files = {"brainstorm.md": brief, "wrap.md": DONE_WRAP}
                done = brief.replace("Status: complete", "Status: done")
                if state == "committed":
                    files["brainstorm.md"] = done
                elif state in ("untracked", "ignored"):
                    del files["brainstorm.md"]
                out = check(files, args=("--all",),
                            seed={".gitignore": f"{RUN}/brainstorm.md\n"} if state == "ignored" else None,
                            dirty={"notes/dirty.txt": "pending receipt\n"} if state == "committed" else {"brainstorm.md": done})
                if state == "committed":
                    self.assertIn("0 errors · 0 warnings", out)
                else:
                    self.assertRegex(out, r"(?m)^ERROR .*no Retired:")
                    self.assertRegex(out, r"(?m)^ERROR .*9 behaviours; at most 8")

    def test_done_brief_keeps_header_sha_and_layout_checks(self):
        brief = BRIEF.replace("Status: complete", "Status: done")
        for files, expected in (({"brainstorm.md": brief.replace("{base}", "abcdef0")}, "Base abcdef0"),
                ({"brainstorm.md": brief.replace("Command:", "Broken:")}, "provenance header"),
                ({"brainstorm.md": brief, "stray.json": "{}"}, "stray.json")):
            with self.subTest(expected=expected):
                self.assertIn(expected, check(files, args=("--all",)))

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

    def test_wrap_in_progress_notes_net_code_and_tests_since_plan_base(self):
        wrap = HEADER.format(cmd="wrap", created="2026-10-09", base="{base}").replace("complete", "drafting") + "\n## Steps\n"
        seed = {"src/old.py": lines(10), "tests/test_old.py": lines(8)}
        ticket = {"src/x.py": lines(12), "src/old.py": lines(4), "tests/test_x.py": lines(5),
                  "tests/test_old.py": lines(2), "docs/x.md": lines(40)}
        out = check({"brainstorm.md": BRIEF, "plan.md": plan(), "wrap.md": wrap}, ticket, seed=seed)
        self.assertRegex(out, r"(?m)^note .*wrap.md .*run net since plan Base: code \+6 · tests -1 ")

    def test_wrap_all_warns_on_a_test_reading_the_run_folder(self):
        pin = {"tests/test_x.py": f"open('{RUN}/data.json')\n", "src/x.py": f"open('{RUN}/data.json')\n"}
        out = check({"brainstorm.md": BRIEF, "plan.md": plan()}, pin, args=("--all",))
        self.assertRegex(out, r"(?m)^warn  tests/test_x.py  reads a path inside .workflow")
        self.assertNotIn("src/x.py", out)


if __name__ == "__main__":
    unittest.main()
