---
name: plain
description: >
  Plain English for people. Explain mode: explain something in simple terms, or re-explain the
  last message for a reader who has lost the thread. Use on "in simple terms", "explain simply",
  "ELI5", "plain English", "plain language", "wait, what?", "I don't follow", "say that again
  simpler". Rewrite mode: rewrite text or a file so it carries no AI patterns and keeps every
  fact. Use on "remove AI patterns", "unslop", "sounds like AI", "make this plain". Other skills
  read its rules.md for any text a person reads.
---

# plain

The reader is the user, who runs many projects at once and has just switched into this one. They
know how to code. They do not hold this session in their head.

All writing follows [`rules.md`](rules.md), the single source of the plain-language rules. Read
it before writing. Other skills read `rules.md` directly and skip the modes below.

## Explain mode

**Invocation:** `plain` re-explains the last message · `plain <question>` explains that.

1. **Ground.** Done when you can name the repo, the task and what just happened. Use the
   conversation first. In a fresh session, read `git status`, `git log --oneline -5` and the
   newest `.workflow/<slug>/` artifact when one exists.
2. **Write the answer** in this order:
   - **Where we are:** one sentence with the repo, the task and the last step.
   - **The short answer:** two or three sentences that stand alone.
   - **More detail,** only what the question needs. A concrete example from this repo beats an
     analogy. Define each repo term in passing.
   - **What you need to do,** only when the reader must decide or act: lettered options with a
     recommended default.
3. **Check** the answer against every rule in `rules.md`. Keep it under ~200 words unless the
   reader asked for depth.

When the reader needs proof or a page to keep, end with one line: `understand <area>` writes a
cited explainer. Explain mode writes no files.

## Rewrite mode

**Invocation:** `plain rewrite <file>` or pasted text with a rewrite trigger.

1. **Rewrite** with every rule in `rules.md`. Keep every fact, number, name, link and code span.
   Keep the intended tone.
2. **Self-audit** as `rules.md` describes, then fix what it finds.
3. **Deliver.** A named file is edited in place; pasted text comes back as text. Say in one line
   what kind of changes you made, and name any fact you could not keep plain without changing it.
