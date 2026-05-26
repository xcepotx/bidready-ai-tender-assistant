#!/usr/bin/env python3
from pathlib import Path
import shutil
import re

APP = Path("apps/web/src/App.jsx")
VIEW = Path("apps/web/src/views/ResponsePlanView.jsx")
DETAIL = Path("apps/web/src/components/ResponseItemDetail.jsx")

def backup(path):
    backup_path = path.with_suffix(path.suffix + ".bak.fix-response-id-ui")
    shutil.copy2(path, backup_path)
    print(f"BACKUP: {backup_path}")

def ensure_response_plan_prop():
    text = APP.read_text(encoding="utf-8")
    original = text
    backup(APP)

    # Add languageSetting prop inside ResponsePlanView usage.
    if "<ResponsePlanView" in text and "languageSetting={languageSetting}" not in text:
        markers = [
            "              generateResponsePlan={generateResponsePlan}\n",
            "              updateResponseItem={updateResponseItem}\n",
        ]

        inserted = False
        for marker in markers:
            if marker in text:
                text = text.replace(marker, marker + "              languageSetting={languageSetting}\n", 1)
                inserted = True
                break

        if not inserted:
            raise SystemExit("Could not find safe marker to add languageSetting prop to ResponsePlanView.")

    if text != original:
        APP.write_text(text, encoding="utf-8")
        print("UPDATED App.jsx: pass languageSetting to ResponsePlanView")
    else:
        print("SKIP App.jsx: languageSetting prop already present or no change needed")

def patch_response_plan_view():
    text = VIEW.read_text(encoding="utf-8")
    original = text
    backup(VIEW)

    # Normalize imports.
    if 'translateRequirementTextForUi' not in text:
        if 'import { L } from "../utils/i18n.js";' in text:
            text = text.replace(
                'import { L } from "../utils/i18n.js";',
                'import { translateRequirementTextForUi } from "../utils/i18n.js";'
            )
        else:
            lines = text.splitlines(True)
            insert_at = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("import "):
                    insert_at = i + 1
            text = "".join(lines[:insert_at]) + 'import { translateRequirementTextForUi } from "../utils/i18n.js";\n' + "".join(lines[insert_at:])

    text = text.replace('import { L } from "../utils/i18n.js";\n', "")

    # Add prop and T helper once.
    signature_old = """  generateResponsePlan,
  requirements,
}) {"""
    signature_new = """  generateResponsePlan,
  requirements,
  languageSetting = { output_language: "en" },
}) {
  const uiLanguage = languageSetting?.output_language || "en";
  const isIndonesian = String(uiLanguage || "").toLowerCase().startsWith("id");
  const T = (en, id) => (isIndonesian ? id : en);"""

    if signature_old in text and "const uiLanguage = languageSetting?.output_language" not in text:
        text = text.replace(signature_old, signature_new)

    # Static labels.
    replacements = {
        '<h3>Response Plan</h3>': '<h3>{T("Response Plan", "Rencana Respons")}</h3>',
        '<p className="muted">Convert reviewed requirements into compliance status, response strategy, draft response, and evidence checklist.</p>':
            '<p className="muted">{T("Convert reviewed requirements into compliance status, response strategy, draft response, and evidence checklist.", "Konversi requirement yang sudah direview menjadi status kepatuhan, strategi respons, draft respons, dan checklist evidence.")}</p>',
        'Generate Response Plan': '{T("Generate Response Plan", "Generate Rencana Respons")}',
        'placeholder="Search requirement, draft response, owner, category, or compliance..."':
            'placeholder={T("Search requirement, draft response, owner, category, or compliance...", "Cari requirement, draft respons, owner, kategori, atau kepatuhan...")}',
        '<option value="all">All compliance</option>':
            '<option value="all">{T("All compliance", "Semua kepatuhan")}</option>',
        '<option value="all">All statuses</option>':
            '<option value="all">{T("All statuses", "Semua status")}</option>',
        '<option value="all">All categories</option>':
            '<option value="all">{T("All categories", "Semua kategori")}</option>',
        '{filteredItems.length} / {responsePlan.length} {L("shown", "ditampilkan")}':
            '{filteredItems.length} / {responsePlan.length} {T("shown", "ditampilkan")}',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Translate requirement text display in list/card, but keep metadata values raw.
    text = text.replace(
        "{item.requirement_text}",
        "{translateRequirementTextForUi(item.requirement_text, uiLanguage)}"
    )

    # Pass uiLanguage to detail.
    if "<ResponseItemDetail" in text and "uiLanguage={uiLanguage}" not in text:
        text = text.replace(
            "              updateResponseItem={updateResponseItem}\n            />",
            "              updateResponseItem={updateResponseItem}\n              uiLanguage={uiLanguage}\n            />"
        )

    if text != original:
        VIEW.write_text(text, encoding="utf-8")
        print("UPDATED ResponsePlanView.jsx")
    else:
        print("SKIP ResponsePlanView.jsx: no change needed")

def patch_response_item_detail():
    text = DETAIL.read_text(encoding="utf-8")
    original = text
    backup(DETAIL)

    if 'translateRequirementTextForUi' not in text:
        text = text.replace(
            'import ResponseList from "./ResponseList.jsx";',
            'import { translateRequirementTextForUi } from "../utils/i18n.js";\nimport ResponseList from "./ResponseList.jsx";'
        )

    text = text.replace(
        'export default function ResponseItemDetail({ item, busy, updateResponseItem }) {',
        '''export default function ResponseItemDetail({ item, busy, updateResponseItem, uiLanguage = "en" }) {
  const isIndonesian = String(uiLanguage || "").toLowerCase().startsWith("id");
  const T = (en, id) => (isIndonesian ? id : en);
  const requirementText = translateRequirementTextForUi(item.requirement_text, uiLanguage);
  const evidenceQuote = translateRequirementTextForUi(item.evidence_quote, uiLanguage);'''
    )

    replacements = {
        '<p className="eyebrow dark">Response Item #{item.id}</p>':
            '<p className="eyebrow dark">{T("Response Item", "Item Respons")} #{item.id}</p>',
        '<h2>{item.requirement_text}</h2>':
            '<h2>{requirementText}</h2>',
        '<span>Category: {item.category}</span>':
            '<span>{T("Category", "Kategori")}: {item.category}</span>',
        '<span>Status: {item.status}</span>':
            '<span>{T("Status", "Status")}: {item.status}</span>',
        '<span>Owner: {item.owner || "-"}</span>':
            '<span>{T("Owner", "Penanggung jawab")}: {item.owner || "-"}</span>',
        '<span>Source page: {item.source_page || "-"}</span>':
            '<span>{T("Source page", "Halaman sumber")}: {item.source_page || "-"}</span>',
        '<span>Mode: {item.generation_mode}</span>':
            '<span>{T("Mode", "Mode")}: {item.generation_mode}</span>',
        '<strong>Requirement Evidence</strong>':
            '<strong>{T("Requirement Evidence", "Bukti Requirement")}</strong>',
        '<p>{item.evidence_quote}</p>':
            '<p>{evidenceQuote}</p>',
        '<ResponseList title="Evidence Needed" items={item.evidence_needed || []} />':
            '<ResponseList title={T("Evidence Needed", "Evidence yang Dibutuhkan")} items={item.evidence_needed || []} />',
        '<ResponseList title="Risks" items={item.risks || []} />':
            '<ResponseList title={T("Risks", "Risiko")} items={item.risks || []} />',
        '<ResponseList title="Assumptions" items={item.assumptions || []} />':
            '<ResponseList title={T("Assumptions", "Asumsi")} items={item.assumptions || []} />',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    label_replacements = {
        "Compliance": '{T("Compliance", "Kepatuhan")}',
        "Status": '{T("Status", "Status")}',
        "Owner": '{T("Owner", "Penanggung jawab")}',
        "Confidence": '{T("Confidence", "Tingkat keyakinan")}',
        "Response Strategy": '{T("Response Strategy", "Strategi Respons")}',
        "Draft Response": '{T("Draft Response", "Draft Respons")}',
        "Notes": '{T("Notes", "Catatan")}',
    }

    for en, repl in label_replacements.items():
        text = re.sub(rf'(\n\s*){re.escape(en)}(\n\s*<)', rf'\1{repl}\2', text)

    if text != original:
        DETAIL.write_text(text, encoding="utf-8")
        print("UPDATED ResponseItemDetail.jsx")
    else:
        print("SKIP ResponseItemDetail.jsx: no change needed")

ensure_response_plan_prop()
patch_response_plan_view()
patch_response_item_detail()
