#!/usr/bin/env python3
from pathlib import Path
import re
import shutil

APP = Path("apps/web/src/App.jsx")
HOOK = Path("apps/web/src/hooks/useTenderSimpleUpdates.js")

FUNCTIONS = [
    "updateRequirement",
    "updateClarification",
]

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

def find_async_function(text, name):
    m = re.search(rf"\n[ \t]*async\s+function\s+{re.escape(name)}\s*\(", text)
    if not m:
        raise RuntimeError(f"Function not found: {name}")

    start = m.start() + 1
    paren_open = text.find("(", m.start())
    paren_close = scan_match(text, paren_open, "(", ")")
    brace_open = text.find("{", paren_close)
    brace_close = scan_match(text, brace_open, "{", "}")

    if paren_close < 0 or brace_open < 0 or brace_close < 0:
        raise RuntimeError(f"Could not parse function: {name}")

    end = brace_close + 1
    while end < len(text) and text[end] in " \t\r\n":
        end += 1

    return start, end, text[start:brace_close + 1]

def insert_after_hook_block(text, hook_name, insertion):
    marker = f"  }} = {hook_name}({{"
    start = text.find(marker)
    if start == -1:
        raise RuntimeError(f"Could not find hook block: {hook_name}")

    # Find the opening parenthesis in the hook call.
    call_start = text.find(f"{hook_name}(", start)
    paren_open = text.find("(", call_start)
    paren_close = scan_match(text, paren_open, "(", ")")
    if paren_close < 0:
        raise RuntimeError(f"Could not parse hook call: {hook_name}")

    end = paren_close + 1
    if end < len(text) and text[end] == ";":
        end += 1

    while end < len(text) and text[end] in " \t":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1

    return text[:end] + insertion + text[end:]

def main():
    text = APP.read_text(encoding="utf-8")

    app_backup = APP.with_suffix(".jsx.bak.extract-simple-update-handlers-hook")
    shutil.copy2(APP, app_backup)
    print(f"BACKUP: {app_backup}")

    found = []
    for name in FUNCTIONS:
        found.append((name, *find_async_function(text, name)))

    hook_body = "\n\n".join(chunk for _, _, _, chunk in found)

    hook_text = f'''import {{ apiFetch }} from "../api/client.js";

export function useTenderSimpleUpdates({{
  selectedProjectId,
  setBusy,
  setMessage,
  setSelectedRequirementId,
  setSelectedClarificationId,
  loadProjectData,
}}) {{
{hook_body}

  return {{
    updateRequirement,
    updateClarification,
  }};
}}
'''

    HOOK.parent.mkdir(parents=True, exist_ok=True)
    HOOK.write_text(hook_text, encoding="utf-8")
    print(f"WROTE: {HOOK}")

    for name, start, end, chunk in sorted(found, key=lambda item: item[1], reverse=True):
        print(f"REMOVE from App.jsx: {name}")
        text = text[:start].rstrip() + "\n\n" + text[end:].lstrip()

    if 'import { useTenderSimpleUpdates } from "./hooks/useTenderSimpleUpdates.js";' not in text:
        text = text.replace(
            'import { useTenderDownloads } from "./hooks/useTenderDownloads.js";',
            'import { useTenderDownloads } from "./hooks/useTenderDownloads.js";\nimport { useTenderSimpleUpdates } from "./hooks/useTenderSimpleUpdates.js";'
        )

    hook_call = '''
  const {
    updateRequirement,
    updateClarification,
  } = useTenderSimpleUpdates({
    selectedProjectId,
    setBusy,
    setMessage,
    setSelectedRequirementId,
    setSelectedClarificationId,
    loadProjectData,
  });
'''

    if "useTenderSimpleUpdates({" not in text:
        if "useTenderDownloads({" in text:
            text = insert_after_hook_block(text, "useTenderDownloads", hook_call)
        else:
            raise RuntimeError("useTenderDownloads hook not found for insertion point")

    APP.write_text(text, encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
