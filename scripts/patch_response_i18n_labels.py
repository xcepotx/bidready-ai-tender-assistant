#!/usr/bin/env python3
from pathlib import Path
import shutil

FILES = [
    Path("apps/web/src/views/ResponsePlanView.jsx"),
    Path("apps/web/src/components/ResponseItemDetail.jsx"),
    Path("apps/web/src/components/ResponseList.jsx"),
]

REPLACEMENTS = {
    # View heading / descriptions
    "Response Plan": 'Rencana Respons',
    "Convert reviewed requirements into compliance status, response strategy, draft response, and evidence checklist.": "Konversi requirement yang sudah direview menjadi status kepatuhan, strategi respons, draft respons, dan checklist evidence.",
    "Search requirement, draft response, owner, category, or compliance": "Cari requirement, draft respons, owner, kategori, atau kepatuhan",
    "All compliance": "Semua kepatuhan",
    "All statuses": "Semua status",

    # Detail labels
    "Response Item": "Item Respons",
    "Requirement Evidence": "Evidence Requirement",
    "Compliance": "Kepatuhan",
    "Status": "Status",
    "Owner": "Owner",
    "Category": "Kategori",
    "Mode": "Mode",
    "Response Strategy": "Strategi Respons",
    "Draft Response": "Draft Respons",
    "Evidence Checklist": "Checklist Evidence",
    "Notes": "Catatan",
    "No response item selected.": "Belum ada item respons yang dipilih.",
    "Generate response plan first.": "Generate rencana respons terlebih dahulu.",
}

def ensure_l_import(path, text):
    if "L(" not in text:
        return text

    if "../utils/i18n.js" in text or "./utils/i18n.js" in text:
        return text

    lines = text.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("import "):
            insert_at = i + 1

    import_line = 'import { L } from "../utils/i18n.js";\n'
    return "".join(lines[:insert_at]) + import_line + "".join(lines[insert_at:])

def wrap_plain_text(text, en, id_text):
    # JSX text: >English<
    text = text.replace(f">{en}<", f">{{L(\"{en}\", \"{id_text}\")}}<")

    # common attributes: placeholder="English", title="English", aria-label="English"
    text = text.replace(f'placeholder="{en}"', f'placeholder={{L("{en}", "{id_text}")}}')
    text = text.replace(f'title="{en}"', f'title={{L("{en}", "{id_text}")}}')
    text = text.replace(f'aria-label="{en}"', f'aria-label={{L("{en}", "{id_text}")}}')

    return text

def main():
    changed = []

    for path in FILES:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        original = text

        for en, id_text in REPLACEMENTS.items():
            text = wrap_plain_text(text, en, id_text)

        if text != original:
            backup = path.with_suffix(path.suffix + ".bak.response-i18n")
            shutil.copy2(path, backup)
            text = ensure_l_import(path, text)
            path.write_text(text, encoding="utf-8")
            changed.append(path)

    if not changed:
        print("NO CHANGES. The labels may use a different structure. Send grep output.")
        return

    print("UPDATED:")
    for path in changed:
        print("-", path)

if __name__ == "__main__":
    main()
