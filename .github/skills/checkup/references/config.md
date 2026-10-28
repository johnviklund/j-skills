### 5. Config health

- **`.gitignore` coverage.** Confirm it ignores the usual junk (`.DS_Store`, `.env`, venvs, build
  output). Missing common entries are ⚠️.
- **Light secret sniff.** Only flag obvious committed credential files or `.env`; do not attempt a
  deep secret scan (too noisy) -- point at a dedicated tool if the user wants depth.
- **Agent settings.** Run `python3 <checkup skill folder>/scripts/config-scan.py` from the repo
  root. It reads the Claude Code, Codex and Copilot CLI settings files, project and user, and
  prints one finding per line with severity, location and fix: settings that let a tool run
  without asking, hooks that pipe a download into a shell, secrets (🔴 when git tracks the file).
  Copy its lines into the Config section unchanged; they never include a value, so quote them
  rather than opening the files, which would put a secret into the transcript. A setting that
  skips asking may be the human's choice: it stays a ⚠️ line and is never changed here.
