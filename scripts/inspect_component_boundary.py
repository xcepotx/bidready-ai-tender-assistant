#!/usr/bin/env python3
from pathlib import Path
import argparse
import re
import sys

DEFAULT_APP = "apps/web/src/App.jsx"

def line_no(text, pos):
    return text.count("\n", 0, pos) + 1

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

        # code state
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

def find_function_component(text, name):
    # Supports:
    # function ComponentName(...) {
    pattern = re.compile(rf"(^|\n)(function\s+{re.escape(name)}\s*\()", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return None

    fn_start = m.start(2)
    paren_open = text.find("(", fn_start)
    if paren_open == -1:
        raise RuntimeError("Function opening parenthesis not found")

    paren_close = scan_match(text, paren_open, "(", ")")
    if paren_close == -1:
        raise RuntimeError("Function parameter closing parenthesis not found")

    i = paren_close + 1
    while i < len(text) and text[i].isspace():
        i += 1

    if i >= len(text) or text[i] != "{":
        raise RuntimeError(f"Expected function body '{{' after line {line_no(text, paren_close)}")

    brace_open = i
    brace_close = scan_match(text, brace_open, "{", "}")
    if brace_close == -1:
        raise RuntimeError("Function body closing brace not found")

    return fn_start, brace_close + 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("component", help="Component/function name, e.g. AuditLogView")
    parser.add_argument("--app", default=DEFAULT_APP)
    parser.add_argument("--out", default=None, help="Optional path to write extracted preview")
    args = parser.parse_args()

    app_path = Path(args.app)
    if not app_path.exists():
        print(f"ERROR: not found: {app_path}", file=sys.stderr)
        sys.exit(1)

    text = app_path.read_text(encoding="utf-8")
    found = find_function_component(text, args.component)

    if not found:
        print(f"NOT FOUND: function {args.component}(...) in {app_path}")
        sys.exit(2)

    start, end = found
    chunk = text[start:end]

    start_line = line_no(text, start)
    end_line = line_no(text, end)

    print(f"FOUND: {args.component}")
    print(f"FILE : {app_path}")
    print(f"LINES: {start_line}-{end_line}")
    print(f"CHARS: {start}-{end}")
    print(f"SIZE : {len(chunk)} chars")
    print(f"HAS_RETURN_PAREN: {'YES' if 'return (' in chunk else 'NO'}")
    print(f"HAS_EXPORT_DEFAULT_INSIDE: {'YES' if 'export default' in chunk else 'NO'}")
    print()

    print("FIRST 20 LINES:")
    print("-" * 80)
    for line in chunk.splitlines()[:20]:
        print(line)

    print("-" * 80)
    print("LAST 20 LINES:")
    print("-" * 80)
    for line in chunk.splitlines()[-20:]:
        print(line)
    print("-" * 80)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(chunk + "\n", encoding="utf-8")
        print(f"PREVIEW_WRITTEN: {out_path}")

if __name__ == "__main__":
    main()
