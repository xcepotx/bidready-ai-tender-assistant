#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_component_boundary import find_function_component

DEFAULT_APP = "apps/web/src/App.jsx"

def find_import_insert_pos(text):
    lines = text.splitlines(True)
    pos = 0
    last_import_end = 0

    for line in lines:
        stripped = line.strip()
        line_len = len(line)

        if stripped.startswith("import "):
            last_import_end = pos + line_len

        pos += line_len

        if stripped and not stripped.startswith("import "):
            break

    return last_import_end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    parser.add_argument("--app", default=DEFAULT_APP)
    parser.add_argument("--target", required=True)
    parser.add_argument("--import-path", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    app_path = Path(args.app)
    target_path = Path(args.target)

    if not app_path.exists():
        print(f"ERROR: App file not found: {app_path}", file=sys.stderr)
        sys.exit(1)

    text = app_path.read_text(encoding="utf-8")
    found = find_function_component(text, args.component)

    if not found:
        print(f"ERROR: function {args.component}(...) not found", file=sys.stderr)
        sys.exit(2)

    start, end = found
    chunk = text[start:end]

    if "return (" not in chunk:
        print("ERROR: extracted component does not contain 'return ('", file=sys.stderr)
        sys.exit(3)

    if "export default" in chunk:
        print("ERROR: extracted component already contains export default", file=sys.stderr)
        sys.exit(4)

    import_line = f'import {args.component} from "{args.import_path}";\n'

    if import_line in text:
        print("ERROR: import already exists in App.jsx", file=sys.stderr)
        sys.exit(5)

    new_component = "export default " + chunk + "\n"

    # remove component block from App.jsx
    new_text = text[:start].rstrip() + "\n\n" + text[end:].lstrip()

    # add import
    insert_pos = find_import_insert_pos(new_text)
    if insert_pos <= 0:
        new_text = import_line + new_text
    else:
        new_text = new_text[:insert_pos] + import_line + new_text[insert_pos:]

    print(f"COMPONENT : {args.component}")
    print(f"TARGET    : {target_path}")
    print(f"IMPORT    : {import_line.strip()}")
    print(f"APP       : {app_path}")
    print(f"MODE      : {'APPLY' if args.apply else 'DRY RUN'}")
    print()
    print("EXTRACT PREVIEW:")
    print("-" * 80)
    print("\n".join(new_component.splitlines()[:30]))
    print("-" * 80)

    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to write files.")
        return

    backup_path = app_path.with_suffix(app_path.suffix + ".bak.extract-" + args.component)

    shutil.copy2(app_path, backup_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    app_path.write_text(new_text, encoding="utf-8")
    target_path.write_text(new_component, encoding="utf-8")

    print(f"WROTE     : {target_path}")
    print(f"UPDATED   : {app_path}")
    print(f"BACKUP    : {backup_path}")

if __name__ == "__main__":
    main()
