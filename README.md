# Oracle box

You lock facts. The oracle fills empty slots. The agent builds from the binding.

You do not pick palettes, tropes, layouts, or “a random word.”
You point the agent at this folder.

```
oracle/
  ORACLE.md: standing orders for any agent
  MENU_RULES.md: update menus when a direction chosen doesn't exist
  METHODS.md: how methods 1, 3, 4, 5 are executed
  YOU.md: what you actually have to do (read this)
  oracle.py: the sampler — run this, don't narrate a roll
  schemas/: which slots exist per job type
  menus/: the lists the sampler indexes into
  draws.log: created after the first draw
```

## Fastest way to use it

1. Keep this folder next to the project (or paste `ORACLE.md` into the agent’s project instructions).
2. Say one block like this:

```
Follow oracle/ORACLE.md
Job: website
Locks:
- character: Flash the sloth from Zootopia
- deliverable: a website that tells a story
- fact: he works at the DMV
Invoke the oracle for everything else.
Use method 3. Use method 4 for the hook.
Then build the site.
```

3. If the agent can run commands, it should run:

```
python oracle/oracle.py draw --job website --method 3 \
  --lock "character=Flash the sloth from Zootopia" \
  --lock "deliverable=website that tells a story" \
  --lock "fact=he works at the DMV" \
  --slot-method hook=4
```

4. You should see an `ORACLE BINDING` block first. After that, the agent may work.
   If it skips the block and starts designing, stop it and point at `ORACLE.md` again.

## Method numbers (what you say)

| You say | What happens |
|---|---|
| `use method 3` (default) | Script picks an index with OS entropy, binds the exact menu line |
| `use method 1` | Same entropy; still mapped through a menu if the slot has one |
| `use method 4` | RANDOM.ORG picks the index; hook slot fetches a real Wikipedia title |
| `use method 5` | Hash of time + your locks (+ optional headline). Add `daily` to freeze one direction per UTC day |

Mix freely:

```
Use method 3 for visual, structure, engine, constraint.
Use method 4 for the hook.
```

## Jobs the schemas already know

- `website` — visual, structure, story engine, constraint, optional hook + motion
- `story` — engine, constraint, object, place texture, optional hook
- `design` — visual, constraint, type pairing, optional motion
- `product` — product engine, visual, constraint, ugly flaw, optional hook
- `generic` — visual, engine, constraint, optional hook

If you ask for something else (“a zine”, “a ritual”), the agent should use `generic` or add a schema with at least 12 concrete menu items *before* sampling.

## What you own vs what the box owns

You own anything you type under **Locks**. That is sacred. The agent may not improve Flash, swap Zootopia for a generic sloth, or drop the DMV.

The box owns every slot in the schema you did not lock.

The agent owns craft: making those two lists into one coherent thing.
