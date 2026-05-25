#!/usr/bin/env python3
from pathlib import Path
import shutil

APP = Path("apps/web/src/App.jsx")

DOWNLOADS = [
    {
        "endpoint": "/api/v1/projects/${selectedProjectId}/exports/checklist.xlsx",
        "filename": "bidready_ai_tender_report_project_${selectedProjectId}.xlsx",
        "message": "Readiness matrix exported.",
    },
    {
        "endpoint": "/api/v1/projects/${selectedProjectId}/exports/proposal-draft.docx",
        "filename": "bidready_ai_proposal_draft_project_${selectedProjectId}.docx",
        "message": "Proposal draft exported.",
    },
]

def ensure_download_import(text):
    if 'downloadApiFile' in text.split("function App()")[0]:
        return text

    if 'import { apiFetch } from "./api/client.js";' in text:
        return text.replace(
            'import { apiFetch } from "./api/client.js";',
            'import { apiFetch, downloadApiFile } from "./api/client.js";'
        )

    if 'import { apiFetch, downloadApiFile } from "./api/client.js";' in text:
        return text

    marker = 'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";'
    if marker in text:
        return text.replace(
            marker,
            marker + '\nimport { apiFetch, downloadApiFile } from "./api/client.js";'
        )

    raise RuntimeError("Could not find safe place to add downloadApiFile import")

def replace_download(text, endpoint, filename, message):
    fetch_pos = text.find(f"`{endpoint}`")
    if fetch_pos == -1:
        print(f"SKIP: endpoint not found or already migrated: {endpoint}")
        return text

    start = text.rfind("\n        const internalApiKey =", 0, fetch_pos)
    if start == -1:
        start = text.rfind("\n        const headers = new Headers", 0, fetch_pos)

    if start == -1:
        raise RuntimeError(f"Could not find block start for {endpoint}")

    message_line = f'        setMessage("{message}");'
    message_pos = text.find(message_line, fetch_pos)
    if message_pos == -1:
        raise RuntimeError(f"Could not find success message for {endpoint}")

    replacement = f'''
        await downloadApiFile(
          `{endpoint}`,
          `{filename}`
        );

'''

    print(f"REPLACE: {endpoint}")
    return text[:start] + replacement + text[message_pos:]

def main():
    text = APP.read_text(encoding="utf-8")
    backup = APP.with_suffix(".jsx.bak.remaining-download-fetches")
    shutil.copy2(APP, backup)
    print(f"BACKUP: {backup}")

    text = ensure_download_import(text)

    for item in DOWNLOADS:
        text = replace_download(
            text,
            item["endpoint"],
            item["filename"],
            item["message"],
        )

    APP.write_text(text, encoding="utf-8")
    print("UPDATED: apps/web/src/App.jsx")

if __name__ == "__main__":
    main()
