# Skill mechanics

The skill-specific branch of [`agent-docs`](SKILL.md): what changes when the document is a skill (frontmatter, the invocation choice, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously, and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full).
- A **user-invoked** skill strips the description from the agent's reach: only the human typing its name can invoke it, and no other skill can. Zero context load, but it spends cognitive load: you are the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing: a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

Shared reference that two user-invoked skills both need can live in neither: with no descriptions, neither can fire the other. Push it to a plain file outside the skill system: external reference any skill can point at.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts), or another skill must reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. It can only hint, never fire them: user-invoked skills have no description, so nothing but the human can reach them.

## j-skills conventions

What this repo has measured or settled, on top of the reference above:

- **Explicit-trigger descriptions.** A j-skill that should fire only when typed still keeps a model-facing description and ends it with "Run only on an explicit `<name>` message; never on casual mentions of ...". It does not set `disable-model-invocation`, so for a j-skill this replaces the user-invoked choice in *Invocation*. A skill meant to fire on phrases, like `plain`, lists those phrases instead.
- **Description under ~900 characters.** Copilot CLI silently dropped a skill whose description was around 1033 to 1078 characters: it loaded with no error and left that one skill out of `copilot skill list`. After adding or editing a skill, check that it registered with `copilot skill list --json`.
- **Shared reference lives in one skill's file.** When several skills need the same rules, one skill owns them in a file the others point at by skill name and file, as every skill that writes for a person points at `plain`'s `rules.md`. No skill keeps a copy.
- **No external skills.** A j-skill names only j-skills. `checkup` flags any other skill name as a dead reference.
- **Every change is logged.** A skill change gets a row in `workflow/SKILL-IMPACT.md` and is judged on the runs that follow, not by review alone.
