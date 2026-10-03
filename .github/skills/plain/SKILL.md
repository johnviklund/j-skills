---
name: plain
description: >
  Plain English for people. Explain mode: explain something in simple terms, or re-explain the
  last message for a reader who has lost the thread. Use on "in simple terms", "explain simply",
  "ELI5", "plain English", "plain language", "wait, what?", "I don't follow", "say that again
  simpler". Rewrite mode: rewrite text or a file so it carries no AI patterns and keeps every
  fact. Use on "remove AI patterns", "unslop", "sounds like AI", "make this plain". Other skills
  invoke it for its Rules before writing any text a person reads.
---

# plain

The reader is the user, who runs many projects at once and has just switched into this one. They
know how to code. They do not hold this session in their head.

All writing follows the *Rules* below, the single source of the plain-language rules for every
j-skill. **Sent here by another skill?** Apply the Rules to the text that skill writes for a
person, skip both modes, and return to that skill.

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
3. **Check** the answer against every rule in *Rules*. Keep it under ~200 words unless the
   reader asked for depth.

When the reader needs proof or a page to keep, end with one line: `understand <area>` writes a
cited explainer. Explain mode writes no files.

## Rewrite mode

**Invocation:** `plain rewrite <file>` or pasted text with a rewrite trigger.

1. **Rewrite** with every rule in *Rules*. Keep every fact, number, name, link and code span.
   Keep the intended tone.
2. **Self-audit** as *Rules* describes, then fix what it finds.
3. **Deliver.** A named file is edited in place; pasted text comes back as text. Say in one line
   what kind of changes you made, and name any fact you could not keep plain without changing it.

## Rules

The rules cover text people read: chat answers, reports, cards, decisions, explainer pages,
READMEs. Rule numbers are stable ids. A removed rule leaves a gap; a new rule takes the next number.

**Scope.** The rules apply to prose. Code, commands, file paths, identifiers, quoted text that
must stay word for word, and cite markers such as `[1]` are not prose and stay as they are.

### Sentences and paragraphs

1. **One idea per sentence.** At most 20 words in a step the reader follows, 25 in a description.
   If the reader has to go back to parse a sentence, split it or drop a clause.
2. **Main point first.** A paragraph opens with its point and holds at most six sentences. A
   run of one-sentence paragraphs reads as a list, so join them or make the list.
3. **Active voice, present tense.** Name the actor: "queries are validated" becomes "the
   compiler validates queries". Passive is fine only when the actor is unknown or does not matter.
4. **Whole sentences.** Keep articles and verbs, and spell out arrows and abbreviations. "Parser
   rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2,
   and writes nothing."
5. **A list for three or more steps, a table for a comparison.** Use the number of items the
   content has. Forcing ideas into groups of three is a tell.

### Words

6. **One word, one meaning.** Pick one term per concept and keep it. Cycling through synonyms
   such as "protagonist, main character, hero" makes the reader wonder if they are different things.
7. **Define each term the first time.** A repo term, acronym or jargon word gets a short plain
   definition on first use. Prefer the repo's own name for a thing over a new one.
8. **Plain words.** "utilize" and "leverage" become "use", "facilitate" becomes "help",
   "numerous" becomes "many", "in the event that" becomes "if".
9. **No AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner,
   interplay, intricate, landscape, pivotal, robust, seamless, showcase, tapestry, testament,
   underscore, vibrant. Replace each with the plain word or cut it.
10. **Concrete nouns, not metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus,
    primitive, harness, surface as in "API surface", bedrock, scaffolding, modality, paradigm,
    gold-plating, ratchet, endgame, north star, flywheel. "Substrate" becomes "base", "wedge in"
    becomes "add", "gold-plating" becomes "more than the job needs".
11. **Say "is" and "has".** "serves as", "stands as", "boasts" and "features" become "is" or "has".
12. **Strong verbs, few adverbs.** "runs quickly" becomes "is fast" or the number. "significantly
    improves" becomes the measured change.

### Meaning

13. **Say what it does, not how it feels.** "SQL you can read" names a feeling. "`.toSQL()`
    returns the exact string sent to the database" names the mechanism. If a sentence could
    appear unchanged in another project's docs, it says nothing about this one. Cut it.
14. **Literal, not mannered.** No aphorisms, no figurative verbs such as "rides along", no
    personified code such as "the plan holds it", no rhetorical fragments. Say what you mean.
15. **Direct, not "not just X, but Y".** State the point.
16. **Name the source.** "Experts believe" and "some argue" either name who, or go.
17. **No empty -ing tails.** "...highlighting the need for", "...ensuring that" add nothing.
    Delete them or state the real effect.
18. **No false ranges.** "from X to Y" only when X and Y sit on one scale. Otherwise list the items.
19. **Hedge once.** "could potentially possibly be argued that it might" becomes "may".
20. **Specific endings.** "The future looks bright" becomes the plan or the fact.
21. **No filler.** "In order to" becomes "to", "due to the fact that" becomes "because", "it is
    important to note that", "basically" and "note that" go.

### Punctuation and formatting

22. **No em dashes.** End the sentence or use a comma. En dashes and a hyphen used as a dash are
    the same tell.
23. **No parentheses in prose.** Make the aside its own sentence, use a comma, or cut it.
24. **Colons only before a list or an example.** Not as a link between two halves of a sentence.
25. **Bold sparingly.** Not every name or acronym. A bold label followed by a colon that repeats
    the line, "**Performance:** Performance improved", becomes prose. A bold lead-in that ends in
    a period and is followed by new detail is fine.
26. **Sentence case headings.**
27. **No decorative emojis** in headings or bullets.
28. **Straight quotes,** not curly ones.

### Tone

29. **No chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!",
    "Great question!", "You're absolutely right!" go. Answer directly.

### Self-audit

After writing, ask: "What makes this obviously AI-generated?" Fix what you find, then check
every rule once more. The text is done when no rule fires.
