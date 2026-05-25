#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_component_boundary import find_function_component

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("function_name")
    parser.add_argument("--source", default="apps/web/src/App.jsx")
    parser.add_argument("--target", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    target = Path(args.target)

    text = source.read_text(encoding="utf-8")
    found = find_function_component(text, args.function_name)

    if not found:
        print(f"ERROR: function not found: {args.function_name}", file=sys.stderr)
        sys.exit(2)

    start, end = found
    chunk = text[start:end]

    if chunk.startswith("export "):
        exported = chunk
    else:
        exported = "export " + chunk

    print(f"FUNCTION: {args.function_name}")
    print(f"SOURCE  : {source}")
    print(f"TARGET  : {target}")
    print(f"MODE    : {'APPLY' if args.apply else 'DRY RUN'}")
    print()
    print("UTIL PREVIEW:")
    print("-" * 80)
    print(exported)
    print("-" * 80)

    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to write util.")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(exported + "\n", encoding="utf-8")
    print(f"WROTE: {target}")

if __name__ == "__main__":
    main()
