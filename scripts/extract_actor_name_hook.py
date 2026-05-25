#!/usr/bin/env python3
from pathlib import Path
import re
import shutil

APP = Path("apps/web/src/App.jsx")

def scan_match(text, open_pos, open_ch, close_ch):
    depth = 0
    i = open_pos
    n = len(text)
    state = "code"
    quote = None
    escaped = False

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if state == "line_comment":
            if ch == "\n":
                state = "code"
            i += 1
            continue

        if state == "block_comment":
            if ch == "*" and nxt == "/":
                state = "code"
                i += 2
            else:
                i += 1
            continue

        if state == "string":
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                state = "code"
                quote = None
            i += 1
            continue

        if state == "template":
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == "`":
                state = "code"
            i += 1
            continue

        if ch == "/" and nxt == "/":
            state = "line_comment"
            i += 2
            continue

        if ch == "/" and nxt == "*":
            state = "block_comment"
            i += 2
            continue

        if ch in ("'", '"'):
            state = "string"
            quote = ch
            i += 1
            continue

        if ch == "`":
            state = "template"
            i += 1
            continue

        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return -1

def remove_use_effect_containing(text, needle):
    marker = "useEffect("
    pos = text.find(needle)

    if pos == -1:
        print(f"SKIP useEffect removal: needle not found: {needle}")
        return text

    start = text.rfind(marker, 0, pos)
    if start == -1:
        raise RuntimeError(f"Could not find useEffect start for {needle}")

    line_start = text.rfind("\n", 0, start) + 1
    paren_open = text.find("(", start)
    paren_close = scan_match(text, paren_open, "(", ")")

    if paren_close < 0:
        raise RuntimeError(f"Could not parse useEffect for {needle}")

    end = paren_close + 1

    if end < len(text) and text[end] == ";":
        end += 1

    while end < len(text) and text[end] in " \t\r\n":
        end += 1

    print(f"REMOVE useEffect containing: {needle}")
    return text[:line_start].rstrip() + "\n\n" + text[end:].lstrip()

def main():
    text = APP.read_text(encoding="utf-8")

    backup = APP.with_suffix(".jsx.bak.extract-actor-name-hook")
    shutil.copy2(APP, backup)
    print(f"BACKUP: {backup}")

    if 'import { useActorName } from "./hooks/useActorName.js";' not in text:
        text = text.replace(
            'import { useAuthSession } from "./hooks/useAuthSession.js";',
            'import { useAuthSession } from "./hooks/useAuthSession.js";\nimport { useActorName } from "./hooks/useActorName.js";'
        )

    actor_state_block = '''  const [actorName, setActorName] = useState(() => {
    return window.localStorage.getItem("bra_actor") || "bid_manager";
  });'''

    if actor_state_block not in text:
        raise RuntimeError("actorName state block not found")

    text = text.replace(
        actor_state_block,
        '  const [actorName, setActorName] = useActorName();'
    )

    text = remove_use_effect_containing(
        text,
        'window.localStorage.setItem("bra_actor", actorName);'
    )

    APP.write_text(text, encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
