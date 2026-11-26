"""Issue and pull request mode against a stateful stub gh: Proof rows 1 to 6 of jflow-issue-pr-mode."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "jflow.py"

STUB = r'''#!{python}
import json, os, re, sys
state_path = os.environ["GH_STUB"]
s = json.load(open(state_path))
args = sys.argv[1:]
if not s["auth"]:
    sys.exit(print("To get started with GitHub CLI, please run:  gh auth login", file=sys.stderr) or 4)
path, query = (args[1].split("?") + [""])[:2]
body = json.loads(sys.stdin.read()) if "--input" in args else None
if "{owner}" in path and not os.path.realpath(os.getcwd()).startswith(s["cwd"]):
    sys.exit(print("gh: cannot infer repository from cwd", file=sys.stderr) or 1)
path = path.replace("{owner}/{repo}", s["nwo"])
if path == "user":
    sys.exit(print(json.dumps({"login": "me"})))
m = re.fullmatch(r"repos/([^/]+/[^/]+)(/issues|/pulls|/collaborators)?(?:/([\w-]+))?(/comments|/timeline|/permission|/labels(?:/[\w-]+)?)?", path)
if not m or m[1] != s["nwo"]:
    sys.exit(print("gh: Not Found (HTTP 404)", file=sys.stderr) or 1)
def stamp():
    s["clock"] += 1
    return s["clock"], "2026-01-01T%02d:%02d:00Z" % divmod(s["clock"], 60)
out = None
if not m[2]:
    out = {"full_name": s["nwo"], "private": s["private"]}
elif m[2] == "/collaborators":
    out = {"permission": s.get("perms", {}).get(m[3], "read")}
elif m[2] == "/pulls" and m[3]:
    out = next(({"number": p["number"], "state": p.get("state", "open"), "head": {"ref": p["head"]}}
                for p in s["pulls"] if str(p["number"]) == m[3]), None)
elif m[2] == "/pulls":
    head = dict(q.split("=", 1) for q in query.split("&") if q).get("head", "")
    out = [{"number": p["number"], "state": p.get("state", "open")} for p in s["pulls"]
           if p.get("owner", "o") + ":" + p["head"] == head]
elif m[4] == "/timeline":
    out = s.get("timeline", {}).get(m[3], [])
elif m[4] and m[4].startswith("/labels"):
    labels = s.setdefault("labels", {}).setdefault(m[3], [])
    if m[4] == "/labels" and body is not None:
        for name in body.get("labels", []):
            if name not in labels:
                labels.append(name)
        out = [{"name": n} for n in labels]
    elif m[4].startswith("/labels/") and "-X" in args and "DELETE" in args:
        name = m[4].split("/", 2)[2]
        if name in labels:
            labels.remove(name)
            out = [{"name": n} for n in labels]
        else:
            out = None
    else:
        out = [{"name": n} for n in labels]
elif m[4]:
    out = s["comments"].setdefault(m[3], [])
    if body is not None:
        n, at = stamp()
        out.append({"id": n, "created_at": at, "body": body["body"], "user": {"login": "me"}})
        out = out[-1]
elif m[3]:
    out = s["issues"].get(m[3])
elif body is not None:
    number = str(max([int(k) for k in s["issues"]] + [100]) + 1)
    s["issues"][number] = dict(body, number=int(number))
    out = s["issues"][number]
else:
    out = list(s["issues"].values())
if out is None:
    sys.exit(print("gh: Not Found (HTTP 404)", file=sys.stderr) or 1)
json.dump(s, open(state_path, "w"))
print(json.dumps(out))
'''

SPEC = """# demo
Status: ready
Base: {base}

## Problem
A fixture run.

## Goals
1. Prove the run.

## Non-goals
- none

## Constraints
- Ask first: {ask}
- Gate: {gate}

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | a | cli | x | y | new | red |
| 2 | b | cli | x | y | keep | green |

## Human checks
{human}
"""

RECEIPT = """# check-{n} @ {sha} · GPT-6.1 Sol · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | {v1} | `cmd` -> ok |
| 2 | {v2} | `cmd` -> ok |

## Defects
{defects}

## Maybes
{maybes}
"""


def receipt(n, sha, v1="PROVED", v2="PROVED", defects="- none", maybes="- <none>"):
    return RECEIPT.format(n=n, sha=sha, v1=v1, v2=v2, defects=defects, maybes=maybes)


class GitHubMode(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.bin, self.bare = self.tmp / "bin", self.tmp / "bare"
        for d in (self.bin, self.bare):
            d.mkdir()
            os.symlink(shutil.which("git"), d / "git")
        (self.bin / "gh").write_text(STUB.replace("{python}", sys.executable))
        (self.bin / "gh").chmod(0o755)
        self.state = self.tmp / "gh.json"
        self.repo = self.make_repo(self.tmp / "repo")
        self.base = self.head()
        self.save({"auth": True, "nwo": "o/r", "private": True, "clock": 0, "pulls": [], "comments": {},
                   "cwd": os.path.realpath(self.repo),
                   "issues": {"42": {"number": 42, "title": "Make it faster", "body": "Original body"}}})

    def make_repo(self, repo):
        repo.mkdir()
        for args in (("init", "-q"), ("config", "user.email", "t@example.com"), ("config", "user.name", "t"),
                     ("config", "commit.gpgsign", "false")):
            self.git(repo, *args)
        (repo / "app.py").write_text("x = 0\n")
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-qm", "base")
        return repo

    def git(self, repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                              text=True).stdout.strip()

    def head(self, repo=None):
        return self.git(repo or self.repo, "rev-parse", "HEAD")

    def code(self, repo=None, text="x = 1\n"):
        repo = repo or self.repo
        with (repo / "app.py").open("a") as f:
            f.write(text)
        self.git(repo, "commit", "-qam", "code")
        return self.head(repo)

    def load(self):
        return json.loads(self.state.read_text())

    def save(self, s):
        self.state.write_text(json.dumps(s))

    def run_jflow(self, *args, path=None, env=None, repo=None, cwd=None):
        full = {k: v for k, v in os.environ.items() if k != "JFLOW_CONFIG"}
        full.update(PATH=str(path or self.bin), GH_STUB=str(self.state), **(env or {}))
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd or repo or self.repo, env=full,
                              capture_output=True, text=True)

    def ok(self, *args, **kw):
        out = self.run_jflow(*args, **kw)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def next(self, slug="#42", **kw):
        return json.loads(self.ok("next", slug, "--json", **kw))

    def file(self, name, text):
        path = self.tmp / name
        path.write_text(text)
        return str(path)

    def post(self, number, kind, body, sha=None, login="me", **attrs):
        """A jflow comment, by default from the gh user."""
        s = self.load()
        s["clock"] += 1
        marker = "".join(f" {k}={v}" for k, v in dict(attrs, sha=sha or self.head()).items())
        s["comments"].setdefault(str(number), []).append({
            "id": s["clock"], "created_at": "2026-01-01T%02d:%02d:00Z" % divmod(s["clock"], 60),
            "body": f"<!-- jflow:{kind} v1{marker} -->\n{body}", "user": {"login": login}})
        self.save(s)

    def spec(self, ask="none", gate="none", human="- none"):
        return SPEC.format(base=self.base, ask=ask, gate=gate, human=human)

    def open_pr(self):
        self.git(self.repo, "checkout", "-qb", "jflow/42")
        s = self.load()
        s["pulls"].append({"number": 7, "head": "jflow/42"})
        self.save(s)

    def record(self, step, *extra):
        return self.ok("record", "#42", step, "--model", "m", "--effort", "high", *extra)

    def assert_no_jflow(self):
        self.assertFalse((self.repo / ".jflow").exists())
        self.assertNotIn(".jflow", self.git(self.repo, "status", "--porcelain", "--untracked-files=all"))

    # Row 1
    def test_entry_points_enter_github_mode_without_jflow_files(self):
        self.post(42, "spec", self.spec())
        s = self.load()
        s["issues"]["43"] = {"number": 43, "title": "jflow: demo", "body": "b"}
        self.save(s)
        self.post(43, "spec", self.spec(), slug="demo")
        external = self.file("config.json", '{"schema_version": 1, "mode": "github"}')
        cases = [("#42", {}, None), ("https://github.com/o/r/issues/42", {}, None),
                 ("demo", {}, "github"), ("demo", {"JFLOW_CONFIG": external}, None)]
        for slug, env, mode in cases:
            with self.subTest(slug=slug, env=env, mode=mode):
                if mode:
                    self.git(self.repo, "config", "jflow.mode", mode)
                n = self.next(slug, env=env)
                self.assertEqual((n["step"], n["slug"]), ("build", "#42" if slug != "demo" else "demo"))
                self.assert_no_jflow()
                self.git(self.repo, "config", "--unset-all", "jflow.mode") if mode else None
        # A plain slug without the setting stays in .jflow/ mode and never calls gh.
        s = self.load()
        s["auth"] = False
        self.save(s)
        self.assertEqual(self.next("demo")["why"], "no spec.md, or it is not ready")

    # Row 2
    def test_full_run_through_comments(self):
        steps = [self.next()["step"]]
        spec = self.file("spec.md", self.spec())
        self.ok("validate", "#42", "spec", "--file", spec)
        self.record("spec", "--file", spec)
        steps.append(self.next()["step"])
        self.open_pr()
        a = self.code()
        steps.append(self.next()["step"])
        r1 = self.file("r1.md", receipt(1, a, v1="BROKEN", defects="- 1. [use] off by one. Evidence: `x` -> 2"))
        self.ok("validate", "#42", "check", "--file", r1)
        self.record("check", "--file", r1)
        n = self.next()
        steps.append(n["step"])
        self.assertIn("check-1 receipt comment on PR #7", n["command"])
        b = self.code(text="x = 2\n")
        self.record("fix")
        steps.append(self.next()["step"])
        r2 = self.file("r2.md", receipt(2, b))
        self.ok("validate", "#42", "check", "--file", r2)
        self.record("check", "--file", r2)
        steps.append(self.next()["step"])
        self.assertIn("jflow:", self.record("done"))
        self.assertEqual(steps, ["spec", "build", "check", "fix", "check", "done"])
        self.assertEqual(self.next()["step"], None)
        s = json.loads(self.ok("summary", "#42", "--json"))
        self.assertEqual({k: s[k] for k in ("checks", "fix_rounds", "rows", "defects", "net_code", "accepted")},
                         {"checks": 2, "fix_rounds": 1, "rows": 2, "defects": 1, "net_code": 2, "accepted": 0})
        state = self.load()
        self.assertEqual(state["issues"]["42"]["body"], "Original body")
        self.assertEqual([c["body"].split()[1] for c in state["comments"]["42"]], ["jflow:spec", "jflow:record"])
        self.assert_no_jflow()

    # Row 3: the same story in a .jflow/ run and in comments gives the same decision at every point.
    STORIES = {
        "approach": [("spec", dict(ask="the marker format")), ("pr",), ("step", "build"),
                     ("notes", "## Approach\n- markers"), ("ask", "approve the approach"),
                     ("notes", 'Yes: approach · "yes" · 2026-11-23'), ("step", "build")],
        "gate": [("spec", dict(gate="deploy to prod")), ("pr",), ("code",), ("receipt", dict(v2="WAITING")),
                 ("ask", "the live gate"), ("notes", 'Yes: gate · "go" · 2026-11-23'), ("step", "live")],
        "done": [("spec", dict(human="- try it on a phone")), ("pr",), ("code",),
                 ("receipt", dict(maybes="- slow on a cold cache")), ("ask", "answer these before done"),
                 ("notes", 'Yes: done · "fine" · 2026-11-23'), ("step", "done")],
        "edits": [("spec", {}), ("pr",), ("code",), ("receipt", {}),
                  ("notes", "## Proposed edits\n- PRODUCT.md: mark the outcome reached"), ("ask", "product.md: mark"),
                  ("notes", 'Yes: edits · "yes" · 2026-11-24'), ("step", "done")],
        "edits-changed": [("spec", {}), ("pr",), ("code",), ("receipt", {}),
                          ("notes", "## Proposed edits\n- PRODUCT.md: mark the outcome reached"),
                          ("notes", "## Proposed edits\n- DESIGN.md: the revised rule"), ("ask", "design.md: the revised"),
                          ("notes", 'Yes: edits · "yes" · 2026-11-24'), ("step", "done")],
        "cap": [("spec", {}), ("pr",)] + [("code",), ("receipt", dict(v1="BROKEN"))] * 3
               + [("ask", "3 checks used of 3"), ("notes", "Checks allowed: 4"), ("step", "fix")],
        "rerun": [("spec", {}), ("pr",), ("code",), ("receipt", dict(v1="BROKEN")), ("code",),
                  ("receipt", dict(v1="BLOCKED")), ("notes", "input for the blocked row"),
                  ("receipt", dict(v1="BROKEN")), ("step", "fix")],
        "edge": [("spec", {}), ("pr",), ("code",), ("receipt", dict(defects="- 1. [edge] odd. Evidence: `x` -> 1")),
                 ("ask", "every open defect is [edge]"), ("accepted", "base"), ("ask", "every open defect is [edge]"),
                 ("accepted", "check"), ("step", "done")],
        "early": [("spec", {}), ("pr",), ("code",), ("accepted", "head"),
                  ("receipt", dict(defects="- 1. [edge] odd. Evidence: `x` -> 1")),
                  ("ask", "every open defect is [edge]")],
    }

    def play(self, story, github):
        """Play a story; return next's decision at each ask or step point."""
        repo = self.repo if github else self.make_repo(self.tmp / f"plain-{story}")
        base, seen, receipts, check_sha = self.head(repo), [], 0, None
        run = repo / ".jflow/demo"

        def write(name, text, append=False):
            path = run / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text((path.read_text() if append and path.exists() else "") + text)
            self.git(repo, "add", ".jflow")
            self.git(repo, "commit", "-qm", name)

        for event, *arg in self.STORIES[story]:
            if event == "spec":
                text = SPEC.format(base=base, **dict(dict(ask="none", gate="none", human="- none"), **arg[0]))
                self.post(42, "spec", text, sha=base) if github else write("spec.md", text)
            elif event == "pr":
                self.open_pr() if github else None
            elif event == "code":
                self.code(repo)
            elif event == "receipt":
                receipts += 1
                check_sha = self.head(repo)
                text = receipt(receipts, check_sha, **arg[0])
                self.post(7, "receipt", text, n=receipts) if github else write(f"receipts/check-{receipts}.md", text)
            elif event == "notes":
                self.post(7, "notes", arg[0] + "\n") if github else write("notes.md", arg[0] + "\n", True)
            elif event == "accepted":
                sha = {"base": base, "check": check_sha, "head": self.head(repo)}[arg[0]]
                line = f'- Defect 1 · odd · "fine" · 2026-11-23 · {sha}'
                if github:
                    self.post(42, "accepted", line + "\n")
                else:
                    spec = (run / "spec.md").read_text()
                    write("spec.md", spec + ("" if "## Accepted" in spec else "\n## Accepted\n") + line + "\n")
            else:
                n = self.next("#42") if github else json.loads(self.ok("next", "demo", "--json", repo=repo))
                if event == "ask":
                    self.assertIn(arg[0], (n["blocker"] or "").lower(), (story, github))
                else:
                    self.assertEqual(n["step"], arg[0], (story, github, n))
                seen.append((n["step"], n["n"], n["role"], bool(n["blocker"]), n["session"], n.get("wait_point")))
        return seen

    def test_wait_points_cap_edge_and_accepted_match_jflow_mode(self):
        for story in self.STORIES:
            with self.subTest(story=story):
                self.setUp()
                self.assertEqual(self.play(story, github=True), self.play(story, github=False))
                self.assert_no_jflow()

    def test_marked_comment_counts_only_from_the_gh_user_or_write_access(self):
        self.post(42, "spec", self.spec(ask="the marker format"))
        self.open_pr()
        self.post(7, "notes", "## Approach\n- markers\n")
        s = self.load()
        s["perms"] = {"reader": "read", "maintainer": "write"}
        self.save(s)
        self.post(7, "notes", 'Yes: approach · "sure" · 2026-11-23\n', login="reader")
        self.assertIn("approve the approach", self.next()["blocker"].lower())
        self.post(7, "notes", 'Yes: approach · "yes" · 2026-11-23\n', login="maintainer")
        self.assertEqual(self.next()["step"], "build")

    def checked_run(self):
        """A recorded spec, a draft pull request, code and a clean check-1."""
        self.record("spec", "--file", self.file("spec.md", self.spec()))
        self.open_pr()
        self.record("check", "--file", self.file("r1.md", receipt(1, self.code())))
        self.assertEqual(self.next()["step"], "done")

    def test_spec_recorded_after_the_newest_check_needs_another_check(self):
        self.checked_run()
        self.record("spec", "--file", self.file("spec2.md", self.spec().replace("| 1 | a |", "| 1 | harder |")))
        self.assertEqual((self.next()["step"], self.next()["n"]), ("check", 2))
        self.record("check", "--file", self.file("r2.md", receipt(2, self.head())))
        self.assertEqual(self.next()["step"], "done")

    def test_spec_comment_with_its_marker_removed_is_refused(self):
        self.checked_run()
        s = self.load()
        s["comments"]["42"][0]["body"] = s["comments"]["42"][0]["body"].split("\n", 1)[1]
        self.save(s)
        out = self.run_jflow("next", "#42")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("changed after record spec", out.stderr)

    def test_repo_option_runs_gh_in_that_clone(self):
        self.checked_run()
        out = self.run_jflow("next", "#42", "--json", "--repo", str(self.repo), cwd=self.tmp)
        self.assertEqual((out.returncode, json.loads(out.stdout or "{}").get("step")), (0, "done"), out.stderr)

    def test_fork_pull_request_found_through_its_issue_reference_open_one_first(self):
        self.record("spec", "--file", self.file("spec.md", self.spec()))
        self.git(self.repo, "checkout", "-qb", "jflow/42")
        self.code()
        s = self.load()
        s["pulls"] += [{"number": 7, "head": "jflow/42", "owner": "fork", "state": "closed"},
                       {"number": 8, "head": "jflow/42", "owner": "fork"}]
        s["timeline"] = {"42": [{"event": "cross-referenced", "source": {"issue": {
            "number": n, "pull_request": {}, "repository": {"full_name": "o/r"}}}} for n in (7, 8)]}
        self.save(s)
        self.assertEqual(self.next()["step"], "check")
        self.ok("note", "#42", "--file", self.file("n.md", "a note\n"))
        self.assertIn("8", self.load()["comments"])
        self.assertNotIn("7", self.load()["comments"])

    def test_spec_recorded_after_done_needs_another_check(self):
        self.checked_run()
        self.record("done")
        self.assertIsNone(self.next()["step"])
        self.record("spec", "--file", self.file("spec2.md", self.spec().replace("| 1 | a |", "| 1 | harder |")))
        self.assertEqual((self.next()["step"], self.next()["n"]), ("check", 2))
        self.record("check", "--file", self.file("r2.md", receipt(2, self.code(text="x = 2\n"))))
        self.record("done")
        s = json.loads(self.ok("summary", "#42", "--json"))
        self.assertEqual((s["net_code"], s["checks"]), (2, 2))

    # Row 4
    def test_jflow_files_on_the_branch_are_refused(self):
        self.post(42, "spec", self.spec())
        self.open_pr()
        (self.repo / ".jflow/42").mkdir(parents=True)
        (self.repo / ".jflow/42/notes.md").write_text("Yes: approach\n")
        self.git(self.repo, "add", ".jflow")
        for state in ("staged", "committed"):
            for args in (("validate", "#42", "check"), ("next", "#42")):
                with self.subTest(state=state, args=args):
                    out = self.run_jflow(*args)
                    self.assertNotEqual(out.returncode, 0)
                    self.assertIn(".jflow/", out.stderr)
            self.git(self.repo, "commit", "-qm", "run files") if state == "staged" else None

    # Row 5
    def test_spec_comment_edited_after_record_spec_is_refused(self):
        self.record("spec", "--file", self.file("spec.md", self.spec()))
        self.open_pr()
        a = self.code()
        self.post(7, "receipt", receipt(1, a), n=1)
        s = self.load()
        s["comments"]["42"][0]["body"] = s["comments"]["42"][0]["body"].replace("| 1 | a |", "| 1 | easier |")
        self.save(s)
        for args in (("validate", "#42", "check"), ("next", "#42")):
            with self.subTest(args=args):
                out = self.run_jflow(*args)
                self.assertNotEqual(out.returncode, 0)
                self.assertIn("changed after record spec", out.stderr)

    # Row 6
    def test_missing_gh_auth_or_pr_fails_on_one_line_without_writes(self):
        self.record("spec", "--file", self.file("spec.md", self.spec()))
        a = self.code()
        r1 = self.file("r1.md", receipt(1, a))
        commands = (("next", "#42"), ("record", "#42", "check", "--model", "m", "--effort", "high", "--file", r1))
        for cause, path, auth, says in (("no gh", self.bare, True, "gh not found"),
                                        ("auth", None, False, "gh auth login"),
                                        ("no PR", None, True, "no linked pull request")):
            s = self.load()
            s["auth"] = auth
            self.save(s)
            for args in commands:
                with self.subTest(cause=cause, cmd=args[0]):
                    before = self.state.read_text()
                    out = self.run_jflow(*args, path=path)
                    self.assertNotEqual(out.returncode, 0)
                    self.assertIn(says, out.stderr)
                    self.assertEqual(len(out.stderr.strip().splitlines()), 1, out.stderr)
                    self.assertNotIn("Traceback", out.stderr)
                    self.assertEqual(json.loads(self.state.read_text())["comments"], json.loads(before)["comments"])
                    self.assert_no_jflow()

    def test_record_spec_labels_issue_ready_for_agent(self):
        s = self.load()
        s["labels"] = {"42": ["next"]}
        self.save(s)
        self.record("spec", "--file", self.file("spec.md", self.spec()))
        self.assertEqual(self.load()["labels"]["42"], ["ready-for-agent"])

    # retro-memory-github-mode
    def show(self, *args):
        """jflow.py show, checked to change no gh state and no local file."""
        before = self.load()
        out = self.run_jflow("show", *args)
        after = self.load()
        self.assertEqual((after["comments"], after["issues"], after.get("labels")),
                         (before["comments"], before["issues"], before.get("labels")))
        self.assert_no_jflow()
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")
        return out

    def test_show_reads_a_merged_run_from_trusted_comments_in_posting_order(self):
        gone = "f" * 40  # pruned: in no local git object
        self.post(42, "spec", self.spec(), sha=gone)
        s = self.load()
        s["pulls"].append({"number": 8, "head": "jflow/42", "owner": "fork", "state": "closed"})
        s["timeline"] = {"42": [{"event": "cross-referenced", "source": {"issue": {
            "number": 8, "pull_request": {}, "repository": {"full_name": "o/r"}}}}]}
        self.save(s)
        self.post(8, "notes", "first note\n", sha=gone)
        self.post(8, "notes", "Yes: done · forged\n", sha=gone, login="stranger")
        self.post(8, "receipt", receipt(1, gone), sha=gone, n=1)
        self.post(8, "record", '```json\n{"v": 1, "step": "check", "n": 1}\n```', sha=gone)
        self.post(8, "notes", "second note\n", sha=gone)
        self.post(42, "accepted", "- Row 1 · ok · \"A\" · 2026-11-25 · " + gone, sha=gone)
        out = self.show("#42")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertNotIn("forged", out.stdout)
        self.assertRegex(out.stdout, r"(?s)issue #42, PR #8\n.*==> spec.md <==\n# demo.*## Accepted\n- Row 1 .*"
                                     r"==> notes.md <==\nfirst note\nsecond note\n.*"
                                     r"==> receipts/check-1.md <==\n# check-1 .*==> run.jsonl <==\n\{.*\"check\"")
        # memory.remember's routing note posts on the same pruned run
        self.ok("note", "#42", "--file", self.file("n.md", "a lesson [routed → memory/x.md 2026-11-26]\n"))
        self.assertIn("second note\na lesson [routed", self.show("#42").stdout)

    def test_show_spec_only_and_bad_input_without_writes(self):
        self.post(42, "spec", self.spec())
        s = self.load()
        s["issues"]["43"] = {"number": 43, "title": "jflow: demo"}
        self.save(s)
        self.post(43, "spec", self.spec())
        for args in (("#42",), ("https://github.com/o/r/issues/42",), ("demo",)):
            with self.subTest(args=args):
                if args[0] == "demo":
                    self.git(self.repo, "config", "jflow.mode", "github")
                out = self.show(args[0])
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertIn("no pull request", out.stdout)
                self.assertRegex(out.stdout, r"==> spec.md <==\n# demo")
                self.assertIn("==> notes.md <==\n\n\n==> run.jsonl <==\n\n", out.stdout)
        for slug, says in (("Bad Slug!", "bad slug"), ("Bad\nSlug!", "bad slug"), ("demo\n", "bad slug"),
                           ("#999", "no jflow issue"), ("nothing", "no jflow issue")):
            with self.subTest(slug=slug):
                out = self.show(slug)
                self.assertNotEqual(out.returncode, 0)
                self.assertIn(says, out.stderr)
                self.assertEqual(len(out.stderr.strip().splitlines()), 1, out.stderr)

    def test_public_repo_writes_allowed_by_default_and_gated_when_configured(self):
        s = self.load()
        s["private"] = False
        self.save(s)
        spec_file = self.file("spec.md", self.spec())
        # Default: allowed on public repo without --confirmed
        self.record("spec", "--file", spec_file)
        # Opt-in via git config: refused without --confirmed, allowed with --confirmed
        subprocess.run(["git", "-C", str(self.repo), "config", "jflow.confirmPublicWrites", "true"], check=True)
        out = self.run_jflow("record", "#42", "spec", "--model", "m", "--effort", "high", "--file", spec_file)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("--confirmed", out.stderr)
        self.record("spec", "--file", spec_file, "--confirmed")


if __name__ == "__main__":
    unittest.main()
