#!/usr/bin/env python3
"""Oracle sampler — methods 1, 3, 4, 5.

The agent (or you) runs this. The model does not invent the draw.

Examples:
  python oracle.py draw --job website --method 3 \\
      --lock "character=Flash the sloth from Zootopia" \\
      --lock "deliverable=website that tells a story"

  python oracle.py draw --job website --method 5 --daily

  python oracle.py draw --job story --method 3 --slot-method hook=4
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
MENUS = ROOT / "menus"
SCHEMAS = ROOT / "schemas"
LOG = ROOT / "draws.log"
UA = "OracleBox/1.0 (personal creative agent; local use)"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_schema(job: str) -> dict:
    path = SCHEMAS / f"{job}.yaml"
    if not path.exists():
        path = SCHEMAS / "generic.yaml"
    text = path.read_text(encoding="utf-8")
    return parse_simple_yaml(text)


def parse_simple_yaml(text: str) -> dict:
    """Tiny YAML subset good enough for the kit schemas. Avoids a PyYAML dependency."""
    job = "generic"
    slots: dict[str, dict] = {}
    do_not_invent: list[str] = []
    current_slot = None
    section = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("job:"):
            job = line.split(":", 1)[1].strip()
            continue
        if line.startswith("slots:"):
            section = "slots"
            current_slot = None
            continue
        if line.startswith("do_not_invent:"):
            section = "dni"
            current_slot = None
            continue
        if section == "dni" and line.strip().startswith("-"):
            do_not_invent.append(line.split("-", 1)[1].strip())
            continue
        if section == "slots":
            if not line.startswith(" "):
                continue
            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()
            if indent == 2 and stripped.endswith(":"):
                current_slot = stripped[:-1]
                slots[current_slot] = {}
            elif indent >= 4 and current_slot and ":" in stripped:
                k, v = stripped.split(":", 1)
                v = v.strip()
                if v.lower() == "true":
                    val: Any = True
                elif v.lower() == "false":
                    val = False
                elif v.lower() == "null":
                    val = None
                else:
                    val = v
                slots[current_slot][k.strip()] = val
    return {"job": job, "slots": slots, "do_not_invent": do_not_invent}


def load_menu(name: str) -> list:
    path = MENUS / name
    if not path.exists():
        raise FileNotFoundError(f"menu not found: {path}")
    data = load_json(path)
    if not isinstance(data, list) or not data:
        raise ValueError(f"menu {name} must be a non-empty JSON list")
    return data


def method1_index(n: int) -> int:
    if n <= 0:
        raise ValueError("menu is empty")
    return secrets.randbelow(n)


def fetch_text(url: str, timeout: int = 12) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def method4_index(n: int) -> tuple[int, str]:
    """RANDOM.ORG integer in 0..n-1. Returns (index, note)."""
    url = (
        "https://www.random.org/integers/"
        f"?num=1&min=0&max={n - 1}&col=1&base=10&format=plain&rnd=new"
    )
    body = fetch_text(url).strip()
    if body.startswith("Error:"):
        raise RuntimeError(body)
    return int(body.split()[0]), f"random.org:{body.split()[0]}"


def method4_wiki_title() -> tuple[str, str]:
    url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query&list=random&rnnamespace=0&rnlimit=1&format=json"
    )
    raw = fetch_text(url)
    data = json.loads(raw)
    title = data["query"]["random"][0]["title"]
    page_id = data["query"]["random"][0].get("id")
    return title, f"wikipedia:{page_id}"


def method5_index(n: int, locks: list[str], daily: bool, headline: str, salt: str | None) -> tuple[int, dict]:
    ts = utc_date() if daily else utc_now()
    if daily:
        used_salt = ""
    else:
        used_salt = salt if salt is not None else str(uuid.uuid4())
    msg = f"{ts}|{' | '.join(locks)}|{headline}|{used_salt}".encode("utf-8")
    digest = hashlib.sha256(msg).hexdigest()
    index = int(digest[:16], 16) % n
    meta = {
        "utc": ts,
        "digest16": digest[:16],
        "salt": used_salt,
        "headline": headline,
        "daily": daily,
    }
    return index, meta


def draw_index(n: int, method: str, locks: list[str], daily: bool, headline: str) -> tuple[int, str, dict]:
    """Returns index, method_used, raw_meta. Fallback 4 → 5 → 1."""
    order = [method]
    if method == "4":
        order = ["4", "5", "1"]
    elif method == "5":
        order = ["5", "1"]
    elif method == "3":
        order = ["3"]
    last_err = None
    for m in order:
        try:
            if m in ("1", "3"):
                i = method1_index(n)
                return i, m if method != "3" else "3", {"source": "secrets.randbelow"}
            if m == "4":
                i, note = method4_index(n)
                return i, "4", {"source": note}
            if m == "5":
                i, meta = method5_index(n, locks, daily, headline, None)
                return i, "5", meta
        except (URLError, HTTPError, TimeoutError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as e:
            last_err = e
            continue
    raise RuntimeError(f"oracle could not draw; last error: {last_err}")


def format_binding(payload: dict) -> str:
    lines = ["ORACLE BINDING"]
    lines.append(f"job: {payload['job']}")
    lines.append(f"default_method: {payload['default_method']}")
    lines.append(f"fallback_used: {payload['fallback_used']}")
    lines.append("locks:")
    if payload["locks"]:
        for lock in payload["locks"]:
            lines.append(f"  - {lock}")
    else:
        lines.append("  - (none)")
    lines.append("draws:")
    for slot, item in payload["draws"].items():
        lines.append(f"  {slot}: {item['value']}")
    lines.append("raw:")
    for slot, item in payload["draws"].items():
        raw = item["raw"]
        lines.append(
            f"  - {slot} index={raw.get('index', '-')} "
            f"menu={raw.get('menu', '-')} method={raw.get('method')} "
            f"source={raw.get('source', '-')}"
        )
    lines.append(f"timestamp: {payload['timestamp']}")
    lines.append("do_not_invent:")
    for x in payload.get("do_not_invent", []):
        lines.append(f"  - {x}")
    lines.append("")
    lines.append("After this block, build. Do not reopen the draws.")
    return "\n".join(lines)


def append_log(text: str) -> None:
    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(text)
        f.write("\n")


def cmd_draw(args: argparse.Namespace) -> int:
    schema = load_schema(args.job)
    job = schema.get("job", args.job)
    slots = schema["slots"]
    locks = list(args.lock or [])
    default_method = str(args.method)
    slot_methods = {}
    for pair in args.slot_method or []:
        if "=" not in pair:
            print(f"bad --slot-method {pair} (want hook=4)", file=sys.stderr)
            return 2
        k, v = pair.split("=", 1)
        slot_methods[k.strip()] = v.strip()

    draws = {}
    fallback_notes = []
    headline = args.headline or ""

    for name, spec in slots.items():
        required = spec.get("required", False)
        if not required and name not in slot_methods and name != "hook":
            if not args.all_optional:
                continue
        # hook is optional unless method 4 is default or slot-method says so
        method = slot_methods.get(name)
        if method is None:
            if name == "hook" and default_method != "4" and not args.force_hook:
                continue
            method = spec.get("method_hint") if name == "hook" and default_method == "3" else default_method
            if name == "hook" and method is None:
                method = "4"
            if method is None:
                method = default_method
        method = str(method)

        menu_name = spec.get("menu")
        if name == "hook" and method == "4":
            try:
                title, note = method4_wiki_title()
                draws[name] = {
                    "value": title,
                    "raw": {
                        "index": "-",
                        "menu": "wikipedia-random",
                        "method": "4",
                        "source": note,
                    },
                }
            except Exception as e:
                fallback_notes.append(f"hook:4 failed ({e}); used method 5 phrase")
                # method 5 against concrete nouns as a grounded-ish stand-in
                menu = load_menu("concrete_nouns.json")
                i, used, meta = draw_index(len(menu), "5", locks, args.daily, headline)
                draws[name] = {
                    "value": f"(wiki failed) object stand-in: {menu[i]}",
                    "raw": {
                        "index": i,
                        "menu": "concrete_nouns.json",
                        "method": used,
                        "source": meta,
                    },
                }
            continue

        if not menu_name:
            continue
        menu = load_menu(menu_name)
        requested = method
        i, used, meta = draw_index(len(menu), method, locks, args.daily, headline)
        if used != requested and requested == "4":
            fallback_notes.append(f"{name}: method 4 failed, used {used}")
        draws[name] = {
            "value": menu[i],
            "raw": {
                "index": i,
                "menu": menu_name,
                "method": used if requested != "3" else "3",
                "source": meta.get("source") or meta.get("digest16") or meta,
            },
        }

    payload = {
        "job": job,
        "default_method": default_method,
        "fallback_used": "; ".join(fallback_notes) if fallback_notes else "none",
        "locks": locks,
        "draws": draws,
        "timestamp": utc_now(),
        "do_not_invent": schema.get("do_not_invent", []),
    }
    block = format_binding(payload)
    print(block)
    try:
        append_log(block)
    except OSError:
        print("\n# could not write draws.log — keep the block above as the log", file=sys.stderr)
    return 0


def cmd_list_menus(_args: argparse.Namespace) -> int:
    for p in sorted(MENUS.glob("*.json")):
        items = load_json(p)
        print(f"{p.name:28} {len(items):3} items")
    return 0


def cmd_show_menu(args: argparse.Namespace) -> int:
    menu = load_menu(args.name if args.name.endswith(".json") else f"{args.name}.json")
    for i, item in enumerate(menu):
        print(f"{i:3}  {item}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Oracle box — draw slots the model may not pick.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("draw", help="draw a BINDING block for a job")
    d.add_argument("--job", required=True, choices=["website", "story", "design", "product", "generic"])
    d.add_argument("--method", default="3", choices=["1", "3", "4", "5"])
    d.add_argument("--lock", action="append", help='repeatable, e.g. --lock "character=Flash"')
    d.add_argument("--slot-method", action="append", help="per-slot method, e.g. hook=4 visual=3")
    d.add_argument("--daily", action="store_true", help="method 5: same locks + UTC date → same draws")
    d.add_argument("--headline", default="", help="optional extra entropy for method 5")
    d.add_argument("--force-hook", action="store_true", help="always draw a live hook")
    d.add_argument("--all-optional", action="store_true", help="also draw optional slots")
    d.set_defaults(func=cmd_draw)

    l = sub.add_parser("menus", help="list menus")
    l.set_defaults(func=cmd_list_menus)

    s = sub.add_parser("show", help="print a menu with indices")
    s.add_argument("name")
    s.set_defaults(func=cmd_show_menu)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
