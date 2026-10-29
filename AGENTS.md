# AGENTS.md

This repo is the `j-skills` skill collection. Each skill lives in `.github/skills/<name>/`, and
`skills/<name>` is a symlink to it. The CLIs load installed copies, not this clone, so a pushed
skill change reaches them only after `npx skills update -g` (`README.md`, Setup).

## This repo is public

Everything committed here is public, including run folders, receipts and commit messages. Use a
private repo as evidence, but call it "the work repo" and commit none of its file names, code,
data or reports. Commit no home paths, hostnames or account names. gitleaks catches secrets, not
private names, so read a receipt before committing it.

## Verifying your work

The skills are Markdown plus standard-library Python 3: there is no build or lint step. Two
unittest suites cover the scripts. Run them from the repo root as the baseline and before
reporting any step done, and paste the result:

```sh
python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
```

Healthy output: each suite ends with `OK`, and the command exits 0. The workflow suite takes
about a minute. Zero tests run is a failure, not a pass.

A failing test is fixed in the code, never by editing or deleting the test. A ticket that edits
only Markdown also verifies by content with the `grep` its plan names.
