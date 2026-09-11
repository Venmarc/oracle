# Methods 1, 3, 4, 5 — how the agent actually does them

The human only names the method. You execute it.

Preferred: `python oracle.py draw --job website --method 3 --lock "character=Flash from Zootopia" --lock "deliverable=story website"`

If you cannot run the script, do the manual version below and still emit a BINDING block.

---

## Method 1 — code / OS entropy

**Purpose:** a number the model did not pick.

**Do this in a real interpreter, not in prose.**

Python:

```python
import secrets
n = 48                      # length of the menu, or the requested range
print(secrets.randbelow(n)) # 0 .. n-1
print(secrets.choice(["a", "b", "c"]))
```

Node:

```javascript
const crypto = require("crypto");
console.log(crypto.randomInt(0, n));
console.log(crypto.randomUUID());
```

**Do not** use `Math.random()`, `random.random()`, or "I'll pick 17".
**Do not** describe rolling. Run it.

If the slot has a menu, method 1 is only the index. Binding is still `menu[index]` — that is method 3's mapping, and you should still do it.

---

## Method 2: Alphanumeric string

Generate a long, random alphanumeric string using a shell script.

Define the creative direction (color scheme, layout, typography, etc.) based on the string.

---

## Method 3 — menu + index (default)

**Purpose:** useful surprise, not raw noise.

Steps:

1. Open `menus/<file>.json` named in the job schema.
2. `i = secrets.randbelow(len(items))`
3. Bind `items[i]` exactly. Do not paraphrase into a "better" version.
4. Record `index`, `menu`, `method=3`.

Menus must be lists of concrete specs, not adjectives.
Bad: `"minimal"`, `"bold"`, `"fun"`.
Good: `"Swiss grid, two-color acid green on bone, grotesque type, no photos"`.

If you need a menu that does not exist, you may create one with **at least 12 concrete items** first, then sample. Creating the menu is not choosing the winner. Sampling is.

---

## Method 4 — live API (RANDOM.ORG + Wikipedia)

**Purpose:** entropy or a real unchosen fact from outside this machine.

### 4a. Integer from RANDOM.ORG (no API key, quota per IP)

```
GET https://www.random.org/integers/?num=1&min=0&max={N-1}&col=1&base=10&format=plain&rnd=new
```

Strip whitespace. That integer is the index into the menu.
If the body starts with `Error:` or status is 503, fall back to method 5.

Quota check:

```
GET https://www.random.org/quota/?format=plain
```

### 4b. Real-world hook from Wikipedia (MediaWiki API, more reliable than Special:Random)

```
GET https://en.wikipedia.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=1&format=json
```

Bind `query.random[0].title` as the hook.
Optional inflate (allowed): one search or one page summary for that exact title.
Forbidden: "this page is dull, I'll use a nearby famous event instead."

For a *dated* real event rather than a random article, fetch on-this-day or a news list, then use 4a to pick which item in that list.

User-Agent: send a descriptive UA. Wikipedia expects one.

### 4c. Signed / JSON-RPC RANDOM.ORG

Only if an API key exists in the environment as `RANDOM_ORG_KEY`.
Not required for this kit.

---

## Method 5 — hash of public state

**Purpose:** no extra service; same inputs → same draw; still not your taste.

```python
import hashlib, datetime, uuid

utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
locks = "character=Flash from Zootopia | deliverable=story website"
headline = ""   # optional: paste one fetched headline; otherwise leave empty
salt = str(uuid.uuid4())  # omit salt if the human wants replay-by-timestamp

msg = f"{utc}|{locks}|{headline}|{salt}".encode("utf-8")
digest = hashlib.sha256(msg).hexdigest()
index = int(digest[:16], 16) % menu_length
```

Log `utc`, `locks`, `headline`, `salt`, `digest[:16]`, `index`.

If the human says `use method 5` and `daily`, drop `salt` and floor time to the UTC date so the same locks produce one direction per day.

---

## Mixing methods in one job

Allowed and useful:

```
visual, structure, constraint  → method 3
hook                           → method 4b
any leftover numeric id        → method 5
```

Say it in the BINDING block per slot.

---

## Failure order

4 → 5 → 1 → stop and tell the human the oracle could not draw.
Never: "I'll choose so we can keep moving."
