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

def remove_function(text, name):
    m = re.search(rf"\n[ \t]*(async\s+)?function\s+{re.escape(name)}\s*\(", text)
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

    print(f"REMOVE function: {name}")
    return text[:start].rstrip() + "\n\n" + text[end:].lstrip()

def main():
    text = APP.read_text(encoding="utf-8")

    backup = APP.with_suffix(".jsx.bak.extract-auth-session-hook")
    shutil.copy2(APP, backup)
    print(f"BACKUP: {backup}")

    text = text.replace(
        'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";\n',
        ''
    )

    if 'import { useAuthSession } from "./hooks/useAuthSession.js";' not in text:
        text = text.replace(
            'import { apiFetch, downloadApiFile } from "./api/client.js";',
            'import { apiFetch, downloadApiFile } from "./api/client.js";\nimport { useAuthSession } from "./hooks/useAuthSession.js";'
        )

    state_block = '''  const [authUser, setAuthUser] = useState(() => getStoredAuthUser());
  const [authToken, setAuthToken] = useState(() => getStoredAuthToken());
  const [authForm, setAuthForm] = useState({ email: "admin@bidready.local", password: "" });'''

    replacement = '''  const {
    authUser,
    authToken,
    authForm,
    setAuthForm,
    loginWithPassword,
    logoutUser,
  } = useAuthSession({ setBusy, setMessage, setActorName });'''

    if state_block not in text:
        raise RuntimeError("Auth state block not found")

    text = text.replace(state_block, replacement)

    text = remove_function(text, "loginWithPassword")
    text = remove_function(text, "logoutUser")

    APP.write_text(text, encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
