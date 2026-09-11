# ORACLE — standing orders

The oracle is the only thing allowed to make a first choice.
You (the agent) interpret. You do not originate empty slots.

If this file is in context, or the user says "invoke the oracle",
you MUST follow this protocol before generating the deliverable.

## What the human owns vs what you own

Human may lock any of:

- the idea
- a character, brand, fact, or constraint
- the deliverable type (website, story, deck, product)
- a method number: `use method 1` / `3` / `4` / `5`
- which slots to fill (`oracle: tone, structure, hook`)

Everything not locked is an empty slot.
Empty slots are filled by the oracle, never by your taste.

## Hard rules

1. Read `schemas/<job>.yaml` for the job type. If the job is unclear, use `schemas/generic.yaml`.
2. Copy every human lock into the BINDING block unchanged. Do not improve them.
3. For each empty slot, draw with the requested method. Default method: `3`.
4. If a method needs a network call and it fails, fall back to method `5`, then method `1`. Never fall back to "I'll just pick".
5. Print a BINDING block before any creative work. Then obey it.
6. You may combine draws. You may not discard a draw because it is awkward or off-brand.
7. Log the draw in `draws.log` (append). If you cannot write the file, include the same line in your reply.
8. After BINDING, you are a craftsman. Make the locked + drawn spec coherent. Do not add a new axis.

## How the human invokes you

Any of these are valid:

- `Invoke the oracle. Job: website. Locks: Flash from Zootopia; site tells a story.`
- `Use method 5. Then design the homepage.`
- `Use method 3 for visual and structure. Use method 4 for the hook.`
- Point you at this folder: `Follow /oracle/ORACLE.md`

They do not have to roll numbers. They do not have to pick a palette.

## BINDING block format

```
ORACLE BINDING
job: website
method: 3
fallback_used: none
locks:
  - character: Flash the sloth from Zootopia
  - deliverable: website that tells a story
draws:
  visual: Swiss grid + two-color acid on bone
  structure: one long scrollytelling page, no nav
  engine: bureaucratic delay as the plot
  constraint: almost no dialogue; time is visible on screen
  hook: (none — not drawn)
raw:
  - visual index=17 menu=visual_directions.json method=3
  - structure index=4 menu=site_structures.json method=3
timestamp: 2026-09-08T16:20:00Z
```

After this block, build. Do not reopen the draws.

## Method cheat sheet

| # | Name | When the human says | What you actually do |
|---|---|---|---|
| 1 | Code entropy | `use method 1` | Run `oracle.py` or `secrets.randbelow` / `secrets.choice`. No menus required if they only need a number; if a slot has a menu, still index into the menu. |
| 3 | Menu + index | `use method 3` (default) | Load the slot's menu JSON. Draw an index with method 1. Bind `menu[index]`. |
| 4 | Live API | `use method 4` | Hit RANDOM.ORG and/or MediaWiki random. Bind the returned integer or page title. Optionally inflate the title with one search. Do not swap the page. |
| 5 | Public-state hash | `use method 5` | `SHA256(utc_iso + locks + optional_headline + uuid)`; map hex into the menu length. Same result if replayed with the same inputs. |

Details: `METHODS.md`.
Runner: `oracle.py`.
Human brief: `YOU.md`.
Folder brief: `README.md`.

## Job detection (do not ask if you can infer)

- website, landing, web app, page → `website`
- story, fiction, tale, script → `story`
- visual, brand, poster, UI look → `design`
- product, startup, feature, spin up → `product`
- anything else → `generic`

## What "invoke the oracle for everything else" means

It is valid ONLY because the schema lists the slots.
If you invent new slots on the fly, you have skipped the oracle.

Allowed extra slots: none, unless the human names them.

## Refusal cases (still draw, then warn)

- Lock contradicts a draw: keep both, resolve in the work, do not reroll.
- Menu item is offensive or unusable for the lock: draw the next index (`(i+1) % n`) once, log the skip. Only once.
- Child sexual content, real-world crime how-to: stop. Oracle does not override that.
