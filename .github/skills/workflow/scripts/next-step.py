#!/usr/bin/env python3
"""Print a workflow run's next step as a card or schema-versioned JSON. Needs Python 3 and git."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

spec = importlib.util.spec_from_file_location("check_run", Path(__file__).with_name("check-run.py"))
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

EFFORTS = {"medium", "high", "xhigh"}


def table(doc, heading, columns):
    rows = {}
    header = False
    for number, line in doc.section(heading) or []:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r"[-:]+", cell) for cell in cells):
            continue
        label = f"{doc.path}:{number}: {cells[0]}"
        if not header:
            if cells != columns:
                raise ValueError(f"{label}: expected columns {' | '.join(columns)}")
            header = True
            continue
        if len(cells) != len(columns) or any(not cell for cell in cells[:-1]):
            raise ValueError(f"{label}: expected {len(columns)} cells, with only Notes allowed empty")
        if cells[0] in rows:
            raise ValueError(f"{label}: duplicate row")
        rows[cells[0]] = dict(zip(columns, cells))
    if not header:
        raise ValueError(f"{doc.path}: missing {heading} table")
    return rows


def model(text, effort, key):
    parts = [part.strip() for part in text.split("·")]
    if len(parts) not in (2, 3) or not all(parts) or (len(parts) == 3 and parts[2] not in EFFORTS):
        raise ValueError(f"{key}: expected Vendor · Model with optional · medium/high/xhigh: {text}")
    return {"vendor": parts[0], "name": parts[1], "effort": parts[2] if len(parts) == 3 else effort}


def routing(path):
    doc = checks.Doc(str(path))
    seats = table(doc, "Seat mapping", ["Seat", "Vendor", "Model", "Trial", "Fallback chain", "Notes"])
    phases = table(doc, "Phase", ["Key", "Phase / work", "Seat", "Effort", "Context", "Approval", "Notes"])
    # Parse every seat, including unused rows, so a broken configuration never produces a card.
    parsed = {}
    for key, row in seats.items():
        primary = model(f"{row['Vendor']} · {row['Model']}", None, key)
        trial = None if row["Trial"] == "—" else model(row["Trial"], None, key)
        fallbacks = [model(item, None, key) for item in row["Fallback chain"].split(";")]
        parsed[key] = primary, trial, fallbacks
    routes = {}
    for key, row in phases.items():
        if row["Effort"] not in EFFORTS or row["Context"] not in ("standard", "large") or row["Approval"] not in ("auto", "human"):
            raise ValueError(f"{path}: {key}: invalid Effort, Context or Approval")
        if row["Seat"] not in parsed:
            raise ValueError(f"{path}: {key}: unknown seat {row['Seat']}")
        primary, trial, fallbacks = parsed[row["Seat"]]
        with_effort = lambda item: {**item, "effort": item["effort"] or row["Effort"]}
        routes[key] = {"key": key, "seat": row["Seat"], "model": with_effort(trial or primary),
                       "trial": trial is not None, "context": row["Context"], "approval": row["Approval"],
                       "fallback": [with_effort(item) for item in ([primary] if trial else []) + fallbacks]}
    return routes


def model_lines(step):
    current = step["model"]
    fallback = step["fallback"][0] if step["fallback"] else None
    model_line = (f"{current['name']} · {current['effort']} · {step['context']}" if current else
                  f"human · {step['blocker']['action']}")
    fallback_line = f"{fallback['name']} · {fallback['effort']}" if fallback else "none"
    if step["trial"]:
        model_line += " (trial)"
    return f"- **Model:** {model_line}\n- **Fallback:** {fallback_line}\n"


def card(step, prefix):
    if step["phase"] == "done":
        return f"---\n**✅ Done** · {step['slug']}\n---\n"
    return (f"---\n**▶ Next: {step['phase']}** · {step['slug']}\n\n"
            f"- **Why:** {step['why']}\n- **Reset:** {'yes' if step['reset'] else 'no'}\n"
            f"{model_lines(step)}"
            f"- **Reads:** {', '.join(step['reads'])}\n\n**Run:**\n\n"
            f"```text\n{prefix}{step['command']}\n```\n---\n")


def ticket_step(repo, slug, doc, patch=False):
    run = repo / ".workflow" / slug
    blocker, reads = None, []
    tickets = checks.parse_tickets(doc)
    statuses = {t["id"]: checks.field(t, "Status")[1] or "" for t in tickets}
    unfinished = [t for t in tickets if not statuses[t["id"]].startswith("done @ ")]
    selected = None
    for t in unfinished:
        dependencies = re.findall(r"(?:C\d+-)?T\d+", checks.field(t, "Blocked by")[1] or "")
        if not all(statuses.get(dep, "").startswith("done @ ") for dep in dependencies):
            continue
        status = statuses[t["id"]]
        receipt = re.search(r"receipt:\s*(receipts/[^\s`]+)", checks.field(t, "Verify")[1] or "")
        if status == "todo" or (status == "awaiting-human" and receipt and (run / receipt[1]).is_file()):
            selected = t
            break
    if selected is None:
        selected = next((t for t in unfinished if statuses[t["id"]] == "awaiting-human"), None)
        if selected is None:
            raise ValueError(f"{slug}: no ready ticket in {Path(doc.path).name}")
        handoffs = sorted((run / "receipts").glob(f"{selected['id'].lower()}-*handoff*.md"))
        title = re.split(checks.DASH, doc.lines[selected["line"] - 1], maxsplit=1)[1]
        action = "; ".join([title] + [str(path.relative_to(run)) for path in handoffs])
        blocker = {"ticket": selected["id"], "action": action}
        reads = [str(path.relative_to(repo)) for path in handoffs]
    phase, ticket_id = "execute", selected["id"]
    lane = checks.field(selected, "Lane")[1] or ""
    key = f"execute:{lane.split()[0]}" if lane else "execute:"
    why = f"{ticket_id} is awaiting human action." if blocker else f"{ticket_id} is ready."
    reads = [str(Path(doc.path).relative_to(repo))] + (reads if blocker else [])
    if patch:
        fixes = checks.ticket_fixes(selected)
        if not fixes:
            raise ValueError(f"{ticket_id}: needs Fixes: C<n>-<m> (P#)")
        key = "fix:P0" if fixes[2] == "P0" else f"fix:{lane.split()[0]}"
        cycle = re.match(r"C(\d+)-", ticket_id)
        why = f"Patch cycle {cycle[1] if cycle else fixes[1].split('-')[0][1:]} · fix {fixes[1]}"
    return {"phase": phase, "key": key, "ticket": ticket_id, "why": why, "reads": reads, "blocker": blocker}


def next_step(repo, slug, routes, prefix=""):
    run = repo / ".workflow" / slug
    brief = checks.Doc(str(run / "brainstorm.md"))
    step = {"schema_version": 1, "slug": slug, "phase": "plan", "key": "plan", "ticket": None,
            "why": "The brief is complete; the run needs a plan.", "reads": [f".workflow/{slug}/brainstorm.md"],
            "reset": True, "blocker": None}
    docs = {name: checks.Doc(str(run / name)) for name in ("plan.md", "patch_plan.md", "review.md")
            if (run / name).exists()} if brief.status() == "complete" else {}
    plan, patch, review = (docs.get(name) for name in ("plan.md", "patch_plan.md", "review.md"))
    unfinished = lambda doc: any(not (checks.field(t, "Status")[1] or "").startswith("done @ ")
                                 for t in checks.parse_tickets(doc))
    if brief.status() == "drafting":
        step.update(phase="brainstorm", key="brainstorm", why="The brief is unfinished.")
    elif brief.status() == "parked":
        step.update(phase="parked", why="The run is parked.")
    elif brief.status() == "done":
        step.update(phase="done", key=None, why="The run is done.")
    elif brief.status() != "complete":
        raise ValueError(f"{slug}: unknown brief status {brief.status()}")
    elif plan and plan.status() == "drafting":
        step.update(why="The plan is unfinished.", reads=[f".workflow/{slug}/plan.md"])
    elif patch and patch.status() == "drafting":
        step.update(phase="review", key="patch-plan", why="The patch plan is unfinished.",
                    reads=[f".workflow/{slug}/patch_plan.md"])
    elif patch and unfinished(patch):
        step.update(ticket_step(repo, slug, patch, patch=True))
    elif plan and unfinished(plan):
        step.update(ticket_step(repo, slug, plan))
    elif plan:
        step.update(phase="review", key="review", why="All tickets are done; review the changes.",
                    reads=[f".workflow/{slug}/plan.md"])
        if review:
            step["reads"].append(f".workflow/{slug}/review.md")
            findings = checks.review_findings(review)
            cycle = max(findings, default=0)
            open_ids = [f["id"] for group in findings.values() for f in group if checks.open_finding(f)]
            base = review.header().get("Base", "")
            if not checks.git_has(str(repo), base):
                raise ValueError(f"review.md: unknown Base {base}")
            changed = any(not re.search(checks.RECEIPTS, path) for path in
                          checks.git_out(str(repo), "diff", "--name-only", f"{base}..HEAD").splitlines())
            current_patch = patch and any(t["id"].startswith(f"C{cycle}-") for t in checks.parse_tickets(patch))
            if review.status() == "drafting":
                step["why"] = "The review is unfinished."
            elif open_ids:
                step["why"] = f"Patch cycle {cycle} · fix {', '.join(open_ids)}"
                if not current_patch:
                    step["blocker"] = {"findings": open_ids, "action": f"Resolve {', '.join(open_ids)} before continuing."}
            elif not changed:
                step.update(phase="wrap", key="wrap", reset=False, why="The review has no open finding or later code change.")
    key = step["key"]
    if key is not None and key not in routes:
        raise ValueError(f"ROUTING.md: missing key {key}")
    if key is not None:
        step.update(routes[key])
    else:
        step.update(seat=None, model=None, trial=False, context=None, fallback=[], approval="auto")
    step["command"] = None if step["phase"] == "done" else f"workflow {'plan' if step['phase'] == 'parked' else step['phase']} {slug}"
    if step["blocker"]:
        step.update(model=None, fallback=[], trial=False)
    step["card"] = card(step, prefix)
    return step


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--key", help="print Model and Fallback lines for a routing key, without a run")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--routing", type=Path, default=Path(__file__).resolve().parents[1] / "ROUTING.md")
    parser.add_argument("--prefix", default="")
    args = parser.parse_args()
    try:
        routes = routing(args.routing)
        if args.key is not None:
            if args.key not in routes:
                raise ValueError(f"ROUTING.md: missing key {args.key}")
            print(model_lines(routes[args.key]), end="")
            return 0
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.slug or ""):
            raise ValueError("slug must contain only letters, digits, dots, underscores and hyphens")
        root = checks.git_out(str(args.repo), "rev-parse", "--show-toplevel")
        if not root:
            raise ValueError(f"{args.repo}: not inside a git repo")
        result = next_step(Path(root), args.slug, routes, args.prefix)
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False) if args.json else result["card"], end="\n" if args.json else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
