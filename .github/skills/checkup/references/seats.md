### 6. Seat & skill performance, reviewer exam set

Models earn seats on **trial runs**, not exams: every `workflow wrap` appends a `WORKLOG.md`
entry with a `Run:` line (tickets · sessions · review cycles · deviations · findings overturned · net code and tests) and a
`Seats:` line (model per phase). Checkup turns those into a per-seat comparison and
*detects the need* to promote, demote, or run the one exam. It never edits `ROUTING.md`.

```sh
grep -nE '^\s*- (Run|Seats):' WORKLOG.md 2>/dev/null | tail -30        # recent run evidence
E="$HOME/.agents/j-skills-evals/strict-reviewer"
ls "$E"/*.md 2>/dev/null | grep -v RESULTS.md | wc -l                 # exam cases (cap 10)
grep -L '^## Must name' "$E"/*-*.md 2>/dev/null                        # cases missing their findings
grep -l '\.workflow/' "$E"/*-*.md 2>/dev/null                          # cases pointing at run scratch
tail -20 "$E"/RESULTS.md 2>/dev/null                                   # last exam results
ls -d evals/strict-reviewer 2>/dev/null                                # old per-repo set, to move
```

- **Per-seat table.** From the last ~10 entries, group by seat → model and average cycles,
  deviations, and (for the reviewer) overturned findings. Read the incumbent per seat from the
  `workflow` skill's `ROUTING.md`. Print the table; it *is* the evaluation.
- **Pending skill proposals.** `find . ~/.agents -name 'SKILL.md.proposed' 2>/dev/null` and any
  `SKILL-IMPACT.md` row with outcome `proposed`: ⚠️ "awaiting your accept/reject — `mv` to accept,
  delete and mark `rejected` to decline". Never accept or reject on the human's behalf.
- **Skill trials.** Entries also carry `Skills: <skill>@<sha>`. For each `trialing` line in the
  skills repo's `SKILL-IMPACT.md`, compare `Run:` numbers for entries at the new sha against the
  entries before it. The sha is the skill folder's tree hash: map it to a commit by matching
  `git rev-parse <commit>:<skill folder>` over that folder's history; an entry whose sha matches
  no commit is ⚠️ "unresolvable sha" and is left out of the comparison: once the trial count is reached, ⚠️ "trial complete -- better / worse / no
  signal, N runs"; worse means recommend reverting. Never edit the skill. Compare only like with
  like: v2.02 entries count checklist steps (≤12), v2.1 entries count tickets (≤8), so across that
  boundary compare review cycles and deviations only.
- **Trial in progress.** A model on a seat with only one run: ✅ note "trial, 1 run -- needs one
  more before judging".
- **Promotion candidate.** A non-incumbent with ≥2 runs that ties or beats the incumbent on
  cycles and deviations: ⚠️ recommend the human promote it in `ROUTING.md` (quote the row).
- **Regression.** The incumbent's last 2–3 runs clearly worse than its earlier average, or a
  candidate worse than the incumbent: ⚠️ say so with the numbers; the decision is the human's.
- **Code growth.** Report the summed `net code` of the last ~10 entries that carry it, and the
  directory that grew most (`git diff --dirstat=lines <oldest entry's first commit>^ HEAD -- .
  ':(exclude).workflow'`). When none of those runs shrank the code: ⚠️ ten runs with no pay-down,
  recommend `workflow improve <that directory> - goal: simpler, same behaviour`.
- **Test growth.** Over the same range as Code growth, report net tests and net code plus the current tracked-text tests ÷ code ratio. When net tests exceed net code, ⚠️ recommend `workflow improve tests - goal: fewer tests, same coverage`. The ratio is context only. Run this block with the loaded workflow skill's path; Python 3 and git are required. It prints one line.

```sh
python3 - "<workflow skill folder>/scripts/check-run.py" "<oldest entry's first commit>^" HEAD <<'PY'
import pathlib, re, runpy, sys
rules = runpy.run_path(sys.argv[1])
_, code, tests = rules["growth"](".", sys.argv[2], sys.argv[3])
stock = [0, 0]  # code, tests; use check-run's receipt and test-file definitions
for name in rules["git_out"](".", "ls-files", "-z").split("\0"):
    path = pathlib.Path(name)
    if not name or re.search(rules["RECEIPTS"], name) or not path.is_file():
        continue
    data = path.read_bytes()
    if b"\0" not in data:
        stock[bool(re.search(rules["TEST_FILE"], name))] += len(data.splitlines())
ratio = f"{stock[1] / stock[0]:.2f}" if stock[0] else "n/a"
advice = "⚠️ workflow improve tests - goal: fewer tests, same coverage" if tests > code else "✅"
print(f"tests net {tests:+d} · code net {code:+d} · tracked tests/code {ratio} · {advice}")
PY
```

- **Missing evidence.** Recent entries without `Run:`/`Seats:` lines: ⚠️ the wrap step is being
  skipped -- nothing can be judged until it isn't.
- **Stale routing.** `ROUTING.md`'s *Last verified* date > 90 days old, or a *Trial* entry with no
  run in the last ~10 entries: ⚠️ re-verify model IDs in the picker / clear or use the trial.
- **Reviewer exam set.** It lives in the private `j-skills-evals` repo, cloned at `~/.agents/j-skills-evals`;
  missing clone is ⚠️ (give `gh repo clone johnviklund/j-skills-evals ~/.agents/j-skills-evals`). A per-repo
  `evals/strict-reviewer/` is ⚠️ "move its cases into the exam set". Cases referencing a
  `.workflow/` path are 🔴 (the scratch is gone; the case is worthless). More than 10 cases is ⚠️
  (rolling cap; recommend a human prune). A case without
  an inlined diff or its P0/P1 lines is ⚠️. Fewer than 3 usable cases is ⚠️ -- the exam cannot run;
  seed it from shipped diffs (the `evals` skill's *seeded* kind).
- **Unchecked reviewer.** The strict-reviewer model in `ROUTING.md` has no passing entry in
  the exam set's `RESULTS.md` and the set has ≥3 usable cases: ⚠️ recommend
  `evals.run reviewer`. No other seat is examined -- do not recommend exams for them.
