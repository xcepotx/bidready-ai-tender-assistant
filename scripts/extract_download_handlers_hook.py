#!/usr/bin/env python3
from pathlib import Path
import re
import shutil

APP = Path("apps/web/src/App.jsx")
HOOK = Path("apps/web/src/hooks/useTenderDownloads.js")

FUNCTIONS = [
    "downloadReadinessMatrix",
    "downloadProposalDraft",
    "downloadExecutivePack",
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

def main():
    text = APP.read_text(encoding="utf-8")

    app_backup = APP.with_suffix(".jsx.bak.extract-download-handlers-hook")
    shutil.copy2(APP, app_backup)
    print(f"BACKUP: {app_backup}")

    found = []
    for name in FUNCTIONS:
        found.append((name, *find_async_function(text, name)))

    hook_body = "\n\n".join(chunk for _, _, _, chunk in found)

    hook_text = f'''import {{ downloadApiFile }} from "../api/client.js";

export function useTenderDownloads({{
  selectedProjectId,
  requirements,
  proposalOutline,
  setBusy,
  setMessage,
}}) {{
{hook_body}

  return {{
    downloadReadinessMatrix,
    downloadProposalDraft,
    downloadExecutivePack,
  }};
}}
'''

    HOOK.parent.mkdir(parents=True, exist_ok=True)
    HOOK.write_text(hook_text, encoding="utf-8")
    print(f"WROTE: {HOOK}")

    # Remove functions from App.jsx from bottom to top.
    for name, start, end, chunk in sorted(found, key=lambda item: item[1], reverse=True):
        print(f"REMOVE from App.jsx: {name}")
        text = text[:start].rstrip() + "\n\n" + text[end:].lstrip()

    # Remove downloadApiFile import from App.jsx if present.
    text = text.replace(
        'import { apiFetch, downloadApiFile } from "./api/client.js";',
        'import { apiFetch } from "./api/client.js";'
    )

    # Add hook import.
    if 'import { useTenderDownloads } from "./hooks/useTenderDownloads.js";' not in text:
        text = text.replace(
            'import { useActorName } from "./hooks/useActorName.js";',
            'import { useActorName } from "./hooks/useActorName.js";\nimport { useTenderDownloads } from "./hooks/useTenderDownloads.js";'
        )

    insert_after = '''  const {
    authUser,
    authToken,
    authForm,
    setAuthForm,
    loginWithPassword,
    logoutUser,
  } = useAuthSession({ setBusy, setMessage, setActorName });
'''

    hook_call = '''
  const {
    downloadReadinessMatrix,
    downloadProposalDraft,
    downloadExecutivePack,
  } = useTenderDownloads({
    selectedProjectId,
    requirements,
    proposalOutline,
    setBusy,
    setMessage,
  });
'''

    if insert_after not in text:
        raise RuntimeError("Could not find useAuthSession block for insertion")

    if "useTenderDownloads({" not in text:
        text = text.replace(insert_after, insert_after + hook_call)

    APP.write_text(text, encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
