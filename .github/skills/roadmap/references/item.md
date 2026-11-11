# roadmap item

Turns one idea into one item. The idea usually arrives as a solution ("add a dashboard"); the item
leaves as a problem with evidence, a chosen option, and a way to tell it is solved.

## 1. Ground

Run `check` and `next` on the roadmap. Read `PRODUCT.md` and `DESIGN.md`, the open items, the
archive's headings, `TODO.md`, and the code or docs the idea touches. Done when you can say which
outcome in `PRODUCT.md` the idea moves, which group it belongs to, which open items touch the same
problem, and whether the archive shows it was already done.

## 2. Restate and gather evidence

Open round 1 with **Problem, as I read it**: two or three lines on who meets the problem and what
they see, written with no solution in them. The human's ideas about the fix are options, so set
them aside for step 3. Then find the evidence yourself: count the cases, measure the cost, quote
the line, name the commit. Done when the restatement holds at least one fact you looked up.

## 3. Grill the why

Ask only what the evidence left open, in one round where you can:

- Who pays for this today, and what does it cost them?
- Why now: what changes if we wait?
- Which option: the human's idea, one or two others, and "do nothing", with a recommendation.
  "Do nothing" wins when the cost is small or the problem fades by itself.
- What would someone observe once it is solved?

An idea that moves no outcome in `PRODUCT.md`, or works against one of its principles or
non-goals, becomes the first question: drop it, or change the north star on purpose. A change to
`PRODUCT.md` is the human's call and goes through the `bootstrap` skill's update step. An open item
that solves the same problem, or contradicts this one, becomes a question: merge, keep both with a
boundary, or replace. Stop when every required field holds a fact or a human answer.
An idea that needs several jflow runs becomes several items: propose the split.

## 4. Play back and write

Show the item in chat, exactly as it will be written, with its group and a proposal for Next up:
its place, or that it waits. Wait for an explicit yes. Then write it, and finish as `SKILL.md`
says under *Changing the file*. Done when the item is committed and `check` prints no `error:` line.
