#!/usr/bin/env python3
from pathlib import Path
import argparse
import re
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_component_boundary import find_function_component

DEFAULT_APP = "apps/web/src/App.jsx"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    parser.add_argument("--app", default=DEFAULT_APP)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    app_path = Path(args.app)
    text = app_path.read_text(encoding="utf-8")

    found = find_function_component(text, args.component)
    if not found:
        print(f"NOT FOUND: {args.component}")
        sys.exit(2)

    start, end = found
    chunk = text[start:end]

    outside = text[:start] + text[end:]
    refs = list(re.finditer(rf"\b{re.escape(args.component)}\b", outside))

    print(f"FUNCTION  : {args.component}")
    print(f"APP       : {app_path}")
    print(f"REFS_OUTSIDE_DECLARATION: {len(refs)}")
    print(f"MODE      : {'APPLY' if args.apply else 'DRY RUN'}")
    print()
    print("REMOVAL PREVIEW:")
    print("-" * 80)
    print("\n".join(chunk.splitlines()[:100]))
    print("-" * 80)

    if refs:
        print("ERROR: function still referenced outside its declaration. Not removing.", file=sys.stderr)
        sys.exit(3)

    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to remove.")
        return

    backup = app_path.with_suffix(app_path.suffix + ".bak.remove-" + args.component)
    shutil.copy2(app_path, backup)

    new_text = text[:start].rstrip() + "\n\n" + text[end:].lstrip()
    app_path.write_text(new_text, encoding="utf-8")

    print(f"UPDATED: {app_path}")
    print(f"BACKUP : {backup}")

if __name__ == "__main__":
    main()
