#!/usr/bin/env python3
"""Check a workflow run folder against the shapes the workflow skill defines.

Checks what a script can count, so no phase has to eyeball it:
- every artifact opens with the five-line provenance header, `Status:` holds a known value,
  and every sha in `Base:` / `Inputs:` / `done @` / `Resolved: @` exists in git;
- budgets: brainstorm ~80 lines and 5-15 behaviours, plan ~120 lines and 8 tickets,
  review ~100 lines, a done wrap ~40 lines;
- the brief: required sections, `B# — situation → result` behaviours, prototype notes;
- tickets in plan.md / patch_plan.md: Delivers · Blocked by · Lane, Seam, 1-4 acceptance lines,
  Verify with `pre:`, Skills paths, Status; every behaviour delivered by a ticket; no
  blocked-by cycle; operator tickets verify a receipt;
- slop guards, on artifacts created from SLOP_SINCE: a `Budget:` on logic and contract plan
  tickets, acceptance lines of at most ACCEPT_WORDS words; a done ticket's commit within
  OVERRUN× its budget and tests within TEST_RATIO× code, unless `## Deviations` names it;
  a `Risk:` on operator tickets, and no script test in the run's `scripts/` for a `cheap` one;
  a `Size:` line in a complete review's Coverage; a `Retired:` line in a done wrap;
- review.md: findings with a disposition, P0/P1 deferrals approved, a verdict once complete;
- the folder: only the artifacts at the top level, everything else in a known subfolder;
- `--all` only: a tracked test file outside the run folders that names a path inside one.

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
BEHAVIOURS_MIN, BEHAVIOURS_MAX = 5, 15     # phase-0-brainstorm §4: more means two runs
MAX_TICKETS = 8                            # phase-2-plan §5
ACCEPT_MIN, ACCEPT_MAX = 1, 4              # phase-2-plan §3 *Small*
MAX_PROTOTYPES = 3                         # phase-0-brainstorm §3a
BIG_FILE = 100_000                         # wrap 9b flags files over ~100 KB
# Slop guards fire only on artifacts whose first `Created:` date is on or after SLOP_SINCE.
SLOP_SINCE = "2026-10-09"
ACCEPT_WORDS = 40                          # phase-2-plan asks ~25; warn above this
OVERRUN = 2                                # a ticket commit's net lines over 2× its Budget warns
TEST_RATIO, TEST_FLOOR = 3, 50             # tests added over 3× code added, and ≥ 50, is an ERROR
RECEIPTS = r"\.(md|txt)$|^[.]workflow/[^/]+/(screens|prototypes|understand)/"
TEST_FILE = r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]*$|_test\.[^/]*$|\.(test|spec)\.[^/]*$"
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

    def slop_gated(self):
        m = re.search(r"\d{4}-\d{2}-\d{2}", self.header().get("Created", ""))
        return bool(m) and m.group(0) >= SLOP_SINCE


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
    if strict and not BEHAVIOURS_MIN <= len(ids) <= BEHAVIOURS_MAX:
        rep.warn(doc.path, doc.heading("Behaviours"),
                 f"{len(ids)} behaviours; the brief wants {BEHAVIOURS_MIN}-{BEHAVIOURS_MAX} (more means two runs)")
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
    edges, gated = {}, doc.slop_gated()
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
            if gated and words > ACCEPT_WORDS:
                rep.warn(doc.path, n, f"{t['id']}: acceptance line has {words} words: one outcome, about 25")
        if (gated and doc.path.endswith("/plan.md") and lane and lane.split()[0] in ("logic", "contract")
                and field(t, "Budget")[1] is None):
            rep.warn(doc.path, t["line"], f"{t['id']}: no Budget: line (`Budget: code +N · tests +N`)")
        if gated and lane and lane.split()[0] == "operator":
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
                if gated and doc.path.endswith("/plan.md") and not deviated(doc, t["id"]):
                    check_overrun(t, lane, m.group(2), doc, rep, n_st)
    cycle = find_cycle(edges)
    if cycle:
        rep.error(doc.path, 0, "blocked-by cycle: " + " → ".join(cycle))
    return tickets


def deviated(doc, tid):
    return any(re.search(r"\b" + tid + r"\b", x) for _, x in doc.section("Deviations") or [])


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
    code = tests = net = 0
    for row in git_out(rep.repo, "diff", "--numstat", f"{sha}^", sha).splitlines():
        added, deleted, path = row.split("\t", 2)
        if added == "-" or re.search(RECEIPTS, path):
            continue
        net += int(added) - int(deleted)
        if re.search(TEST_FILE, path):
            tests += int(added)
        else:
            code += int(added)
    budget = sum(int(x) for x in re.findall(r"\+(\d+)", field(t, "Budget")[1] or ""))
    if budget and net > OVERRUN * budget:
        rep.warn(doc.path, n, f"{t['id']}: net +{net} lines, over {OVERRUN}× budget +{budget}: "
                              "log the reason under `## Deviations`")
    if lane and lane.split()[0] == "logic" and tests >= TEST_FLOOR and tests > TEST_RATIO * code:
        rep.error(doc.path, n, f"{t['id']}: tests +{tests} over {TEST_RATIO}× code +{code}: "
                               "cut to one test per behaviour, or log the reason under `## Deviations`")


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
    if doc.slop_gated() and status in ("complete", "done") and cover is not None and not any(
            x.startswith("Size:") for _, x in cover):
        rep.error(doc.path, 0, "Coverage has no Size: line (`Size: +<code> code · +<tests> tests · ratio · net · over 1,000`)")
    cycles = sorted(int(m.group(1)) for t in doc.sections if (m := re.match(r"Cycle (\d+) findings", t)))
    if status in ("complete", "done") and cycles and not doc.section(f"Cycle {cycles[-1]} verdict"):
        rep.error(doc.path, 0, f"Status {status} but no `## Cycle {cycles[-1]} verdict`")
    open_fix = []
    for c in cycles:
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
        if doc.slop_gated() and not any(t.startswith("Retired:") for t in doc.lines):
            rep.error(doc.path, 0, "wrap.md has no Retired: line: step 5b records what was deleted, or `none` with a reason")
        if len(doc.lines) > WRAP_DONE_BUDGET:
            rep.warn(doc.path, 0, f"{len(doc.lines)} lines; a finished run's summary is ~{WRAP_DONE_BUDGET}")
    elif doc.section("Steps") is None:
        rep.warn(doc.path, 0, "wrap in progress but no `## Steps` checklist")


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


def checkout_warnings(repo):
    """The next phase opens the primary checkout on the primary branch; a run committed elsewhere is invisible there."""
    out = []
    git_dir = os.path.realpath(os.path.join(repo, git_out(repo, "rev-parse", "--git-dir")))
    common = os.path.realpath(os.path.join(repo, git_out(repo, "rev-parse", "--git-common-dir")))
    if git_dir != common:
        out.append(f"this is a linked worktree; the primary checkout is {os.path.dirname(common)}: "
                   "fast-forward its branch to this one and push before the closing card")
    branch = git_out(repo, "branch", "--show-current")
    primary = git_out(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").split("/", 1)[-1]
    if not primary:
        primary = next((b for b in ("main", "master") if git_out(repo, "rev-parse", "--verify", "-q", b)), "")
    if branch and primary and branch != primary:
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
    rep.done = run["docs"]["brainstorm.md"].status() == "done" if "brainstorm.md" in run["docs"] else False
    for name, doc in run["docs"].items():
        if name != "learnings.md":
            check_header(doc, rep)
        if name in BUDGET:
            check_budget(doc, rep, BUDGET[name])
    run_status = run["docs"]["brainstorm.md"].status() if "brainstorm.md" in run["docs"] else ""
    if is_legacy(run, run_status):
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
    if run_status == "done" and "patch_plan.md" in run["docs"]:
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
