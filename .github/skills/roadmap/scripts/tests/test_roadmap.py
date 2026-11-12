import contextlib
import io
import os
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import roadmap  # noqa: E402

ITEM = """\
### {slug} · {outcome}
Status: {status}
Problem: Admins cannot see an overview of the important data.
  They export three CSVs by hand every Monday.
Impact: ~1 hour a week back for each of 4 admins
Solved when: an admin reads this week's totals in one place.
Budget: about 100 lines
Run: jflow · app
Serves: {serves}
After: {after}
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
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]}).replace("Solved when: an admin reads this week's totals in one place.\n", "")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("missing 'Solved when:'", "\n".join(lines))

    def test_missing_impact_is_an_error(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]}).replace("Impact: ~1 hour a week back for each of 4 admins\n", "")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("missing 'Impact:'", "\n".join(lines))

    def test_options_parses_but_is_stale(self):
        text = roadmap_text(["1. a · why"], {"Features": [item("a")]})
        text = text.replace("Run: jflow · app\n", "Run: jflow · app\nOptions: ➡️ a) a dashboard · b) do nothing\n")
        self.write(text)
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 0)
        self.assertIn("'Options:' picks a fix before jflow spec", "\n".join(lines))

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
        text = text.replace("Run: jflow · app\n", "Run: jflow · app\nOwner: me\n")
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
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a").replace("Serves: One place for the numbers\n", "")]}))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 1)
        self.assertIn("missing 'Serves:'", "\n".join(lines))

    def test_without_product_serves_is_optional(self):
        os.remove(self.product)
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a").replace("Serves: One place for the numbers\n", "")]}))
        code, lines = self.run_cmd("check", self.path)
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["stale: no PRODUCT.md beside the roadmap: the bootstrap skill writes one"])

    def test_product_flag_overrides_the_default(self):
        other = os.path.join(self.tmp.name, "north.md")
        self.write("# X\n## The desired state\n### Speed\n", other)
        self.write(roadmap_text(["1. a · why"], {"Features": [item("a", serves="Speed")]}))
        self.assertEqual(self.run_cmd("check", self.path, "--product", other), (0, []))
