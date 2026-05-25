#!/usr/bin/env python3
from pathlib import Path
import re
import shutil

SRC = Path("apps/web/src")

KNOWN_COMPONENTS = {
    "ActionStat": "components/ActionStat.jsx",
    "ExecutiveMetric": "components/ExecutiveMetric.jsx",
    "ExecutiveStage": "components/ExecutiveStage.jsx",
    "EvidenceStat": "components/EvidenceStat.jsx",
    "RiskStat": "components/RiskStat.jsx",
    "ComplianceMetric": "components/ComplianceMetric.jsx",
    "ComplianceRelationBox": "components/ComplianceRelationBox.jsx",
    "DecisionList": "components/DecisionList.jsx",
    "MetadataField": "components/MetadataField.jsx",
    "BriefList": "components/BriefList.jsx",
    "RelationBox": "components/RelationBox.jsx",
    "ResponseList": "components/ResponseList.jsx",
    "ProposalList": "components/ProposalList.jsx",
    "ResponseItemDetail": "components/ResponseItemDetail.jsx",
    "ProposalSectionDetail": "components/ProposalSectionDetail.jsx",
    "EvidenceItemDetail": "components/EvidenceItemDetail.jsx",
    "ActionItemCard": "components/ActionItemCard.jsx",
    "DecisionGateCard": "components/DecisionGateCard.jsx",
    "RfpMetadataCard": "components/RfpMetadataCard.jsx",
    "BidBriefCard": "components/BidBriefCard.jsx",
    "ReadinessSummaryCard": "components/ReadinessSummaryCard.jsx",
}

def rel_import(from_file, target_rel):
    target = SRC / target_rel
    rel = target.relative_to(from_file.parent) if False else None

    # Manual relative path keeps output predictable.
    if from_file.name == "App.jsx":
        return f"./{target_rel}"

    if from_file.parent == SRC / "views":
        return f"../{target_rel}"

    if from_file.parent == SRC / "components":
        target_name = Path(target_rel).name
        return f"./{target_name}"

    return f"./{target_rel}"

def has_local_definition(text, name):
    return bool(re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", text))

def has_import(text, name):
    return bool(re.search(rf"import\s+{re.escape(name)}\s+from\s+[\"']", text))

def uses_jsx(text, name):
    return bool(re.search(rf"<{re.escape(name)}(\s|>|/)", text))

def insert_imports(text, import_lines):
    lines = text.splitlines(True)
    insert_at = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import "):
            insert_at = i + 1
            continue

        if stripped == "":
            continue

        if insert_at:
            break

    payload = "".join(import_lines)
    return "".join(lines[:insert_at]) + payload + "".join(lines[insert_at:])

def main():
    changed = []

    files = [SRC / "App.jsx"]
    files += list((SRC / "views").glob("*.jsx"))
    files += list((SRC / "components").glob("*.jsx"))

    for path in files:
        if not path.exists() or ".bak" in path.name:
            continue

        text = path.read_text(encoding="utf-8")
        import_lines = []

        for name, target_rel in KNOWN_COMPONENTS.items():
            # Don't import itself.
            if path.name == Path(target_rel).name:
                continue

            if uses_jsx(text, name) and not has_local_definition(text, name) and not has_import(text, name):
                import_path = rel_import(path, target_rel)
                import_lines.append(f'import {name} from "{import_path}";\n')

        if import_lines:
            backup = path.with_suffix(path.suffix + ".bak.fix-missing-component-imports")
            shutil.copy2(path, backup)
            path.write_text(insert_imports(text, import_lines), encoding="utf-8")
            changed.append((path, import_lines))

    if not changed:
        print("NO missing extracted component imports found.")
        return

    print("UPDATED files:")
    for path, imports in changed:
        print(f"- {path}")
        for line in imports:
            print(f"  + {line.strip()}")

if __name__ == "__main__":
    main()
