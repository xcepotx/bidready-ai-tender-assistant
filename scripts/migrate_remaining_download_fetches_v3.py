#!/usr/bin/env python3
from pathlib import Path
import shutil

APP = Path("apps/web/src/App.jsx")

DOWNLOADS = [
    {
        "endpoint": "/api/v1/projects/${selectedProjectId}/exports/checklist.xlsx",
        "filename": "bidready_ai_tender_report_project_${selectedProjectId}.xlsx",
        "message": 'setMessage("Readiness matrix exported.");',
    },
    {
        "endpoint": "/api/v1/projects/${selectedProjectId}/exports/proposal-draft.docx",
        "filename": "bidready_ai_proposal_draft_project_${selectedProjectId}.docx",
        "message": 'setMessage("Proposal draft exported.");',
    },
]

def ensure_import(lines):
    joined = "".join(lines)

    if 'import { apiFetch, downloadApiFile } from "./api/client.js";' in joined:
        print("SKIP import: already has apiFetch + downloadApiFile")
        return lines

    if 'import { apiFetch } from "./api/client.js";' in joined:
        print("UPDATE import: add downloadApiFile")
        return [
            line.replace(
                'import { apiFetch } from "./api/client.js";',
                'import { apiFetch, downloadApiFile } from "./api/client.js";'
            )
            for line in lines
        ]

    raise RuntimeError("api client import not found. Expected apiFetch import first.")

def replace_one(lines, endpoint, filename, message_line):
    fetch_idx = None

    for i, line in enumerate(lines):
        if "const res = await fetch(" in line and endpoint in line:
            fetch_idx = i
            break

    if fetch_idx is None:
        print(f"SKIP: fetch not found, maybe already migrated: {endpoint}")
        return lines

    start_idx = fetch_idx

    # Include stale header setup immediately above fetch if present.
    for j in range(fetch_idx - 1, max(-1, fetch_idx - 12), -1):
        stripped = lines[j].strip()
        if stripped.startswith("const internalApiKey ="):
            start_idx = j
            break

    msg_idx = None
    for k in range(fetch_idx, min(len(lines), fetch_idx + 40)):
        if message_line in lines[k]:
            msg_idx = k
            break

    if msg_idx is None:
        raise RuntimeError(f"Success message not found for {endpoint}")

    replacement = [
        "        await downloadApiFile(\n",
        f"          `{endpoint}`,\n",
        f"          `{filename}`\n",
        "        );\n",
        "\n",
    ]

    print(f"REPLACE lines {start_idx + 1}-{msg_idx}: {endpoint}")
    return lines[:start_idx] + replacement + lines[msg_idx:]

def main():
    lines = APP.read_text(encoding="utf-8").splitlines(True)

    backup = APP.with_suffix(".jsx.bak.remaining-download-fetches-v3")
    shutil.copy2(APP, backup)
    print(f"BACKUP: {backup}")

    lines = ensure_import(lines)

    for item in DOWNLOADS:
        lines = replace_one(
            lines,
            item["endpoint"],
            item["filename"],
            item["message"],
        )

    APP.write_text("".join(lines), encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
