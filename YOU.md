# What you have to do (and what you can refuse to do)

This is the human side. Short on purpose.

## You must do these once

1. Put this `oracle/` folder where the agent can read it.
2. Tell the agent, in project instructions or at the start of a chat:
   `Follow oracle/ORACLE.md. Empty slots go to the oracle. Do not self-sample.`
3. When you start a job, write **locks**. Locks are the only creative decisions you owe the system.

That is the whole setup.

## You must do this every job that requires the agent to fill a direction on its own

Write locks. A lock is a fact or a veto, not a vibe.

Good locks:

- character: Flash the sloth from Zootopia
- deliverable: one-page website that tells a story
- fact: he works at the DMV
- veto: no sequel-bait, no singing, no extra Disney characters unless drawn as background signage
- audience: adults who already know the film
- runtime: under 3 minutes of reading

Bad locks (too vague to protect, too empty to bind):

- make it cool
- surprise me
- a nice website
- random but good

If you say only “make a website about Flash,” the schema will still fill visual / structure / engine / constraint. That is allowed. The work will be specific. It may not be the site you privately wanted. That is the deal.

## You may do these. You do not have to

- Name a method (`use method 5`, `use method 3`).
- Name methods per slot (`hook = method 4`).
- Lock a slot yourself (`visual: Brutalist raw HTML`) — then the oracle skips that slot.
- Add a line to a menu when you keep seeing the same flavor of output.
- Run `oracle.py` yourself and paste the BINDING into the chat if the agent cannot execute code.

## You should not do these

- Pick the palette, the trope, the layout, or the “random word.”
- Re-roll because the binding is awkward. Awkward is the point.
- Argue the agent into “something more on-brand” after the binding. That is skipping the oracle.
- Ask the model to build the menus *and* pick from them in the same breath. If a menu is missing, it must write ≥12 concrete items, *then* run the sampler.

## Is “Flash website, oracle for everything else” enough?

Yes, as a *start*, because `schemas/website.yaml` already lists the empty slots.

It is not enough if you care about any of:

- tone toward the film (homage vs satire vs unofficial fan work)
- whether Flash can speak
- whether other Zootopia characters may appear
- length
- whether it must work offline
- language

Those are locks. Add them if you care. Leave them out if you want the box to decide.

## Minimum prompt you can copy

```
Follow oracle/ORACLE.md and run oracle/oracle.py if you can.

Job: website

Locks:
- character: Flash the sloth from Zootopia
- setting fact: DMV
- deliverable: a website that tells a story
- veto: do not add other named Zootopia leads

Invoke the oracle for every empty slot.
Default method 3. Hook method 4.
Print the BINDING block. Then build.
```

## If the agent cheats

Cheating looks like:

- no BINDING block
- “I rolled 7 in my head”
- “the draw felt off so I picked Swiss modern instead”
- extra pages or extra heroes not in the schema

Reply with only: `Stop. Re-read ORACLE.md. Draw first. Do not discard the draw.`
