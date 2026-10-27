#!/usr/bin/env python3
"""Check a workflow run folder against the shapes the workflow skill defines.

Checks what a script can count, so no phase has to eyeball it:
- every artifact opens with the five-line provenance header, `Status:` holds a known value,
  a brief or plan in a run not yet done names its model on `Created:`, and every sha in `Base:` / `Inputs:` / `done @` / `Resolved: @` exists in git;
- budgets: brainstorm ~80 lines and 1-8 behaviours, plan ~120 lines, 8 tickets and 20 acceptance lines,
  review ~100 lines, a done wrap ~40 lines;
- the brief: required sections, `B# — situation → result` behaviours, prototype notes;
- tickets in plan.md / patch_plan.md: Delivers · Blocked by · Lane, Seam, 1-6 acceptance lines,
  Verify with `pre:`, Skills paths, Status; every behaviour delivered by a ticket; no
  blocked-by cycle; operator tickets verify a receipt;
- slop guards for every run not yet done: a `Budget:` on logic and contract plan
  tickets, and their median code Budget (under MERGE_BELOW over 4+ tickets warns: merge), acceptance lines of at most ACCEPT_WORDS words; a done ticket's commit within
  OVERRUN× its budget; ticket test ratios warn, and the completed-run test ratio gates before review;
  run ratio and ticket budget waivers need a reason under `Ratio waived:` or `Budget waived:`;
  added test lines that import a test module or read SQL source text warn (tests.md);
  a `Risk:` on operator tickets, and no script test in the run's `scripts/` for a `cheap` one;
  a `Size:` line in a complete review's Coverage; a wrap in progress notes the run's net code and test
  lines since plan.md's Base; a `Retired:` line in a done wrap, and a
  WORKLOG.md entry for the run with `Seats:` and `Skills:` that names a reviewer review.md names;
- review.md: findings with a disposition, P0/P1 deferrals approved, a verdict once complete; a third or later cycle carries `Cycle N approved by human:`;
- the folder: only the artifacts at the top level, everything else in a known subfolder;
- `--all` only: a tracked test file outside the run folders that names a path inside one.

A run whose brief is marked done, tracked and clean is history: it gets header, sha and layout
checks only, including under `--all`. Uncommitted done briefs still receive the rule checks.

Runs in the v2.02 shape (plan.md with `## Checklist`, no `## Behaviours`) get header, budget and
layout checks only; their ticket and brief checks are skipped with a note.

Usage:
    check-run.py [SLUG | RUN_DIR ...] [--repo DIR] [--all]

No SLUG checks every run that is not parked or done (a broken Status is checked, not hidden);
`--all` adds parked and done runs. Run from the repo root, or pass `--repo`. Needs Python 3.8+ and git.
Exit 0 with no errors (warnings allowed), 1 with any error, 2 on bad input.
"""
import argparse
import os
import re
import statistics
import subprocess
import sys

ARTIFACTS = ["brainstorm.md", "plan.md", "patch_plan.md", "review.md", "learnings.md", "wrap.md"]
SUBFOLDERS = ["receipts", "screens", "notes", "scripts", "data", "prototypes", "understand"]
HEADER = ["Command", "Created", "Base", "Inputs", "Status"]
STATUSES = {"drafting", "complete", "parked", "done"}
LANES = {"mechanical", "logic", "contract", "operator"}
# Line budgets from SKILL.md *Budgets*; wrap's ~40 applies only once the run is done.
BUDGET = {"brainstorm.md": 80, "plan.md": 120, "review.md": 100}
WRAP_DONE_BUDGET = 40
LEAN_BEHAVIOURS_MAX, PLAN_ACCEPT_MAX = 8, 20  # lean runs: split above either total
MAX_TICKETS = 8                            # phase-2-plan §5
ACCEPT_MIN, ACCEPT_MAX = 1, 6              # phase-2-plan §3 *Right-sized*
MAX_PROTOTYPES = 3                         # phase-0-brainstorm §3a
BIG_FILE = 100_000                         # wrap 9b flags files over ~100 KB
ACCEPT_WORDS = 40                          # phase-2-plan asks ~25; warn above this
OVERRUN = 2                                # a ticket commit's net lines over 2× its Budget warns
TEST_RATIO, TEST_FLOOR = 1.5, 50           # ticket warning: tests net ≥ 50 and over 1.5× code added
RUN_TEST_FLOOR = 100                      # run gate: ignore smaller test changes
MERGE_BELOW, MERGE_MIN_TICKETS = 40, 4      # a median code Budget under 40 over 4+ tickets warns: merge
RECEIPTS = r"\.(md|txt)$|^[.]workflow/[^/]+/(screens|prototypes|understand)/"
TEST_FILE = r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*$|_test\.[^/]*$|\.(test|spec)\.[^/]*$"
TEST_IMPORT = r"^\s*(from\s+\.*(\w+\.)*test_\w*\s+import|import\s+(\w+\.)*test_\w*)\b"   # tests.md: no test imports a test
SQL_TEXT = r"\.sql\b.*\b(read_text|open)\(|\b(read_text|open)\(.*\.sql\b"            # tests.md: never assert source text
BRIEF_SECTIONS = ["Problem", "Outcome", "Behaviours", "Decisions", "Test seams", "Out of scope"]
PLAN_SECTIONS = ["Findings", "Tickets", "Coverage", "Risks", "TODO impacts", "Product doc impacts"]

SHA = r"[0-9a-f]{7,40}"
DASH = r"\s+[—–-]\s+"                     # the templates use an em dash; accept a plain one too


class Report:
    def __init__(self, repo):
        self.repo, self.errors, self.warnings, self.notes = repo, [], [], []
        self.done = False                  # a done run is history: a lost sha only warns

    def missing_sha(self, path, line, msg):
        if self.done:
            self.warn(path, line, msg + " (history rewritten after the run?)")
        else:
            self.error(path, line, msg + ": the pointer is dangling; find the right sha with git log")

    def _where(self, path, line):
        rel = os.path.relpath(path, self.repo)
        return f"{rel}:{line}" if line else rel

    def error(self, path, line, msg):
        self.errors.append(f"ERROR {self._where(path, line)}  {msg}")

    def warn(self, path, line, msg):
        self.warnings.append(f"warn  {self._where(path, line)}  {msg}")

    def note(self, path, msg):
        self.notes.append(f"note  {self._where(path, 0)}  {msg}")


class Doc:
    """A markdown artifact: its lines, and its `## ` sections outside code fences."""

    def __init__(self, path):
        self.path = path
        with open(path, encoding="utf-8") as f:
            self.lines = f.read().splitlines()
        self.sections = {}                 # title -> (heading line no, [(line no, text)])
        current, fence = None, False
        for n, text in enumerate(self.lines, 1):
            if text.lstrip().startswith("```"):
                fence = not fence
            if not fence and text.startswith("## "):
                current = text[3:].strip()
                self.sections[current] = (n, [])
            elif current is not None:
                self.sections[current][1].append((n, text))

    def _match(self, prefix):
        for title in self.sections:
            if title == prefix or title.startswith(prefix + " ") or title.startswith(prefix + "("):
                return title
        return None

    def section(self, prefix):
        """The body lines [(line no, text)] of the first section titled `prefix`, or None."""
        title = self._match(prefix)
        return self.sections[title][1] if title else None

    def heading(self, prefix):
        title = self._match(prefix)
        return self.sections[title][0] if title else 0

    def header(self):
        return {k: v for k, v in (self._field(i) for i in range(min(5, len(self.lines)))) if k}

    def _field(self, i):
        m = re.match(r"^(\w+):\s*(.*)$", self.lines[i])
        return (m.group(1), m.group(2).strip()) if m else (None, None)

    def status(self):
        return self.header().get("Status", "").split()[0] if self.header().get("Status") else ""


def git_has(repo, sha, cache={}):
    if sha not in cache:
        r = subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"],
                           capture_output=True)
        cache[sha] = r.returncode == 0
    return cache[sha]


def check_header(doc, rep):
    keys = [doc._field(i)[0] for i in range(min(5, len(doc.lines)))]
    if keys != HEADER:
        rep.error(doc.path, 1, f"provenance header must be the five lines {', '.join(h + ':' for h in HEADER)} "
                               f"in that order; found {keys}")
        return
    h = doc.header()
    status = h["Status"].split()[0] if h["Status"] else ""
    if status not in STATUSES:
        rep.error(doc.path, 5, f"Status `{h['Status']}` is not one of {', '.join(sorted(STATUSES))}")
    if (os.path.basename(doc.path) in ("brainstorm.md", "plan.md") and not rep.done
            and not re.search(r"\d{4}-\d{2}-\d{2}\s+·\s+\S", h["Created"])):
        rep.warn(doc.path, 2, "Created has no model: write `Created: <date> · <model>` so wrap can fill Seats")
    base = re.match(SHA, h["Base"])
    if not base:
        rep.error(doc.path, 3, f"Base `{h['Base']}` is not a git sha")
    elif not git_has(rep.repo, base.group(0)):
        rep.missing_sha(doc.path, 3, f"Base {base.group(0)} is not a commit in this repo")
    if h["Inputs"] != "none":
        refs = re.findall(r"(\S+)\s+@\s+(" + SHA + ")", h["Inputs"])
        if not refs:
            rep.error(doc.path, 4, "Inputs must be `none` or `<artifact> @ <sha>`")
        for _, sha in refs:
            if not git_has(rep.repo, sha):
                rep.missing_sha(doc.path, 4, f"Inputs sha {sha} is not a commit in this repo")


def check_budget(doc, rep, limit):
    if len(doc.lines) > limit:
        rep.warn(doc.path, 0, f"{len(doc.lines)} lines, budget ~{limit}: cut prose, never acceptance "
                              "lines or checks; still over means two runs")


def require_sections(doc, rep, names, strict):
    for name in names:
        if doc.section(name) is None:
            (rep.error if strict else rep.warn)(doc.path, 0, f"missing section `## {name}`")


# --- brainstorm.md -------------------------------------------------------------------------

def check_brief(run, rep):
    doc = run["docs"]["brainstorm.md"]
    status = doc.status()
    if status == "parked" and doc.section("Parked") is None:
        rep.error(doc.path, 0, "Status parked but no `## Parked` section saying what unparks it")
    body = doc.section("Behaviours") or []
    strict = status in ("complete", "done")
    require_sections(doc, rep, BRIEF_SECTIONS, strict)
    ids = set()
    for n, text in body:
        m = re.match(r"^- (B\d+)" + DASH + r"(.*)$", text)
        if not m:
            continue
        if m.group(1) in ids:
            rep.error(doc.path, n, f"{m.group(1)} is defined twice")
        ids.add(m.group(1))
        if "→" not in m.group(2) and "->" not in m.group(2):
            rep.warn(doc.path, n, f"{m.group(1)} has no `→ observable result`")
    if status != "drafting":
        if len(ids) > LEAN_BEHAVIOURS_MAX and not any(
                re.match(r"Split declined by human:\s*\S", x) for x in doc.lines):
            rep.error(doc.path, doc.heading("Behaviours"),
                      f"{len(ids)} behaviours; at most {LEAN_BEHAVIOURS_MAX}: propose the split into two runs "
                      "or record `Split declined by human: <when>`")
    if strict and not any(t.startswith("Docs read:") for t in doc.lines):
        rep.warn(doc.path, 0, "no `Docs read:` line")
    check_prototypes(run, doc, rep)
    return ids


def check_prototypes(run, doc, rep):
    notes_dir = os.path.join(run["dir"], "notes")
    notes = sorted(os.listdir(notes_dir)) if os.path.isdir(notes_dir) else []
    cited = set()
    for n, text in enumerate(doc.lines, 1):
        for p in re.findall(r"\(prototype:\s*(P\d+)\)", text):
            cited.add(p)
            note = [f for f in notes if f.startswith(p + "-") and f.endswith(".md")]
            if not note:
                rep.error(doc.path, n, f"decision cites {p} but notes/{p}-<topic>.md does not exist")
                continue
            with open(os.path.join(notes_dir, note[0]), encoding="utf-8") as f:
                first = f.readline().strip()
            if not re.match(re.escape(p) + DASH, first):
                rep.warn(os.path.join(notes_dir, note[0]), 1, f"note should open with `{p} — <the question it settles>`")
    proto_dir = os.path.join(run["dir"], "prototypes")
    if os.path.isdir(proto_dir):
        found = sorted(d for d in os.listdir(proto_dir) if re.match(r"P\d+-", d))
        if len(found) > MAX_PROTOTYPES:
            rep.warn(proto_dir, 0, f"{len(found)} prototypes; at most {MAX_PROTOTYPES} per brainstorm")
        for d in found:
            p = d.split("-")[0]
            if not any(f.startswith(p + "-") for f in notes):
                rep.warn(os.path.join(proto_dir, d), 0, f"prototype has no notes/{p}-<topic>.md")


# --- plan.md / patch_plan.md ---------------------------------------------------------------

def parse_tickets(doc):
    tickets, current, fence = [], None, False
    for n, text in enumerate(doc.lines, 1):
        if text.lstrip().startswith("```"):
            fence = not fence
        if fence:
            continue
        m = re.match(r"^### ((?:C\d+-)?T\d+)" + DASH + r"(.+)$", text)
        if m:
            current = {"id": m.group(1), "line": n, "lines": []}
            tickets.append(current)
        elif text.startswith("## "):
            current = None
        elif current is not None:
            current["lines"].append((n, text))
    return tickets


def field(ticket, name):
    for n, text in ticket["lines"]:
        m = re.search(r"(?:^|·\s*)" + re.escape(name) + r":\s*(.*?)(?=\s+·\s+\w[\w ]*:|$)", text)
        if m:
            return n, m.group(1).strip()
    return None, None


def check_tickets(run, doc, rep, behaviours, strict):
    tickets = parse_tickets(doc)
    if not tickets:
        (rep.error if strict else rep.warn)(doc.path, 0, "no tickets (`### T# — <title>`)")
        return []
    ids = [t["id"] for t in tickets]
    for dup in {i for i in ids if ids.count(i) > 1}:
        rep.error(doc.path, 0, f"{dup} is defined twice")
    if doc.path.endswith("/plan.md") and len(tickets) > MAX_TICKETS:
        rep.error(doc.path, 0, f"{len(tickets)} tickets; at most {MAX_TICKETS}: propose the split into two runs")
    edges = {}
    for t in tickets:
        where = lambda n: n or t["line"]
        _, lane = field(t, "Lane")
        n_del, delivers = field(t, "Delivers")
        n_blk, blocked = field(t, "Blocked by")
        if delivers is None or blocked is None or lane is None:
            rep.error(doc.path, t["line"], f"{t['id']}: needs `Delivers: … · Blocked by: … · Lane: …`")
        if lane is not None and lane.split()[0] not in LANES:
            rep.error(doc.path, where(n_del), f"{t['id']}: lane `{lane}` is not one of {', '.join(sorted(LANES))}")
        t["delivers"] = set(re.findall(r"B\d+", delivers or ""))
        for b in t["delivers"] - behaviours if behaviours else ():
            rep.error(doc.path, where(n_del), f"{t['id']}: delivers {b}, which the brief does not define")
        edges[t["id"]] = re.findall(r"(?:C\d+-)?T\d+", blocked or "")
        for b in edges[t["id"]]:
            if b not in ids:
                rep.error(doc.path, where(n_blk), f"{t['id']}: blocked by {b}, which does not exist")
        if field(t, "Seam")[1] is None:
            rep.error(doc.path, t["line"], f"{t['id']}: no `Seam:` line")
        accepts = [(n, x) for n, x in t["lines"] if re.match(r"^\s*- \[[ x]\] ", x)]
        if not ACCEPT_MIN <= len(accepts) <= ACCEPT_MAX:
            rep.error(doc.path, t["line"], f"{t['id']}: {len(accepts)} acceptance lines; a ticket has "
                                           f"{ACCEPT_MIN}-{ACCEPT_MAX} (more is two tickets)")
        for n, x in accepts:
            if re.search(r"\bor\b", re.sub(r"`[^`]*`", "", x)):
                rep.warn(doc.path, n, f"{t['id']}: acceptance line has `or`: one expected result per line")
            words = len(re.sub(r"^\s*- \[[ x]\] ", "", x).split())
            if words > ACCEPT_WORDS:
                rep.warn(doc.path, n, f"{t['id']}: acceptance line has {words} words: one outcome, about 25")
        if (doc.path.endswith("/plan.md") and lane and lane.split()[0] in ("logic", "contract")
                and not field(t, "Budget")[1]):
            rep.warn(doc.path, t["line"], f"{t['id']}: no Budget: line (`Budget: code +N · tests +N`)")
        if lane and lane.split()[0] == "operator":
            check_risk(run, t, doc, rep)
        n_ver, verify = field(t, "Verify")
        if verify is None:
            rep.error(doc.path, t["line"], f"{t['id']}: no `Verify:` line")
        else:
            if strict and "pre:" not in verify:
                rep.error(doc.path, n_ver, f"{t['id']}: Verify has no `(pre: …)`: run it and record the result")
            if lane and lane.startswith("operator") and "receipt:" not in verify:
                rep.error(doc.path, n_ver, f"{t['id']}: operator ticket must verify `receipt: receipts/<file> — <values>`")
        check_skills(t, doc, rep)
        n_st, st = field(t, "Status")
        if st is None:
            rep.error(doc.path, t["line"], f"{t['id']}: no `Status:` line")
        else:
            m = re.match(r"^(todo|awaiting-human|done @ (" + SHA + r"))\b", st)
            if not m:
                rep.error(doc.path, n_st, f"{t['id']}: Status `{st}` must be todo, awaiting-human or done @ <sha>")
            elif m.group(2):
                if not git_has(rep.repo, m.group(2)):
                    rep.missing_sha(doc.path, n_st, f"{t['id']}: done @ {m.group(2)} is not a commit in this repo")
                if field(t, "Writer")[1] is None:
                    rep.warn(doc.path, n_st, f"{t['id']}: done but no `Writer: <model>` line")
                if doc.path.endswith("/plan.md"):
                    check_overrun(t, lane, m.group(2), doc, rep, n_st)
                check_test_smells(t, m.group(2), doc, rep, n_st)
    if doc.path.endswith("/plan.md"):
        check_sizing(tickets, doc, rep)
    cycle = find_cycle(edges)
    if cycle:
        rep.error(doc.path, 0, "blocked-by cycle: " + " → ".join(cycle))
    return tickets


def check_sizing(tickets, doc, rep):
    for t in tickets:
        n, budget = field(t, "Budget")
        n_why, why = field(t, "why")
        m = re.search(r"code\s*\+(\d+)\s*·\s*tests\s*\+(\d+)", budget or "")
        if m and int(m.group(2)) > int(m.group(1)) and not (n_why == n and why):
            rep.warn(doc.path, n, f"{t['id']}: Budget tests +{m.group(2)} exceed code +{m.group(1)}: "
                                 "add `· why: <reason>` on the Budget line")
    budgets = [int(m.group(1)) for t in tickets
               if (field(t, "Lane")[1] or "x").split()[0] in ("logic", "contract")
               and (m := re.search(r"code\s*\+(\d+)", field(t, "Budget")[1] or ""))]
    if not budgets:
        return
    msg = f"median code Budget {statistics.median(budgets):g} over {len(budgets)} tickets"
    rep.note(doc.path, msg)
    if len(budgets) >= MERGE_MIN_TICKETS and statistics.median(budgets) < MERGE_BELOW:
        rep.warn(doc.path, 0, f"{msg}: merge tickets under ~{MERGE_BELOW} code lines into their neighbours")


def waiver(doc, kind, tid):
    for _, text in doc.section("Deviations") or []:
        m = re.match(r"^\s*(?:-\s+)?" + kind + r" waived:\s*" + re.escape(tid) + DASH + r"(\S.*)$", text)
        if m:
            return m.group(1)


def check_risk(run, t, doc, rep):
    """phase-2-plan's risk classes: every operator ticket has one, and a `cheap` one writes no script test."""
    n, risk = field(t, "Risk")
    if not risk:
        rep.warn(doc.path, t["line"], f"{t['id']}: operator ticket has no Risk: (`cheap`, `costly` or `irreversible`)")
    elif risk.split()[0].strip("`") == "cheap":
        for path in git_out(run["dir"], "ls-files", "scripts").splitlines():
            if re.search(TEST_FILE, path):
                rep.warn(doc.path, n, f"{t['id']}: cheap operator ticket adds {path}: "
                                      "reuse the repo's harness or CLI, no bespoke script test")


def check_overrun(t, lane, sha, doc, rep, n):
    """The `done @` commit alone, receipts excluded: net lines against the Budget, tests against code."""
    code, code_net, tests = growth(rep.repo, f"{sha}^", sha)
    net = code_net + tests
    parts = re.findall(r"\+(\d+)", field(t, "Budget")[1] or "")
    budget = sum(int(x) for x in parts)
    if parts and net > OVERRUN * budget:
        reason = waiver(doc, "Budget", t["id"])
        msg = f"{t['id']}: net +{net} lines, over {OVERRUN}× budget +{budget}"
        if reason:
            rep.note(doc.path, msg + f"; Budget waived: {t['id']} — {reason}")
        else:
            rep.warn(doc.path, n, msg + f": record `Budget waived: {t['id']} — <reason>` under `## Deviations`")
    if lane and lane.split()[0] in ("logic", "contract") and tests >= TEST_FLOOR and tests > TEST_RATIO * code:
        rep.warn(doc.path, n, f"{t['id']}: tests net +{tests} over {TEST_RATIO}× code +{code} "
                              f"(allowed {TEST_RATIO * code:g}): cut to one test per behaviour")


def growth(repo, a, b):
    """Code added, code net and tests net over a git range, receipts and binaries excluded."""
    code = code_net = tests = 0
    for row in git_out(repo, "diff", "--numstat", a, b).splitlines():
        added, deleted, path = row.split("\t", 2)
        if added == "-" or re.search(RECEIPTS, path):
            continue
        if re.search(TEST_FILE, path):
            tests += int(added) - int(deleted)
        else:
            code += int(added)
            code_net += int(added) - int(deleted)
    return code, code_net, tests


def check_run_ratio(doc, tickets, rep):
    shas = [re.match(r"done @ (" + SHA + r")\b", field(t, "Status")[1] or "") for t in tickets]
    base = re.match(SHA, doc.header().get("Base", ""))
    if not shas or not all(shas) or not base:
        return
    commits = [base.group(0)] + [m.group(1) for m in shas]
    if not all(git_has(rep.repo, sha) for sha in commits):
        return  # header and ticket checks report dangling pointers
    last = max(commits[1:], key=lambda sha: int(git_out(rep.repo, "rev-list", "--count", sha)))
    code, _, tests = growth(rep.repo, commits[0], last)
    if tests >= RUN_TEST_FLOOR and tests > TEST_RATIO * code:
        reason = waiver(doc, "Ratio", "run")
        msg = f"run: tests net +{tests} over {TEST_RATIO}× code added +{code} (allowed {TEST_RATIO * code:g})"
        if reason:
            rep.warn(doc.path, 0, msg + f"; Ratio waived: run — {reason}")
        else:
            rep.error(doc.path, 0, msg + ": cut tests or record `Ratio waived: run — <reason>` under `## Deviations`")


def check_test_smells(t, sha, doc, rep, n):
    """Lines the `done @` commit adds to test files that break a tests.md rule a script can see: one warning
    per file and rule."""
    rules = {TEST_IMPORT: "imports a test module: move the shared builder to conftest.py or a fixtures module",
             SQL_TEXT: "reads SQL source text: assert the schema contract or the output; "
                       "a deny-list guard is the one exception"}
    hits, path = {}, None
    for line in git_out(rep.repo, "diff", "-U0", f"{sha}^", sha).splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") and re.search(TEST_FILE, line[6:]) else None
        elif path and line.startswith("+"):
            rule = next((r for r in rules if re.search(r, line[1:])), None)
            if rule:
                hits[(path, rule)] = hits.get((path, rule), 0) + 1
    for (path, rule), count in hits.items():
        rep.warn(doc.path, n, f"{t['id']}: {path} {rules[rule]} ({count} added line{'s' if count > 1 else ''})")


def check_skills(t, doc, rep):
    n, skills = field(t, "Skills")
    if skills is None:
        rep.warn(doc.path, t["line"], f"{t['id']}: no `Skills:` line (write `Skills: none`)")
        return
    if skills.split()[0].lower() == "none":
        return
    for p in re.split(r"\s*[,·]\s*", skills):
        p = p.strip("` ")
        full = os.path.expanduser(p) if p.startswith("~") else os.path.join(rep.repo, p)
        if p and not os.path.exists(full):
            rep.warn(doc.path, n, f"{t['id']}: skill path `{p}` does not resolve here")


def find_cycle(edges):
    state, stack = {}, []

    def visit(node):
        state[node] = "open"
        stack.append(node)
        for nxt in edges.get(node, []):
            if state.get(nxt) == "open":
                return stack[stack.index(nxt):] + [nxt]
            if nxt in edges and nxt not in state:
                found = visit(nxt)
                if found:
                    return found
        state[node] = "done"
        stack.pop()
        return None

    for node in edges:
        if node not in state:
            found = visit(node)
            if found:
                return found
    return None


def check_plan(run, rep, behaviours):
    doc = run["docs"]["plan.md"]
    strict = doc.status() in ("complete", "done")
    require_sections(doc, rep, PLAN_SECTIONS, strict)
    tickets = check_tickets(run, doc, rep, behaviours, strict)
    check_run_ratio(doc, tickets, rep)
    accepts = sum(bool(re.match(r"^\s*- \[[ x]\] ", x)) for t in tickets for _, x in t["lines"])
    if strict and accepts > PLAN_ACCEPT_MAX and not any(
            re.match(r"Split declined by human:\s*\S", x) for x in doc.lines):
        rep.error(doc.path, doc.heading("Tickets"),
                  f"{accepts} acceptance lines; at most {PLAN_ACCEPT_MAX}: propose the split into two runs "
                  "or record `Split declined by human: <when>`")
    if behaviours and strict:
        delivered = set().union(*(t.get("delivers", set()) for t in tickets)) if tickets else set()
        for b in sorted(behaviours - delivered, key=lambda x: int(x[1:])):
            rep.error(doc.path, 0, f"{b} has no ticket: every behaviour is delivered by one")
    if doc.status() == "done" and doc.section("Execution state") is not None:
        rep.warn(doc.path, doc.heading("Execution state"), "done plan still has `## Execution state` (wrap 9a strips it)")


# --- review.md -----------------------------------------------------------------------------

def check_review(run, rep):
    doc = run["docs"]["review.md"]
    status = doc.status()
    if doc.section("Coverage") is None:
        (rep.error if status in ("complete", "done") else rep.warn)(doc.path, 0, "missing section `## Coverage`")
    elif not any("Independence:" in x for _, x in doc.section("Coverage")):
        rep.warn(doc.path, 0, "Coverage has no `Independence: cross-vendor | same-vendor (degraded)` line")
    cover = doc.section("Coverage")
    if status in ("complete", "done") and cover is not None and not any(
            x.startswith("Size:") for _, x in cover):
        rep.error(doc.path, 0, "Coverage has no Size: line (`Size: +<code> code · +<tests> tests · ratio · net · over 1,000`)")
    cycles = sorted(int(m.group(1)) for t in doc.sections if (m := re.match(r"Cycle (\d+) findings", t)))
    if status in ("complete", "done") and cycles and not doc.section(f"Cycle {cycles[-1]} verdict"):
        rep.error(doc.path, 0, f"Status {status} but no `## Cycle {cycles[-1]} verdict`")
    open_fix = []
    for c in cycles:
        if c >= 3 and not any(
                re.match(rf"Cycle {c} approved by human:\s*\S", x) for x in doc.lines):
            rep.error(doc.path, doc.heading(f"Cycle {c} findings"),
                      f"cycle {c} needs a `Cycle {c} approved by human: <when>` line: review stops after two")
        findings, current = [], None
        for n, text in doc.section(f"Cycle {c} findings"):
            m = re.match(r"^### (P[0-3])" + DASH + r"(.+)$", text)
            if m:
                current = {"sev": m.group(1), "title": m.group(2), "line": n, "lines": []}
                findings.append(current)
            elif current is not None:
                current["lines"].append((n, text))
        for f in findings:
            label = f"cycle {c} {f['sev']} `{f['title']}`"
            disp = next(((n, x) for n, x in f["lines"] if x.strip().startswith("- Disposition:")), None)
            if disp is None:
                rep.error(doc.path, f["line"], f"{label}: no `- Disposition:` line")
                continue
            n, value = disp[0], disp[1].split("Disposition:", 1)[1].strip()
            if value.startswith("fix now"):
                res = next((x for _, x in f["lines"] if x.strip().startswith("- Resolved:")), "")
                sha = re.search(r"@\s*(" + SHA + ")", res)
                if not sha:
                    open_fix.append(label)
                elif not git_has(rep.repo, sha.group(1)):
                    rep.missing_sha(doc.path, n, f"{label}: Resolved @ {sha.group(1)} is not a commit in this repo")
            elif value.startswith("defer"):
                if f["sev"] in ("P0", "P1") and not re.search(r"Approved by human:\s*\S", value):
                    rep.error(doc.path, n, f"{label}: a {f['sev']} defer needs `Approved by human: <when>`")
            elif value.startswith("wontfix"):
                if not re.match(r"wontfix" + DASH + r"\S", value):
                    rep.error(doc.path, n, f"{label}: wontfix needs a reason (`wontfix — <reason>`)")
            else:
                rep.error(doc.path, n, f"{label}: disposition `{value}` must start with fix now, defer or wontfix")
    resolved = doc.section("Resolved")
    for n, text in resolved or []:
        sha = re.search(r"@\s*(" + SHA + ")", text)
        if sha and not git_has(rep.repo, sha.group(1)):
            rep.missing_sha(doc.path, n, f"Resolved table: @ {sha.group(1)} is not a commit in this repo")
    if open_fix:
        rep.note(doc.path, f"{len(open_fix)} open `fix now` finding(s): {'; '.join(open_fix)}")
    elif cycles:
        rep.note(doc.path, "no open `fix now` finding")


# --- wrap.md and the folder ----------------------------------------------------------------

def check_wrap(run, rep):
    doc = run["docs"]["wrap.md"]
    if doc.status() == "done":
        if doc.section("Steps") is not None:
            rep.error(doc.path, doc.heading("Steps"), "done wrap still has `## Steps`: 9a rewrites it into the summary")
        if not any(t.startswith("Retired:") for t in doc.lines):
            rep.error(doc.path, 0, "wrap.md has no Retired: line: step 5b records what was deleted, or `none` with a reason")
        if len(doc.lines) > WRAP_DONE_BUDGET:
            rep.warn(doc.path, 0, f"{len(doc.lines)} lines; a finished run's summary is ~{WRAP_DONE_BUDGET}")
        check_worklog(run, rep)
    else:
        if doc.section("Steps") is None:
            rep.warn(doc.path, 0, "wrap in progress but no `## Steps` checklist")
        note_net_growth(run, rep)


def note_net_growth(run, rep):
    """Net product lines from plan.md's Base to HEAD, receipts excluded, for wrap's `Run:` line."""
    base = re.match(SHA, run["docs"]["plan.md"].header().get("Base", "")) if "plan.md" in run["docs"] else None
    if not base or not git_has(rep.repo, base.group(0)):
        return
    _, code, tests = growth(rep.repo, base.group(0), "HEAD")
    rep.note(run["docs"]["wrap.md"].path, f"run net since plan Base: code {code:+d} · tests {tests:+d} "
                                          "(copy onto the WORKLOG.md `Run:` line)")


def check_worklog(run, rep):
    """A done wrap's WORKLOG.md entry carries Seats: and Skills:, and names a reviewer review.md names."""
    slug = os.path.basename(os.path.normpath(run["dir"]))
    path = os.path.join(rep.repo, "WORKLOG.md")
    lines = open(path, encoding="utf-8").read().splitlines() if os.path.isfile(path) else []
    start = next((i for i, t in enumerate(lines) if t.startswith("## ") and f" · {slug} · " in t), None)
    if start is None:
        rep.error(path, 0, f"WORKLOG.md has no entry for {slug}: wrap step 8 appends `## <date> · {slug} · ...`")
        return
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    entry = [t.lstrip("- ").strip() for t in lines[start:end]]
    for field in ("Seats:", "Skills:"):
        if not any(t.startswith(field) for t in entry):
            rep.error(path, start + 1, f"entry for {slug} has no {field} line: take the writer from plan.md "
                                       "`Writer:` lines and the reviewer from review.md `Independence:`")
    review = run["docs"].get("review.md")
    named = review and any(re.search(r"\breviewer\s+[A-Z]", t) for t in review.lines if t.startswith("Independence:"))
    if named and "unrecorded" in lines[start]:
        rep.error(path, start + 1, f"entry for {slug} says unrecorded, but review.md names the reviewer "
                                   "on its `Independence:` line")


def check_layout(run, rep):
    for name in sorted(os.listdir(run["dir"])):
        path = os.path.join(run["dir"], name)
        if os.path.isdir(path):
            if name not in SUBFOLDERS:
                rep.warn(path, 0, f"subfolder `{name}/` is not one of {', '.join(SUBFOLDERS)}: wrap 9b moves receipts into them")
        elif name not in ARTIFACTS:
            rep.warn(path, 0, "only the artifacts belong at the top level: move it into its subfolder (wrap 9b)")
    big = sorted(((os.path.getsize(os.path.join(r, f)), os.path.join(r, f))
                  for r, _, fs in os.walk(run["dir"]) for f in fs
                  if os.path.getsize(os.path.join(r, f)) > BIG_FILE), reverse=True)
    if big:
        rep.warn(run["dir"], 0, f"{len(big)} file(s) over ~{BIG_FILE // 1000} KB, largest "
                                f"{os.path.relpath(big[0][1], run['dir'])} at {big[0][0] // 1000} KB: "
                                "the human decides whether they stay in git (wrap 9b)")


def check_pins(repo, rep):
    """Code outside the run folders never reads inside them; a test that does pins a run's files."""
    for f in git_out(repo, "ls-files").splitlines():
        if (re.search(TEST_FILE, f) and not re.match(r"[.]workflow/", f) and not re.search(RECEIPTS, f)
                and os.path.isfile(os.path.join(repo, f))):
            with open(os.path.join(repo, f), encoding="utf-8", errors="replace") as fh:
                if re.search(r"[.]workflow/", fh.read()):
                    rep.warn(os.path.join(repo, f), 0, "reads a path inside .workflow: code outside the run folders never does")


def is_legacy(run, status):
    """A v2.02 run: its plan has checklist steps, or it finished before briefs had behaviours."""
    plan = run["docs"].get("plan.md")
    if plan and plan.section("Tickets") is None and (plan.section("Checklist") or plan.section("Steps")) is not None:
        return True
    brief = run["docs"].get("brainstorm.md")
    return bool(brief) and status == "done" and brief.section("Behaviours") is None


def git_out(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def primary_branch(repo):
    primary = git_out(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").split("/", 1)[-1]
    return primary or next((b for b in ("main", "master")
                            if git_out(repo, "rev-parse", "--verify", "-q", b)), "")


def checkout_warnings(repo):
    """The next phase opens the primary checkout on the primary branch; a run committed elsewhere is invisible there."""
    out = []
    git_dir = os.path.realpath(os.path.join(repo, git_out(repo, "rev-parse", "--git-dir")))
    common = os.path.realpath(os.path.join(repo, git_out(repo, "rev-parse", "--git-common-dir")))
    branch = git_out(repo, "branch", "--show-current")
    slug = os.path.basename(os.path.realpath(repo))
    own_run = (git_dir != common and branch == f"run/{slug}" and
               os.path.realpath(repo) == os.path.join(os.path.dirname(common), ".worktrees", slug))
    if git_dir != common and not own_run:
        out.append(f"this is a linked worktree; the primary checkout is {os.path.dirname(common)}: "
                   "fast-forward its branch to this one and push before the closing card")
    primary = primary_branch(repo)
    if branch and primary and branch != primary and not own_run:
        out.append(f"on branch `{branch}`, not `{primary}`: the next phase will not see this run's commits "
                   f"until `{primary}` includes them")
    return out


def check_run(run_dir, rep):
    run = {"dir": run_dir, "docs": {}}
    for a in ARTIFACTS:
        p = os.path.join(run_dir, a)
        if os.path.isfile(p):
            run["docs"][a] = Doc(p)
    if "brainstorm.md" not in run["docs"]:
        rep.error(run_dir, 0, "no brainstorm.md: it holds the run's status of record")
    brief = run["docs"].get("brainstorm.md")
    rep.done = bool(brief and brief.status() == "done"
                    and git_out(rep.repo, "ls-files", "--", brief.path)
                    and not git_out(rep.repo, "status", "--porcelain", "--", brief.path))
    for name, doc in run["docs"].items():
        if name != "learnings.md":
            check_header(doc, rep)
        if not rep.done and name in BUDGET:
            check_budget(doc, rep, BUDGET[name])
    run_status = run["docs"]["brainstorm.md"].status() if "brainstorm.md" in run["docs"] else ""
    if rep.done:
        rep.note(run_dir, "done run: only header, sha and layout checks apply")
        for name in ("plan.md", "patch_plan.md", "review.md"):
            doc = run["docs"].get(name)
            if doc is None:
                continue
            if name == "review.md":
                for n, text in enumerate(doc.lines[5:], 6):
                    for sha in re.findall(r"@\s*(" + SHA + ")", text):
                        if not git_has(rep.repo, sha):
                            rep.missing_sha(doc.path, n, f"Resolved @ {sha} is not a commit in this repo")
            else:
                for t in parse_tickets(doc):
                    n, status = field(t, "Status")
                    sha = re.match(r"done @ (" + SHA + r")\b", status or "")
                    if sha and not git_has(rep.repo, sha.group(1)):
                        rep.missing_sha(doc.path, n, f"{t['id']}: done @ {sha.group(1)} is not a commit in this repo")
    elif is_legacy(run, run_status):
        rep.note(run_dir, "v2.02 run shape (checklist plan, no behaviours): only header, budget and "
                          "layout checks apply")
    else:
        behaviours = check_brief(run, rep) if "brainstorm.md" in run["docs"] else set()
        if "plan.md" in run["docs"]:
            check_plan(run, rep, behaviours)
        if "patch_plan.md" in run["docs"]:
            pp = run["docs"]["patch_plan.md"]
            check_tickets(run, pp, rep, set(), pp.status() in ("complete", "done"))
        if "review.md" in run["docs"]:
            check_review(run, rep)
        if "wrap.md" in run["docs"]:
            check_wrap(run, rep)
    if not rep.done and run_status == "done" and "patch_plan.md" in run["docs"]:
        rep.warn(run["docs"]["patch_plan.md"].path, 0, "run is done but patch_plan.md remains (wrap 9a deletes it)")
    check_layout(run, rep)
    return run_status


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs", nargs="*", help="run slug or run folder; default: every live run")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--all", action="store_true", help="include parked and done runs")
    args = ap.parse_args()
    top = subprocess.run(["git", "-C", args.repo, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0:
        print(f"{args.repo} is not inside a git repo: run from the repo root or pass --repo", file=sys.stderr)
        return 2
    repo = top.stdout.strip()
    wf = os.path.join(repo, ".workflow")
    if args.runs:
        dirs = []
        for r in args.runs:
            d = r if os.path.isdir(r) else os.path.join(wf, r)
            if not os.path.isdir(d):
                have = sorted(x for x in os.listdir(wf) if os.path.isdir(os.path.join(wf, x))) if os.path.isdir(wf) else []
                print(f"no run `{r}`; runs here: {', '.join(have) or 'none'}", file=sys.stderr)
                return 2
            dirs.append(os.path.abspath(d))
    else:
        if not os.path.isdir(wf):
            print(f"no .workflow folder in {repo}", file=sys.stderr)
            return 2
        dirs = [os.path.join(wf, x) for x in sorted(os.listdir(wf))
                if os.path.isdir(os.path.join(wf, x)) and x != "archive"]
    failed = False
    checked = 0
    checkout = checkout_warnings(repo)
    for d in dirs:
        rep = Report(repo)
        for msg in checkout:
            rep.warn(repo, 0, msg)
        status = check_run(d, rep)
        if not args.runs and not args.all and status in ("parked", "done"):
            continue
        checked += 1
        for line in rep.errors + rep.warnings + rep.notes:
            print(line)
        print(f"== {os.path.basename(d)} · {status or 'no status'} · {len(rep.errors)} errors · {len(rep.warnings)} warnings\n")
        failed = failed or bool(rep.errors)
    if args.all:
        rep = Report(repo)
        check_pins(repo, rep)
        for line in rep.warnings:
            print(line)
        print(f"== repo · {len(rep.warnings)} warnings\n")
    if not checked:
        print("no live runs (use --all to include parked and done runs)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
