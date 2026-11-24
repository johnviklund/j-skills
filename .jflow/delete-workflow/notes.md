# delete-workflow notes

## Judgement calls

- **Row 1 against row 4.** `checkup/SKILL-IMPACT.md` and its archive moved word for word, as row
  4 asks. Their history rows name the deleted skill in 91 lines, such as `| 2026-11-03 | workflow |`.
  Row 1's grep covers `.github/skills`, so it matches those rows. Both rows cannot pass as written.
  The rows are a log of past changes, not pointers to the skill. I left them intact and asked the
  human.
- **Hook marker.** New stubs carry `# j-skills hook`. Install treats any `# j-skills <word> hook`
  line as ours, so older stubs upgrade without the code naming the old skill. `--check` reports
  `installed` only for a stub with the new marker, so checkup flags an old stub.
- **pre-commit.** Install removes our old `pre-commit` stub and leaves a foreign one alone. It no
  longer refuses a foreign `pre-commit`, because it no longer writes one.
- **Hook tests.** `jflow/scripts/tests/test_hooks.py` is the old suite without its pre-commit
  cases, plus one test for the upgrade from an old stub. That fixture uses a made-up marker,
  `# j-skills old hook`. Row 3 runs the real old install from `f2137fb`.
- **Save tags.** `skill-trials.py` now reads `[saved→skill]` tags from `.jflow/*/notes.md`, not
  `.workflow/*/learnings.md`. No learnings file in this repo held a tag, so the sweep output is
  unchanged. `memory.remember/references/runs.md` says where the tag goes.
- **Removal candidates.** `skill-trials.py` used to point at `workflow improve`. It now prints
  `→ TODO.md: remove from <skill>`.
- **No-verify rule.** `config-scan.py` checks for jflow repos and asks only for the
  `git push *--no-verify*` deny rule. The commit rule guarded the deleted pre-commit hook.
- **Design seats.** jflow's seat config accepts only flow steps, so design cannot get its own
  seat there. The design seat is `jflow.py seat build` at effort high. Fresh eyes keeps
  GPT-6.1 Terra, which is cheaper, and falls back to `jflow.py seat check`.
- **evals.** The exam now gives the candidate `jflow/references/check.md`, told to review the diff
  for P0/P1 defects only. The command stays `evals.run reviewer`, so the exam set and
  `RESULTS.md` keep their names.
- **checkup seats.** Code and test growth come from the `jflow:` worklog lines, because
  `check-run.py` is gone. The ROUTING staleness check went with ROUTING.md.
- **README.** The illustration `docs/assets/workflow-character.png` showed workflow's five steps,
  so I deleted it with its prompt file. Setup now links Claude Code to `~/.agents/skills` as well,
  because the Claude install steps lived in the deleted workflow README.
- **memory.remember.** `references/workflow-runs.md` became `references/runs.md`, about `.jflow/`
  runs.

## Fix after check-1

- **Defect 1.** `skill-trials.py` now reads `jflow:` worklog lines. The score is fix rounds plus
  check defects, and the run counts for `jflow`, or for the skills on a `- Skills:` line when
  one exists. Older entries keep their old score. Mixing the two scores in one before/after
  window is possible only for a row whose skills both kinds name. One test, which fails without
  the fix. On this repo's worklog, 13 entries are read, and the jflow ones were dropped before.
  A `jflow:` line kept in `notes.md` because a repo has no worklog is still not read: it has no
  date of its own.
- **Defect 2.** Design's fresh eyes always uses the other vendor. When the design seat is OpenAI,
  it uses `jflow.py seat check`, which already moves to another vendor. Checked with an OpenAI
  build override: `seat check` printed `claude-opus-5-5`, vendor `anthropic`.
- **Row 1** still waits on the human: the spec conflict with row 4 that code cannot fix.

## Open

- Row 1 against row 4: see above. The human decides.
- Plain-English uses of "workflow" stay, such as memory.compact's `## Workflow` heading.
