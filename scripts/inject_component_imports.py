#!/usr/bin/env python3
from pathlib import Path
import argparse
import re
import sys

KNOWN_COMPONENTS = [
    "ActionStat",
    "ExecutiveMetric",
    "ExecutiveStage",
    "EvidenceStat",
    "RiskStat",
    "ComplianceMetric",
    "ComplianceRelationBox",
    "DecisionList",
    "MetadataField",
    "BriefList",
    "RelationBox",
    "ResponseList",
    "ProposalList",
]

KNOWN_HELPERS = [
    "formatWibDateTime",
]

def has_jsx_tag(text, name):
    return bool(re.search(rf"<{re.escape(name)}(\s|>|/)", text))

def has_identifier_call_or_ref(text, name):
    return bool(re.search(rf"\b{re.escape(name)}\b", text))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--self-name", required=True)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    imports = []

    hook_names = []
    for hook in ["useState", "useEffect", "useMemo", "useCallback"]:
        if re.search(rf"\b{hook}\s*\(", text):
            hook_names.append(hook)

    if hook_names and 'from "react"' not in text and "from 'react'" not in text:
        imports.append(f'import {{ {", ".join(hook_names)} }} from "react";')

    for component in KNOWN_COMPONENTS:
        if component == args.self_name:
            continue
        if has_jsx_tag(text, component):
            import_line = f'import {component} from "./{component}.jsx";'
            if import_line not in text:
                imports.append(import_line)

    # For this batch, helper import is usually not needed.
    # Kept conservative: only warn, do not auto-import from App.jsx.
    helper_hits = []
    for helper in KNOWN_HELPERS:
        if has_identifier_call_or_ref(text, helper):
            helper_hits.append(helper)

    if imports:
        text = "\n".join(imports) + "\n\n" + text
        path.write_text(text, encoding="utf-8")
        print(f"UPDATED_IMPORTS: {path}")
        for line in imports:
            print(f"  + {line}")
    else:
        print(f"NO_IMPORTS_NEEDED: {path}")

    if helper_hits:
        print("WARNING_HELPER_REFERENCES:")
        for helper in helper_hits:
            print(f"  - {helper}")

if __name__ == "__main__":
    main()
