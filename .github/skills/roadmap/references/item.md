# roadmap item

Turns one idea into one item. The idea usually arrives as a solution ("add a dashboard"); the item
leaves as a problem with evidence, its impact, and a way to tell it is solved. It names no fix:
jflow spec chooses one after grilling the problem.

## 1. Ground

Run `check` and `next` on the roadmap. Read `PRODUCT.md` and `DESIGN.md`, the open items, the
archive's headings, `TODO.md`, and the code or docs the idea touches. Done when you can say which
outcome in `PRODUCT.md` the idea moves, which group it belongs to, which open items touch the same
problem, and whether the archive shows it was already done.

## 2. Restate and gather evidence

Open round 1 with **Problem, as I read it**: two or three lines on who meets the problem and what
they see, written with no solution in them. The human's ideas about the fix become `Open for spec`
questions in step 3. Then find the evidence yourself: count the cases, measure the cost, time the
query, quote the line, name the commit. Done when the restatement holds at least one fact you
looked up.

## 3. Grill the why

Ask only what the evidence left open, in one round where you can:

- Who pays for this today, and what does it cost them?
- Impact: what gets better once it is solved, and by how much? Measure it when the repo can tell
  you, and use the unit the open items beside it use, so the two can be compared.
- Why now: what does waiting cost? When it costs nothing, recommend that the item waits.
- What would someone observe once it is solved?

Do not choose the fix. Write the human's idea, and any other worth weighing, as questions in
`Open for spec`; jflow spec weighs them, with "do nothing", once the problem is settled.

An idea that moves no outcome in `PRODUCT.md`, or works against one of its principles or
non-goals, becomes the first question: drop it, or change the north star on purpose. A change to
`PRODUCT.md` is the human's call and goes through the `bootstrap` skill's update step. An open item
that solves the same problem, or contradicts this one, becomes a question: merge, keep both with a
boundary, or replace. Stop when every required field holds a fact or a human answer.
An idea that needs several jflow runs becomes several items: propose the split.

## 4. Play back and write

Show the item in chat, exactly as it will be written, with its group, its place in that group by
priority, and a proposal for Next up: its place, with why it goes before the item below it, or
that it waits. Wait for an explicit yes. Then write it, and finish as `SKILL.md`
says under *Changing the file*. Done when the item is committed and `check` prints no `error:` line.
