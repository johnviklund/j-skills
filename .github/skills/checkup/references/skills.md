### 1. Skill hygiene

Discover the three skill locations first:

```sh
ls .github/skills/ 2>/dev/null                                   # repo-local skills (this repo)
ls ~/.copilot/installed-plugins/*/*/skills/ \
   ~/.copilot/installed-plugins/_direct/*/skills/ 2>/dev/null    # Copilot plugin/global skills
ls ~/.codex/skills/ 2>/dev/null                                  # Codex skills (symlinks + real dirs)
```

Then check:

- **Name collision with an installed plugin/global skill.** For every repo-local `.github/skills/<name>`,
  is there also a *different* skill named `<name>` installed elsewhere -- a Copilot plugin/global skill,
  or a `~/.codex/skills/<name>` entry? **Ignore a `~/.codex/skills/<name>` that is a symlink pointing
  back to this same repo skill** -- that is intended cross-CLI parity wiring, not a collision (a naive
  name-match false-positives on every skill you've wired into Codex). For genuine matches, **diff the
  `SKILL.md`:** identical content = benign self-publish (note it); **different content = 🔴 harmful
  shadow** (a repo skill hiding a different, often richer, plugin skill). Fix by renaming the repo-local
  one to a repo-specific prefix (e.g. `acme-<name>`) and updating references -- never silently keep the shadow.
- **Folder name ≠ frontmatter `name`.** For each `.github/skills/<dir>/SKILL.md`, confirm `name:`
  matches `<dir>`. A mismatch breaks discovery.
- **Description length.** Flag any skill whose frontmatter `description` exceeds ~900 characters. This
  limit is **confirmed for the Copilot *plugin-install* path** -- the loader silently drops an
  over-length skill (installs with no error, omits it). So it is **🔴 for any skill published/installed
  as a plugin** (it looks installed but isn't; verify `copilot skill list --json | grep '"name": "<skill>"'`).
  For a **repo-local-only** skill loaded directly from `.github/skills/`, discovery tolerates longer
  descriptions -- treat over-length as **⚠️ portability debt** (trim before it is ever published), not a
  hard failure. When unsure, check whether a matching installed plugin or a `copilot-plugins/` packaging
  dir exists.
- **Codex parity.** Codex only loads from `~/.codex/skills/` -- it does not scan a repo's
  `.github/skills/`. For each repo-local skill meant to be available in Codex, confirm a
  `~/.codex/skills/<name>` entry exists and resolves. Missing ones are ⚠️ (Copilot-only until linked).
- **Broken Codex symlinks.** Dangling links whose target no longer exists:
  `find ~/.codex/skills -maxdepth 1 -type l ! -exec test -e {} \; -print`. Each is 🔴.
- **Skills stand alone.** In the j-skills repo (its `.claude-plugin/plugin.json` is named `j-skills`),
  every skill a j-skill invokes, reads or routes to must be a folder under `.github/skills/`. Match
  backticked names used *as skills* ("the `x` skill", "invoke `x`", "read `x`'s") against that folder
  list, not every backticked word. A name that is not a j-skill is 🔴: port it or drop the reference.
  Exception: `verify-*` (and `verify-APP`) names the repo-local skill that `verify.create` generates.
  Exception: `understand`'s `video.md` names `hyperframes` and `hyperframes-registry`, the
  HyperFrames video skills the user chose on 2026-10-26. Check instead that both are installed:
  `ls ~/.agents/skills/hyperframes*`, ⚠️ when missing, fixed by
  `npx skills add heygen-com/hyperframes -g -a claude-code codex github-copilot -s hyperframes hyperframes-cli hyperframes-registry -y`.
- **Self-publish drift.** For a skill packaged as its own plugin (e.g. a `.github/copilot-plugins/<name>/`
  whose `skills/<name>` symlinks back to `.github/skills/<name>`), confirm it is still a symlink (single
  source) and that the installed snapshot matches the repo source. A materialized copy or a stale
  installed snapshot is ⚠️ drift.
