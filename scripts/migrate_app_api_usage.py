#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys

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

def remove_local_async_function(text, name):
    pattern = re.compile(rf"\n[ \t]*async\s+function\s+{re.escape(name)}\s*\(")
    m = pattern.search(text)
    if not m:
        print(f"SKIP remove {name}: not found")
        return text, False

    fn_start = m.start() + 1
    paren_open = text.find("(", m.start())
    paren_close = scan_match(text, paren_open, "(", ")")
    if paren_close == -1:
        raise RuntimeError(f"Could not match params for {name}")

    brace_open = text.find("{", paren_close)
    if brace_open == -1:
        raise RuntimeError(f"Could not find body for {name}")

    brace_close = scan_match(text, brace_open, "{", "}")
    if brace_close == -1:
        raise RuntimeError(f"Could not match body for {name}")

    remove_end = brace_close + 1
    while remove_end < len(text) and text[remove_end] in " \t\r\n":
        remove_end += 1

    print(f"REMOVE local async function: {name}")
    return text[:fn_start].rstrip() + "\n\n" + text[remove_end:].lstrip(), True

def ensure_imports(text):
    old = 'import { getStoredAuthToken, getStoredAuthUser, buildAuthHeaders } from "./utils/auth.js";'
    new = 'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";\nimport { apiFetch, downloadApiFile } from "./api/client.js";'

    if old in text:
        text = text.replace(old, new)
        print("UPDATED auth/client imports")
        return text

    if 'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";' in text and './api/client.js' not in text:
        text = text.replace(
            'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";',
            'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";\nimport { apiFetch, downloadApiFile } from "./api/client.js";'
        )
        print("ADDED api client import")
        return text

    print("SKIP imports: already updated or unexpected")
    return text

def replace_create_project_headers(text):
    before = text
    text = re.sub(
        r'headers:\s*\{\s*\.\.\.buildAuthHeaders\(\),\s*"Content-Type":\s*"application/json"\s*\}',
        'headers: { "Content-Type": "application/json" }',
        text,
        count=1,
        flags=re.S,
    )
    if text != before:
        print("UPDATED createProject JSON headers")
    else:
        print("SKIP createProject headers: pattern not found or already updated")
    return text

def replace_download_block(text, endpoint_suffix, filename_template, success_message):
    occurrence = text.find(endpoint_suffix)
    if occurrence == -1:
        print(f"SKIP download block {endpoint_suffix}: endpoint not found")
        return text, False

    start = text.rfind("\n        const internalApiKey =", 0, occurrence)
    if start == -1:
        print(f"SKIP download block {endpoint_suffix}: internalApiKey start not found, maybe already migrated")
        return text, False

    end_marker = f'\n\n        setMessage("{success_message}");'
    end = text.find(end_marker, occurrence)
    if end == -1:
        raise RuntimeError(f"Could not find success message end for {endpoint_suffix}")

    replacement = f'''
        await downloadApiFile(
          `{endpoint_suffix}`,
          `{filename_template}`
        );'''

    print(f"UPDATED download block: {endpoint_suffix}")
    return text[:start] + replacement + text[end:], True

def main():
    if not APP.exists():
        raise SystemExit(f"Not found: {APP}")

    text = APP.read_text(encoding="utf-8")
    original = text

    backup = APP.with_suffix(".jsx.bak.migrate-api-client")
    shutil.copy2(APP, backup)
    print(f"BACKUP: {backup}")

    text = ensure_imports(text)

    text, _ = remove_local_async_function(text, "downloadApiFile")
    text, _ = remove_local_async_function(text, "apiFetch")

    text = replace_create_project_headers(text)

    text, _ = replace_download_block(
        text,
        "/api/v1/projects/${selectedProjectId}/exports/checklist.xlsx",
        "bidready_ai_tender_report_project_${selectedProjectId}.xlsx",
        "Readiness matrix exported.",
    )

    text, _ = replace_download_block(
        text,
        "/api/v1/projects/${selectedProjectId}/exports/proposal-draft.docx",
        "bidready_ai_proposal_draft_project_${selectedProjectId}.docx",
        "Proposal draft exported.",
    )

    if text == original:
        print("NO CHANGE made to App.jsx")
        return

    APP.write_text(text, encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
