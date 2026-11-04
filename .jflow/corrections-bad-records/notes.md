# Notes: corrections-bad-records

- One catch per transcript, not a guard per field. The three spec rows crash at three different
  lines, and the Codex and Copilot parsers have the same chained `.get` shape, so field guards would
  only cover the shapes seen so far.
- `except Exception`, not a list of types. Bad shapes raise AttributeError, TypeError, KeyError,
  IndexError or ValueError, and a parser bug raises the same ones, so a list would protect nothing.
  The unit tests are what catch a parser bug.
- A malformed transcript is skipped whole. `list()` collects its events first, so it adds no partial
  counts and is left out of `stores: ... file(s)`. Cost: one odd record in a long session drops that
  session's real corrections, silently, because reporting the file is a non-goal.
- A lone surrogate in a JSON string crashed `print`, after the per-file catch. No spec row names it,
  but it is Goal 1. `sys.stdout.reconfigure(errors='replace')` prints it as `?`.
- `str(text)` in the redirect line covers a non-string Copilot message, which reaches `main` outside
  the catch. A string passes through unchanged.
