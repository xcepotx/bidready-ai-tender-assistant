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
    if './api/client.js' in text and 'downloadApiFile' in text.split('function App()')[0]:
        print("SKIP import: downloadApiFile already imported")
        return text

    if 'import { apiFetch } from "./api/client.js";' in text:
        print("UPDATE import: add downloadApiFile")
        return text.replace(
            'import { apiFetch } from "./api/client.js";',
            'import { apiFetch, downloadApiFile } from "./api/client.js";'
        )

    if 'import { apiFetch, downloadApiFile } from "./api/client.js";' in text:
        print("SKIP import: already complete")
        return text

    marker = 'import { getStoredAuthToken, getStoredAuthUser } from "./utils/auth.js";'
    if marker in text:
        print("ADD import: apiFetch, downloadApiFile")
        return text.replace(
            marker,
            marker + '\nimport { apiFetch, downloadApiFile } from "./api/client.js";'
        )

    raise RuntimeError("Could not find safe import location")

def cleanup_preceding_header_setup(text, fetch_start):
    """
    Remove optional stale header setup immediately before const res = await fetch:
      const internalApiKey...
      const headers = new Headers...
      if (internalApiKey) { ... }
    If absent, no-op.
    """
    search_window_start = max(0, fetch_start - 350)
    window = text[search_window_start:fetch_start]

    markers = [
        "\n        const internalApiKey =",
        "\n        const headers = new Headers",
    ]

    starts = [window.find(marker) for marker in markers if marker in window]
    if not starts:
        return fetch_start

    local_start = min(pos for pos in starts if pos >= 0)
    absolute_start = search_window_start + local_start

    snippet = text[absolute_start:fetch_start]
    if "headers" in snippet or "internalApiKey" in snippet:
        print("REMOVE stale export header setup")
        return absolute_start

    return fetch_start

def replace_download(text, endpoint, filename, message):
    endpoint_token = f"`{endpoint}`"
    endpoint_pos = text.find(endpoint_token)

    if endpoint_pos == -1:
        print(f"SKIP endpoint not found, maybe already migrated: {endpoint}")
        return text

    fetch_start = text.rfind("\n        const res = await fetch", 0, endpoint_pos)
    if fetch_start == -1:
        raise RuntimeError(f"Could not find fetch start for {endpoint}")

    fetch_start = cleanup_preceding_header_setup(text, fetch_start)

    message_line = f'        setMessage("{message}");'
    message_pos = text.find(message_line, endpoint_pos)
    if message_pos == -1:
        raise RuntimeError(f"Could not find success message line for {endpoint}")

    replacement = f'''
        await downloadApiFile(
          `{endpoint}`,
          `{filename}`
        );

'''

    print(f"REPLACE download fetch: {endpoint}")
    return text[:fetch_start] + replacement + text[message_pos:]

def main():
    text = APP.read_text(encoding="utf-8")

    backup = APP.with_suffix(".jsx.bak.remaining-download-fetches-v2")
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
