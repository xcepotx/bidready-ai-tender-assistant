#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys

APP = Path("apps/web/src/App.jsx")
HOOK = Path("apps/web/src/hooks/useTenderScoreRiskActionGenerators.js")

FUNCTIONS = [
    "generateComplianceScorecard",
    "generateRiskRegister",
    "generateActionItems",
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
    m = re.search(rf"(?m)^(?:  )?async\s+function\s+{re.escape(name)}\s*\(", text)
    if not m:
        raise RuntimeError(f"Function not found: {name}")

    start = m.start()
    paren_open = text.find("(", m.start())
    paren_close = scan_match(text, paren_open, "(", ")")
    brace_open = text.find("{", paren_close)
    brace_close = scan_match(text, brace_open, "{", "}")

    if paren_close < 0 or brace_open < 0 or brace_close < 0:
        raise RuntimeError(f"Could not parse function: {name}")

    end = brace_close + 1
    if text[end:end + 2] == "\n\n":
        end += 1

    chunk = text[start:brace_close + 1]
    if chunk.startswith("async function "):
        chunk = "  " + chunk

    return start, end, chunk

def parse_hook_call_end(text, hook_name):
    call_start = text.find(f"{hook_name}(")
    if call_start == -1:
        raise RuntimeError(f"Hook call not found: {hook_name}")

    paren_open = text.find("(", call_start)
    paren_close = scan_match(text, paren_open, "(", ")")

    if paren_close < 0:
        raise RuntimeError(f"Could not parse hook call: {hook_name}")

    end = paren_close + 1
    if end < len(text) and text[end] == ";":
        end += 1
    if end < len(text) and text[end] == "\n":
        end += 1

    return end

def assert_no_broken_async(text):
    bad = re.search(r"(?m)^[ \t]*(ync|sync)\s+function\s+", text)
    if bad:
        line = text[:bad.start()].count("\n") + 1
        raise RuntimeError(f"Broken async prefix would be created around line {line}: {bad.group(0).strip()}")

def main():
    text = APP.read_text(encoding="utf-8")

    app_backup = APP.with_suffix(".jsx.bak.extract-score-risk-action-generator-handlers-hook")
    shutil.copy2(APP, app_backup)
    print(f"BACKUP: {app_backup}")

    found = []
    for name in FUNCTIONS:
        found.append((name, *find_async_function(text, name)))

    hook_body = "\n\n".join(chunk for _, _, _, chunk in found)

    hook_text = f'''import {{ apiFetch }} from "../api/client.js";

export function useTenderScoreRiskActionGenerators({{
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setActiveProjectView,
  setComplianceScorecard,
  setRiskItems,
  setActionItems,
}}) {{
{hook_body}

  return {{
    generateComplianceScorecard,
    generateRiskRegister,
    generateActionItems,
  }};
}}
'''

    new_text = text

    for name, start, end, chunk in sorted(found, key=lambda item: item[1], reverse=True):
        print(f"REMOVE from App.jsx: {name}")
        new_text = new_text[:start].rstrip() + "\n\n" + new_text[end:]

    if 'import { useTenderScoreRiskActionGenerators } from "./hooks/useTenderScoreRiskActionGenerators.js";' not in new_text:
        new_text = new_text.replace(
            'import { useTenderScoreRiskActionUpdates } from "./hooks/useTenderScoreRiskActionUpdates.js";',
            'import { useTenderScoreRiskActionUpdates } from "./hooks/useTenderScoreRiskActionUpdates.js";\nimport { useTenderScoreRiskActionGenerators } from "./hooks/useTenderScoreRiskActionGenerators.js";'
        )

    hook_call = '''
  const {
    generateComplianceScorecard,
    generateRiskRegister,
    generateActionItems,
  } = useTenderScoreRiskActionGenerators({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setActiveProjectView,
    setComplianceScorecard,
    setRiskItems,
    setActionItems,
  });
'''

    if "useTenderScoreRiskActionGenerators({" not in new_text:
        insert_at = parse_hook_call_end(new_text, "useTenderScoreRiskActionUpdates")
        new_text = new_text[:insert_at] + hook_call + new_text[insert_at:]

    assert_no_broken_async(new_text)

    HOOK.parent.mkdir(parents=True, exist_ok=True)
    HOOK.write_text(hook_text, encoding="utf-8")
    APP.write_text(new_text, encoding="utf-8")

    print(f"WROTE: {HOOK}")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
