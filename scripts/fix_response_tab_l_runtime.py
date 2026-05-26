#!/usr/bin/env python3
from pathlib import Path
import shutil
import re

VIEW = Path("apps/web/src/views/ResponsePlanView.jsx")
DETAIL = Path("apps/web/src/components/ResponseItemDetail.jsx")
LIST = Path("apps/web/src/components/ResponseList.jsx")

def backup(path):
    backup_path = path.with_suffix(path.suffix + ".bak.fix-response-l-runtime")
    shutil.copy2(path, backup_path)
    print(f"BACKUP: {backup_path}")

def fix_response_plan_view():
    text = VIEW.read_text(encoding="utf-8")
    original = text
    backup(VIEW)

    # ResponsePlanView already has T helper, so no L should remain.
    text = text.replace("L(", "T(")
    text = text.replace('import { L } from "../utils/i18n.js";\n', "")

    # Avoid accidental duplicate import forms.
    text = text.replace(
        'import { L, translateRequirementTextForUi } from "../utils/i18n.js";',
        'import { translateRequirementTextForUi } from "../utils/i18n.js";'
    )
    text = text.replace(
        'import { translateRequirementTextForUi, L } from "../utils/i18n.js";',
        'import { translateRequirementTextForUi } from "../utils/i18n.js";'
    )

    if text != original:
        VIEW.write_text(text, encoding="utf-8")
        print("UPDATED ResponsePlanView.jsx")
    else:
        print("SKIP ResponsePlanView.jsx")

def fix_response_item_detail():
    text = DETAIL.read_text(encoding="utf-8")
    original = text
    backup(DETAIL)

    # ResponseItemDetail already has T helper, so convert remaining L usage to T.
    text = text.replace("L(", "T(")

    # Clean duplicate / unnecessary L import.
    text = text.replace('import { L } from "../utils/i18n.js";\n', "")
    text = text.replace(
        'import { L, translateRequirementTextForUi } from "../utils/i18n.js";',
        'import { translateRequirementTextForUi } from "../utils/i18n.js";'
    )
    text = text.replace(
        'import { translateRequirementTextForUi, L } from "../utils/i18n.js";',
        'import { translateRequirementTextForUi } from "../utils/i18n.js";'
    )

    # Fix Indonesian wording for this label.
    text = text.replace(
        'T("Requirement Evidence", "Evidence Requirement")',
        'T("Requirement Evidence", "Bukti Requirement")'
    )

    # Pass localized empty text to ResponseList.
    text = text.replace(
        '<ResponseList title={T("Evidence Needed", "Evidence yang Dibutuhkan")} items={item.evidence_needed || []} />',
        '<ResponseList title={T("Evidence Needed", "Evidence yang Dibutuhkan")} items={item.evidence_needed || []} emptyText={T("No item.", "Tidak ada item.")} />'
    )
    text = text.replace(
        '<ResponseList title={T("Risks", "Risiko")} items={item.risks || []} />',
        '<ResponseList title={T("Risks", "Risiko")} items={item.risks || []} emptyText={T("No item.", "Tidak ada item.")} />'
    )
    text = text.replace(
        '<ResponseList title={T("Assumptions", "Asumsi")} items={item.assumptions || []} />',
        '<ResponseList title={T("Assumptions", "Asumsi")} items={item.assumptions || []} emptyText={T("No item.", "Tidak ada item.")} />'
    )

    if text != original:
        DETAIL.write_text(text, encoding="utf-8")
        print("UPDATED ResponseItemDetail.jsx")
    else:
        print("SKIP ResponseItemDetail.jsx")

def fix_response_list():
    text = LIST.read_text(encoding="utf-8")
    original = text
    backup(LIST)

    text = text.replace(
        "export default function ResponseList({ title, items }) {",
        'export default function ResponseList({ title, items, emptyText = "No item." }) {'
    )
    text = text.replace(
        '<p className="muted">No item.</p>',
        '<p className="muted">{emptyText}</p>'
    )

    if text != original:
        LIST.write_text(text, encoding="utf-8")
        print("UPDATED ResponseList.jsx")
    else:
        print("SKIP ResponseList.jsx")

fix_response_plan_view()
fix_response_item_detail()
fix_response_list()
