# delete-workflow
Status: ready
Base: f2137fb
Serves: none

## Problem
Two skills do one job. workflow is 786 KB, its runs took 3 to 10 sessions and up to 7 review
cycles, and j-skills took 232 sessions in two weeks, mostly building rules for workflow. The
verdict on 2026-11-16 keeps jflow, and until workflow goes every skill change has to keep both in
step. Six things still need workflow: the git hooks, `SKILL-IMPACT.md`, the `ROUTING.md` readers,
the reviewer exam, `workflow todo` and the run readers in understand and other skills. The
installed hook stubs search only `skills/workflow/scripts/hooks.py`, so deleting workflow without
a new home blocks every push in the repos that have the hooks. Roadmap item delete-workflow in
ROADMAP.md.

## Goals
1. workflow and the scripts only it uses are gone, and no surviving skill,
   `.claude-plugin/plugin.json`, the README or AGENTS.md points at it.
2. `jflow/scripts/hooks.py` installs a `pre-push` hook that runs gitleaks on outgoing commits.
   Install replaces old workflow stubs, removes our old `pre-commit` stub, and still refuses
   foreign hooks and `core.hooksPath`.
3. `SKILL-IMPACT.md` and its archive move to `checkup/` with every row intact, and
   `skill-trials.py` finds them by default.
4. `ROUTING.md` goes. checkup, agent-docs, design and evals take seats from `jflow.py seat` or
   jflow's `config.json`. evals examines jflow's check seat against `jflow/references/check.md`.
5. retro, understand, memory.compact, memory.remember, plain and checkup read `.jflow/` runs only.
   A new idea becomes a plain `TODO.md` line, not `workflow todo`.
6. The README leads with jflow, and AGENTS.md lists three suites.

## Non-goals
- Carrying over multi-ticket plans, mutation testing, worktrees, unattended mode or the
  brainstorm, improve, park and realign commands.
- Editing or deleting old `.workflow/` folders in any repo. They stay as history.
- Changes to jflow's steps, the conductor skill or the evals exam set.

## Constraints
- Must not break: the checkup, jflow and roadmap suites; a push from a repo with hooks still
  scans for secrets, and a push stays blocked when gitleaks is missing.
- Ask first: nothing. The hook home, the stub upgrade, the SKILL-IMPACT move and dropping
  ROUTING.md were settled in the grill.
- Gate: none. After the push, done runs `npx skills update -g`, deletes the installed `workflow`
  folder if the update leaves it, and runs `hooks.py install` in each repo with hooks.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | workflow and the scripts only it uses are gone, all other suites pass, `git push` still scans for secrets in every repo with the hooks, and no surviving skill points at workflow. | repo | `test ! -e .github/skills/workflow -a ! -e skills/workflow`; the checkup, jflow and roadmap suites; `grep -rnwi workflow .github/skills skills README.md AGENTS.md .claude-plugin/plugin.json`, leaving out `tests/triggers.tsv`; rows 2 and 3 | Folder and link gone; suites OK; every grep match is plain English and names none of the skill, its commands, its files or `.workflow/`; rows 2 and 3 pass | new | red |
| 2 | Goal 2: the new hook blocks a secret | throwaway repo with a bare remote | `jflow/scripts/hooks.py install`; push a commit holding a fake AWS key; push a clean commit; push again with gitleaks off PATH | Key push exits non-zero with a gitleaks finding; clean push succeeds; no-gitleaks push exits non-zero and names gitleaks | new | red |
| 3 | Goal 2: old stubs upgrade, foreign hooks stay | repo A with stubs installed by `f2137fb:.github/skills/workflow/scripts/hooks.py`; repo B with a foreign `pre-push` | run the new install in each | A: `pre-push` names no `skills/workflow` path and no `pre-commit` stub is left; B: install exits 1 and the foreign hook is unchanged | new | red |
| 4 | Goal 3: no impact row lost | `checkup/SKILL-IMPACT.md`, its archive, `skill-trials.py` | diff both moved files against their f2137fb copies; `skill-trials.py --sweep` with no `--impact` | Diffs show only path-reference lines; sweep exits 0 and lists the same trialing rows as `--impact` on the old file at f2137fb | new | red |
| 5 | Goal 4: seat readers use jflow | checkup `references/seats.md` and `references/report.md`, agent-docs, design, evals | grep each for `jflow.py seat` or `config.json`; grep evals for `jflow/references/check.md` | Every file matches; none names `ROUTING.md` | new | red |
| 6 | Goal 5: run readers read `.jflow/` | retro, understand, memory.compact, memory.remember, plain, checkup `references/workspace.md` | grep each skill folder and `workspace.md` for `\.workflow` and `\.jflow` | 0 `.workflow` matches and at least 1 `.jflow` match in each | new | red |
| 7 | Goal 6: README leads with jflow, no dead links | README.md, AGENTS.md | first command in README; resolve every relative link; run the AGENTS.md test command | First command is `jflow spec …`; 0 dead links; the command runs three suites, all OK | new | red |

## Human checks
- On the work laptop: run `npx skills update -g`, delete the installed `workflow` folder if the
  update leaves it, and run `hooks.py install` in each repo with hooks.
- Read the new README top once for plain language.
