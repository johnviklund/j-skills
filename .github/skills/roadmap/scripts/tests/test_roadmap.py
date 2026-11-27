import contextlib
import datetime
import io
import os
import json
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import roadmap  # noqa: E402

ITEM = """\
### {slug} · {outcome}

- **Status:** {status}
- **Problem:** Admins cannot see an overview of the important data.
  They export three CSVs by hand every Monday.
- **Impact:** ~1 hour a week back for each of 4 admins
- **Solved when:** an admin reads this week's totals in one place.
- **Budget:** about 100 lines
- **Run:** jflow · app
- **Serves:** {serves}
- **After:** {after}
"""


PRODUCT = """\
# App
## The desired state
### One place for the numbers
## Principles
### Fast exports
"""


def item(slug, status="open", after="none", outcome="an outcome", serves="One place for the numbers"):
    return ITEM.format(slug=slug, status=status, after=after, outcome=outcome, serves=serves)


def roadmap_text(next_lines, groups):
    parts = ["# Roadmap", "Updated: 2026-11-11", "", "## Next up"]
    parts += next_lines
    for group, items in groups.items():
        parts += ["", f"## {group}", ""] + items
    return "\n".join(parts) + "\n"


class Run(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "ROADMAP.md")
        self.product = os.path.join(self.tmp.name, "PRODUCT.md")
        self.write(PRODUCT, self.product)

    def write(self, text, path=None):
        with open(path or self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def run_cmd(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = roadmap.main(list(args))
        return code, out.getvalue().splitlines()


class CheckTest(Run):
    def test_valid_roadmap_is_silent(self):
        self.write(roadmap_text(
            ["1. export-csv · admins ask weekly", "2. fix-login · blocks two users"],
            {"Features": [item("export-csv", serves="Fast exports")], "Bugs": [item("fix-login", after="export-csv")]},
        ))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual((code, lines), (0, []))

    def test_missing_required_field_is_an_error(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]}).replace("- **Solved when:** an admin reads this week's totals in one place.\n", "")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("missing 'Solved when:'", "\n".join(lines))

    def test_missing_impact_is_an_error(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]}).replace("- **Impact:** ~1 hour a week back for each of 4 admins\n", "")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("missing 'Impact:'", "\n".join(lines))

    def test_options_parses_but_is_stale(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]})
        text = text.replace("- **Run:** jflow · app\n", "- **Run:** jflow · app\n- **Options:** ➡️ a) a dashboard · b) do nothing\n")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 0)
        self.assertIn("'Options:' picks a fix before jflow spec", "\n".join(lines))

    def test_plain_fields_parse_but_are_stale(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]})
        text = re.sub(r"^- \*\*([A-Za-z ]+):\*\* ", r"\1: ", text, flags=re.M)
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 0)
        self.assertIn("1 items write fields as plain lines", "\n".join(lines))

    def test_unknown_section_and_duplicate_slug(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")], "Bugs": [item("a")]})
        text += "\n## Ideas\n"
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        out = "\n".join(lines)
        self.assertEqual(code, 1)
        self.assertIn("slug 'a' is used twice", out)
        self.assertIn("'## Ideas' is not a group", out)

    def test_bad_status_and_unknown_field(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a", status="maybe")]})
        text = text.replace("- **Run:** jflow · app\n", "- **Run:** jflow · app\n- **Owner:** me\n")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        out = "\n".join(lines)
        self.assertEqual(code, 1)
        self.assertIn("Status reads open", out)
        self.assertIn("unknown item line", out)

    def test_next_up_limit_and_unknown_slug(self):
        slugs = [f"s{i}" for i in range(6)]
        text = roadmap_text([f"{i + 1}. {s} · why" for i, s in enumerate(slugs)] + ["7. ghost · why"],
                            {"Tooling": [item(s) for s in slugs]})
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        out = "\n".join(lines)
        self.assertEqual(code, 1)
        self.assertIn("Next up holds 7 items; at most 5", out)
        self.assertIn("'ghost', which is not an item", out)

    def test_after_must_exist_unless_archived(self):
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a", after="old-one")]}))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("'old-one', which is in neither", "\n".join(lines))
        self.write("# Archive\n\n### old-one · shipped\nStatus: done 2026-11-01 abc1234\n",
                   os.path.join(self.tmp.name, "ROADMAP_ARCHIVE.md"))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual((code, lines), (0, []))

    def test_stale_findings_do_not_fail(self):
        text = roadmap_text(
            ["1. b · why", "2. a · why"],
            {"Features": [item("a", status="done 2026-11-10 d55d0e1"), item("b", after="c"), item("c")]},
        )
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        out = "\n".join(lines)
        self.assertEqual(code, 0)
        self.assertIn("stale: line", out)
        self.assertIn("a: done, move it to the archive", out)
        self.assertIn("Next up names 'a', which is done", out)
        self.assertIn("'b' waits for 'c'", out)

    def test_repo_runs_show_done_and_started(self):
        repo = os.path.join(self.tmp.name, "app")
        for slug, status in (("a", "done"), ("b", "ready")):
            os.makedirs(os.path.join(repo, ".jflow", slug))
            self.write(f"# {slug}\nStatus: {status}\nBase: abc1234\n", os.path.join(repo, ".jflow", slug, "spec.md"))
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a"), item("b")]}))
        code, lines = self.run_cmd("check", self.path, "--repo", repo)
        out = "\n".join(lines)
        self.assertEqual(code, 0)
        self.assertIn("a: its jflow run in app is done", out)
        self.assertIn("b: its jflow run in app has started", out)

    def test_missing_file_names_the_problem(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_cmd("check", os.path.join(self.tmp.name, "nope.md"))
        self.assertIn("cannot read", str(cm.exception.code))


class NextTest(Run):
    def test_next_lists_status(self):
        self.write(roadmap_text(["1. a · why", "2. b · why"],
                                {"Features": [item("a", status="started"), item("b")]}))
        code, lines = self.run_cmd("next", self.path)
        self.assertEqual((code, lines), (0, ["1. a · started", "2. b · open"]))

    def test_next_empty(self):
        self.write(textwrap.dedent("""\
            # Roadmap
            ## Next up
            """))
        self.assertEqual(self.run_cmd("next", self.path), (0, ["Next up is empty"]))


if __name__ == "__main__":
    unittest.main()


class ProductTest(Run):
    def test_serves_must_name_a_product_heading(self):
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a", serves="World peace"), item("b", serves="Fast exports")]}))
        code, lines = self.run_cmd("check", self.path)
        out = "\n".join(lines)
        self.assertEqual(code, 1)
        self.assertIn("Serves 'World peace' is not a heading in PRODUCT.md", out)
        self.assertIn("outcome 'One place for the numbers' has no open item", out)

    def test_missing_serves_is_an_error_when_product_exists(self):
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a").replace("- **Serves:** One place for the numbers\n", "")]}))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("missing 'Serves:'", "\n".join(lines))

    def test_without_product_serves_is_optional(self):
        os.remove(self.product)
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a").replace("- **Serves:** One place for the numbers\n", "")]}))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["stale: no PRODUCT.md beside the roadmap: the bootstrap skill writes one"])

    def test_product_flag_overrides_the_default(self):
        other = os.path.join(self.tmp.name, "north.md")
        self.write("# X\n## The desired state\n### Speed\n", other)
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a", serves="Speed")]}))
        self.assertEqual(self.run_cmd("check", self.path, "--product", other), (0, []))


FAKE_GH = """\
#!/usr/bin/env python3
import os, sys
with open(os.environ["FAKE_GH_LOG"], "a") as f:
    f.write(" ".join(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_GH_FAIL"):
    sys.stderr.write(os.environ["FAKE_GH_FAIL"] + "\\nrun gh auth login\\n")
    sys.exit(4)
sys.stdout.write(open(os.environ["FAKE_GH_JSON"]).read())
"""


def issue(number, labels=(), body="- **Problem:** p\n- **Solved when:** s\n- **Serves:** x\n", comments=()):
    return {"number": number, "title": f"issue {number}", "labels": [{"name": l} for l in labels],
            "body": body, "comments": [{"body": c} for c in comments]}


def card(order, extra=""):
    """A Next issue body with every field a Next card needs."""
    return ("- **Problem:** p\n- **Solved when:** s\n- **Serves:** x\n- **Helps:** h\n- **Moves:** m\n"
            f"- **Grounded in:** g\n- **Confidence:** High\n- **Order:** {order}\n{extra}")


class GitHubTest(unittest.TestCase):
    """GitHub mode and the wiki scan, against a fake gh on PATH in a temp git repo."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.repo = os.path.join(self.dir, "repo")
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        bin_dir = os.path.join(self.dir, "bin")
        os.mkdir(bin_dir)
        with open(os.path.join(bin_dir, "gh"), "w") as f:
            f.write(FAKE_GH)
        os.chmod(os.path.join(bin_dir, "gh"), 0o755)
        self.log = os.path.join(self.dir, "gh.log")
        self.fixture = os.path.join(self.dir, "issues.json")
        env = {"PATH": bin_dir + os.pathsep + os.environ["PATH"], "FAKE_GH_LOG": self.log,
               "FAKE_GH_JSON": self.fixture, "FAKE_GH_FAIL": ""}
        old = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        self.addCleanup(lambda: [os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
                                 for k, v in old.items()])
        cwd = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, cwd)

    def issues(self, items):
        with open(self.fixture, "w") as f:
            json.dump(items, f)

    def git_config(self, key, value):
        subprocess.run(["git", "config", key, value], check=True)

    def run_cmd(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = roadmap.main(list(args))
        return code, out.getvalue().splitlines()

    def gh_calls(self):
        with open(self.log) as f:
            return f.read().splitlines()

    def test_board_next_and_check(self):
        with open("PRODUCT.md", "w") as f:
            f.write("# App\n")
        self.issues([issue(n, ["next"], body=card(n)) for n in range(1, 7)]
                    + [issue(7, ["next", "in-progress"]), issue(8, body="Just an idea."),
                       issue(9, ["needs-human"])])
        self.git_config("jflow.mode", "github")
        code, lines = self.run_cmd("next")
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["Next:"] + [f"  #{n} · issue {n}" for n in range(1, 7)]
                         + ["Backlog:", "  #8 · issue 8"])
        code, lines = self.run_cmd("check")
        self.assertEqual(code, 1)
        self.assertEqual(lines, [
            "error: Next holds 6 issues labelled 'next'; at most 5",
            "stale: #7: in flight but still labelled 'next'; remove the label",
            "stale: #8: body has no 'Problem:', 'Solved when:', 'Serves:'",
        ])
        self.assertTrue(all(c.startswith("issue list --state open") for c in self.gh_calls()))
        # A FILE named on the command line stays in file mode.
        with self.assertRaises(SystemExit) as cm:
            self.run_cmd("check", "ROADMAP.md")
        self.assertIn("cannot read ROADMAP.md", str(cm.exception.code))

    def test_next_card_fields_order_and_challenges(self):
        def check(items, product=False):
            if product:
                with open("PRODUCT.md", "w") as f:
                    f.write("# App\n")
            elif os.path.exists("PRODUCT.md"):
                os.remove("PRODUCT.md")
            self.issues(items)
            return self.run_cmd("check", "--github")

        bare = "- **Problem:** p\n- **Solved when:** s\n"
        cases = [
            ("Next card without its confidence fields",
             [issue(1, ["next"], body=bare + "- **Order:** 1\n")], False,
             (0, ["stale: #1: in Next but body has no 'Helps:', 'Moves:' or 'Challenges:', "
                  "'Grounded in:', 'Confidence:'"])),
            ("challenges card needs neither Moves nor Serves",
             [issue(1, ["next", "challenges"], body=bare + "- **Helps:** h\n- **Challenges:** c\n"
                    "- **Grounded in:** g\n- **Confidence:** High\n- **Order:** 1\n")], True, (0, [])),
            ("bad Confidence, duplicate Order, After inversion",
             [issue(10, ["next"], body=card(1).replace("High", "80%") + "- **After:** #20\n"),
              issue(20, ["next"], body=card(1).replace("High", "Medium") + "- **After:** none\n")], False,
             (0, ["stale: #10: Confidence '80%' is not High, Medium or Low",
                  "stale: #10: After #20, but Next starts #20 later; raise its Order",
                  "stale: #20: Order 1 is also #10's; give each Next issue its own"])),
            ("Backlog may stay rough", [issue(1, body=bare)], False, (0, [])),
            ("empty fields count as missing",
             [issue(1, ["next"], body=bare + "- **Helps:**\n- **Moves:** \n- **Grounded in:**\n"
                    "- **Confidence:**\n- **Order:** 1\n")], False,
             (0, ["stale: #1: in Next but body has no 'Helps:', 'Moves:' or 'Challenges:', "
                  "'Grounded in:', 'Confidence:'"])),
        ] + [(f"Order {bad}", [issue(1, ["next"], body=card(bad))], False,
              (0, [f"stale: #1: Order '{bad}' is not a whole number from 1 to 5"]))
             for bad in ("0", "6", "1.5", "1/2")]
        for name, items, product, want in cases:
            with self.subTest(name):
                self.assertEqual(check(items, product), want)

        self.issues([issue(10, ["next"], body=card(2)), issue(20, ["next"], body=card(1)),
                     issue(5, ["next"], body=card("?")), issue(30, body=bare)])
        self.assertEqual(self.run_cmd("next", "--github")[1],
                         ["Next:", "  #20 · issue 20", "  #10 · issue 10", "  #5 · issue 5", "Backlog:", "  #30 · issue 30"])

    def test_gh_missing_or_unauthenticated_fails_in_one_line(self):
        empty = os.path.join(self.dir, "empty")
        os.mkdir(empty)
        for env, cause in (({"PATH": empty}, "error: gh is not installed or not on PATH"),
                           ({"FAKE_GH_FAIL": "To get started with GitHub CLI, please run: gh auth login"},
                            "error: gh failed: To get started with GitHub CLI, please run: gh auth login")):
            with self.subTest(cause=cause):
                saved = {k: os.environ[k] for k in env}
                os.environ.update(env)
                try:
                    with self.assertRaises(SystemExit) as cm:
                        self.run_cmd("next", "--github")
                finally:
                    os.environ.update(saved)
                self.assertEqual(cm.exception.code, cause)
        self.assertEqual(os.listdir(self.repo), [".git"])

    def test_wiki_scan(self):
        self.assertEqual(self.run_cmd("wiki"), (0, []))  # no wiki folder set: silent, no gh call
        self.assertFalse(os.path.exists(self.log))
        wiki = os.path.join(self.dir, "wiki")
        os.makedirs(os.path.join(wiki, "topic"))
        for name, days_old in (("old.md", 30), ("topic/linked.md", 1), ("topic/fresh.md", 1), ("notes.txt", 1)):
            path = os.path.join(wiki, name)
            with open(path, "w") as f:
                f.write("page\n")
            t = (datetime.datetime.now() - datetime.timedelta(days=days_old)).timestamp()
            os.utime(path, (t, t))
        self.issues([issue(3, comments=["See wiki/topic/linked.md for the evidence."])])
        self.assertEqual(self.run_cmd("wiki", "--wiki", wiki), (0, ["topic/fresh.md"]))
        self.git_config("roadmap.wikiPath", wiki)
        old = (datetime.date.today() - datetime.timedelta(days=60)).isoformat()
        self.assertEqual(self.run_cmd("wiki", "--since", old), (0, ["old.md", "topic/fresh.md"]))
        self.git_config("roadmap.wikiLastScan", old)
        self.assertEqual(self.run_cmd("wiki"), (0, ["old.md", "topic/fresh.md"]))
        self.git_config("roadmap.wikiLastScan", datetime.date.today().isoformat())
        self.assertEqual(self.run_cmd("wiki"), (0, []))

    def test_wiki_reference_names_the_page_path(self):
        # check-1 defects 1 and 2: a same-named page in another folder, and a percent-encoded link.
        # check-2 defects 1 and 2: a link with a title, and a URL with a query string.
        wiki = os.path.join(self.dir, "wiki")
        for name in ("alpha/plan.md", "beta/plan.md", "plan.md", "release plan.md", "titled.md", "query.md"):
            os.makedirs(os.path.dirname(os.path.join(wiki, name)), exist_ok=True)
            with open(os.path.join(wiki, name), "w") as f:
                f.write("page\n")
        self.issues([issue(3, comments=[
            "See wiki/alpha/plan.md and [Evidence](wiki/release%20plan.md).",
            '[Source](wiki/titled.md "Source page")',
            "https://github.com/o/r/blob/main/wiki/query.md?plain=1",
        ])])
        self.assertEqual(self.run_cmd("wiki", "--wiki", wiki), (0, ["beta/plan.md", "plan.md"]))
