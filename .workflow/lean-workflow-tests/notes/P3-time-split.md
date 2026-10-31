P3 — Where do the suite's 60 s go?

- Tool: `prototypes/P3-time-split/split.py <scripts/tests>` times every `subprocess.run` the suite makes, grouped by program.
- Result @ aefd430 (measured while P2 was running, so total 77 s; the shares are what count):
  script runs 81 %: check-run.py 123 runs (34 %), run-worktree.py 103 (26 %), next-step.py 95 (21 %), about 0.2 s each.
  Fixture git calls 17.5 % (2,291 calls).
- So the suite gets faster only by dropping cases that run a script. Merging tests into tables keeps the time the same, and faster fixtures save 17 % at most.
