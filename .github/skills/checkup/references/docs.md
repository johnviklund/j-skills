### 3. Doc freshness & consistency

- **Canonical docs present.** Note which of `AGENTS.md`, `README.md`, `PRODUCT.md`, `DESIGN.md`,
  `PRD.md`, `MEMORY.md`, `MEMORY_ARCHIVE.md` exist; a repo that has some but is missing an expected
  one is worth a note, not an error.
- **Dead skill references.** Skill names referenced in `AGENTS.md`/README that no longer resolve to a
  real skill (e.g. renamed but the reference wasn't updated). **Scope this to actual skill references** --
  backticked names in the skills-list sentence, or tokens matched against the real skill inventory --
  **not every prefix-shaped token.** Doc *paths* and identifiers often share a skill's prefix (e.g. a
  `acme-poc/` docs folder vs. `acme-*` skills) and will false-positive a naive `grep`.
  🔴 only when a name genuinely referenced *as a skill* exists nowhere (repo-local, plugin, or Codex).
- **Prose-doc staleness (heuristic).** Compare each canonical doc's last commit date against recent
  activity in the area it governs (e.g. `DESIGN.md` vs. churn under `web-ui/`):
  `git log -1 --format=%cs -- DESIGN.md` and `git log --since=... --oneline -- web-ui | wc -l`.
  If a doc is untouched while its area changed a lot, say "worth a human skim" -- never assert it's wrong.
- **Broken internal links.** Doc references to repo paths that don't exist are ⚠️.
- **Verify skill.** When the repo has `.agents/skills/verify-*/`: a missing or dangling
  `.claude/skills/verify-*` symlink is 🔴 (Claude Code cannot see the skill); a
  `features/README.md` without a `Last maintained: DATE @ SHA` line is ⚠️. Count commits since
  that sha outside `.workflow/` and `*.md` (`git log --oneline SHA..HEAD -- . ':(exclude).workflow'
  ':(exclude)*.md' | wc -l`): a stamp older than ~30 days with 20 or more such commits is ⚠️
  "feature map may have drifted -- `verify.maintain`". A repo with a user surface (UI, CLI, API)
  and no verify skill is ⚠️ "no scripted way to drive the app -- `verify.create`".
