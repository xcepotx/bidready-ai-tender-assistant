#!/usr/bin/env bash
set -Eeuo pipefail

API_BASE="${API_BASE:-http://127.0.0.1}"
PROJECT_ID="${PROJECT_ID:-2}"
KEY="${KEY:-change-this-internal-key-2026}"
ACTOR="${ACTOR:-bid_manager}"
TMP_DIR="${TMP_DIR:-/tmp/bidready_smoke_${PROJECT_ID}}"

mkdir -p "$TMP_DIR"

PASS_COUNT=0
FAIL_COUNT=0

log() {
  echo
  echo "===== $* ====="
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  echo "✅ PASS: $*"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  echo "❌ FAIL: $*" >&2
  echo "Debug artifacts saved in: $TMP_DIR" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing command: $1"
}

api_get() {
  local path="$1"
  curl -sS -f \
    -H "X-Internal-API-Key: $KEY" \
    "$API_BASE$path"
}

api_post() {
  local path="$1"
  curl -sS -f -X POST \
    -H "X-Internal-API-Key: $KEY" \
    -H "X-Actor: $ACTOR" \
    "$API_BASE$path"
}

api_patch_json() {
  local path="$1"
  local payload="$2"
  curl -sS -f -X PATCH \
    -H "Content-Type: application/json" \
    -H "X-Internal-API-Key: $KEY" \
    -H "X-Actor: $ACTOR" \
    -d "$payload" \
    "$API_BASE$path"
}

assert_jq() {
  local file="$1"
  local filter="$2"
  local label="$3"

  if jq -e "$filter" "$file" >/dev/null 2>&1; then
    pass "$label"
  else
    echo "--- File: $file ---" >&2
    cat "$file" >&2 || true
    fail "$label"
  fi
}


api_post_json() {
  local path="$1"
  local body="$2"
  curl -fsS -X POST "$API_BASE$path" \
    -H "X-Internal-API-Key: $KEY" \
    -H "Content-Type: application/json" \
    -d "$body"
}

log "Preflight"
require_cmd curl
require_cmd jq
require_cmd docker
docker compose ps >/dev/null
pass "Required commands available"

log "API health"
curl -sS -f "$API_BASE/api/health" > "$TMP_DIR/health.json"
pass "API health endpoint reachable"

log "Project exists"
api_get "/api/v1/projects" > "$TMP_DIR/projects.json"

if jq -e --argjson project_id "$PROJECT_ID" 'any(.[]; .id == $project_id)' "$TMP_DIR/projects.json" >/dev/null 2>&1; then
  pass "Project #$PROJECT_ID exists"
else
  echo "--- File: $TMP_DIR/projects.json ---" >&2
  cat "$TMP_DIR/projects.json" >&2 || true
  fail "Project #$PROJECT_ID exists"
fi

log "Set language output to Indonesia"
api_patch_json "/api/v1/projects/${PROJECT_ID}/language" \
  '{"input_language":"auto","output_language":"id"}' > "$TMP_DIR/language.json"

assert_jq "$TMP_DIR/language.json" '.output_language == "id"' "Project output_language is id"

log "Core project data endpoints"
api_get "/api/v1/projects/${PROJECT_ID}/requirements" > "$TMP_DIR/requirements.json"
assert_jq "$TMP_DIR/requirements.json" 'length > 0' "Requirements exist"

api_get "/api/v1/projects/${PROJECT_ID}/documents" > "$TMP_DIR/documents.json"
assert_jq "$TMP_DIR/documents.json" 'length > 0' "Documents exist"

api_get "/api/v1/projects/${PROJECT_ID}/readiness-summary" > "$TMP_DIR/readiness_summary.json"
assert_jq "$TMP_DIR/readiness_summary.json" '.readiness_score >= 0' "Readiness summary available"

api_get "/api/v1/projects/${PROJECT_ID}/metadata" > "$TMP_DIR/metadata.json"
assert_jq "$TMP_DIR/metadata.json" '.project_id == '"$PROJECT_ID"'' "Project metadata available"

log "Regenerate artifacts"
api_post "/api/v1/projects/${PROJECT_ID}/generate-clarifications" > "$TMP_DIR/generate_clarifications.json"
pass "Generate clarifications endpoint completed"

api_post "/api/v1/projects/${PROJECT_ID}/generate-response-plan" > "$TMP_DIR/generate_response_plan.json"
assert_jq "$TMP_DIR/generate_response_plan.json" '(.generated_count // (.items | length) // 0) > 0' "Response Plan generated"

api_post "/api/v1/projects/${PROJECT_ID}/generate-proposal-outline" > "$TMP_DIR/generate_proposal_outline.json"
assert_jq "$TMP_DIR/generate_proposal_outline.json" '(.generated_count // (.sections | length) // (.items | length) // 0) > 0' "Proposal Outline generated"

api_post "/api/v1/projects/${PROJECT_ID}/generate-evidence-pack" > "$TMP_DIR/generate_evidence_pack.json"
assert_jq "$TMP_DIR/generate_evidence_pack.json" '(.generated_count // (.items | length) // 0) > 0' "Evidence Pack generated"

api_post "/api/v1/projects/${PROJECT_ID}/generate-compliance-scorecard" > "$TMP_DIR/generate_compliance_scorecard.json"
assert_jq "$TMP_DIR/generate_compliance_scorecard.json" '(.generated_count // (.items | length) // 0) > 0' "Compliance Scorecard generated"
assert_jq "$TMP_DIR/generate_compliance_scorecard.json" '.summary.score_percent >= 0' "Compliance Scorecard summary available"

api_post "/api/v1/projects/${PROJECT_ID}/generate-decision-gate" > "$TMP_DIR/generate_decision_gate.json"
assert_jq "$TMP_DIR/generate_decision_gate.json" '.gate.recommendation | test("Perlu|Rekomendasi")' "Decision Gate generated in Indonesian"

api_post "/api/v1/projects/${PROJECT_ID}/generate-risk-register" > "$TMP_DIR/generate_risk_register.json"
assert_jq "$TMP_DIR/generate_risk_register.json" '(.generated_count // (.items | length) // 0) > 0' "Risk Register generated"

api_post "/api/v1/projects/${PROJECT_ID}/generate-approval-workflow" > "$TMP_DIR/generate_approval_workflow.json"
assert_jq "$TMP_DIR/generate_approval_workflow.json" '.steps | length > 0' "Approval Workflow generated"
assert_jq "$TMP_DIR/generate_approval_workflow.json" '.summary.total_steps > 0' "Approval Workflow summary available"

api_post "/api/v1/projects/${PROJECT_ID}/generate-addendum-impact-analysis" > "$TMP_DIR/generate_addendum_impact.json"
assert_jq "$TMP_DIR/generate_addendum_impact.json" '(.generated_count // (.items | length) // 0) > 0' "Addendum Impact Analysis generated"
assert_jq "$TMP_DIR/generate_addendum_impact.json" '.summary.total_items > 0' "Addendum Impact Analysis summary available"

api_post "/api/v1/projects/${PROJECT_ID}/generate-clarification-response-tracker" > "$TMP_DIR/generate_clarification_response_tracker.json"
assert_jq "$TMP_DIR/generate_clarification_response_tracker.json" '(.generated_count // (.items | length) // 0) > 0' "Clarification Response Tracker generated"
assert_jq "$TMP_DIR/generate_clarification_response_tracker.json" '.summary.total_items > 0' "Clarification Response Tracker summary available"

log "Validate Clarifications"
api_get "/api/v1/projects/${PROJECT_ID}/clarifications" > "$TMP_DIR/clarifications.json"
assert_jq "$TMP_DIR/clarifications.json" 'length > 0' "Clarifications exist"

log "Validate Response Plan i18n"
api_get "/api/v1/projects/${PROJECT_ID}/response-plan" > "$TMP_DIR/response_plan.json"

assert_jq "$TMP_DIR/response_plan.json" \
  '.[0].response_strategy | test("Siapkan|Konfirmasi|Review|Validasi")' \
  "Response Plan strategy localized"

assert_jq "$TMP_DIR/response_plan.json" \
  '.[0].draft_response | test("Kami memahami")' \
  "Response Plan draft localized"

assert_jq "$TMP_DIR/response_plan.json" \
  'any(.[]; (.evidence_needed | tostring) | test("Arsitektur|Proposal komersial|Checklist|Evidence|CV resource"))' \
  "Response Plan evidence checklist localized"

assert_jq "$TMP_DIR/response_plan.json" \
  '.[0].assumptions[0] | test("Response harus|Bahasa final")' \
  "Response Plan assumptions localized"

assert_jq "$TMP_DIR/response_plan.json" \
  '.[0].risks[0] | test("Tidak ada risiko|Requirement|high-risk")' \
  "Response Plan risks localized"

assert_jq "$TMP_DIR/response_plan.json" \
  '.[0].notes | test("Dihasilkan")' \
  "Response Plan notes localized"

log "Validate Proposal Outline i18n"
api_get "/api/v1/projects/${PROJECT_ID}/proposal-outline" > "$TMP_DIR/proposal_outline.json"

assert_jq "$TMP_DIR/proposal_outline.json" \
  '.[0].title | test("Ringkasan|Pemahaman|Solusi|Pendekatan|Security|Commercial|Asumsi|Checklist")' \
  "Proposal Outline title localized"

assert_jq "$TMP_DIR/proposal_outline.json" \
  '.[0].purpose | test("Memberikan|Menjelaskan|Merangkum|Menjabarkan|Menyediakan")' \
  "Proposal Outline purpose localized"

assert_jq "$TMP_DIR/proposal_outline.json" \
  '.[0].content_outline | tostring | test("Ringkas|Posisikan|Highlight|Jelaskan")' \
  "Proposal Outline content outline localized"

assert_jq "$TMP_DIR/proposal_outline.json" \
  '.[0].draft_content | test("Proposal ini|Section ini|Response disusun")' \
  "Proposal Outline draft content localized"

assert_jq "$TMP_DIR/proposal_outline.json" \
  '.[0].notes | test("Dihasilkan")' \
  "Proposal Outline notes localized"

log "Validate Evidence Pack"
api_get "/api/v1/projects/${PROJECT_ID}/evidence-pack" > "$TMP_DIR/evidence_pack.json"

assert_jq "$TMP_DIR/evidence_pack.json" 'length > 0' "Evidence Pack exists"
assert_jq "$TMP_DIR/evidence_pack.json" \
  'any(.[]; (.notes // "") | test("Dit|Dihasilkan|evidence"))' \
  "Evidence Pack notes available/localized"

log "Validate Decision Gate i18n"
api_get "/api/v1/projects/${PROJECT_ID}/decision-gate" > "$TMP_DIR/decision_gate.json"

assert_jq "$TMP_DIR/decision_gate.json" \
  '.recommendation | test("Perlu Review Eksekutif|Rekomendasi")' \
  "Decision Gate recommendation localized"

assert_jq "$TMP_DIR/decision_gate.json" \
  '.executive_summary | test("Decision gate ini|Sistem mengidentifikasi|Skor")' \
  "Decision Gate executive summary localized"

assert_jq "$TMP_DIR/decision_gate.json" \
  '.key_reasons | tostring | test("Skor readiness|requirement berhasil|response plan")' \
  "Decision Gate key reasons localized"

assert_jq "$TMP_DIR/decision_gate.json" \
  '.next_actions | tostring | test("Selesaikan|Kumpulkan|Pindahkan")' \
  "Decision Gate next actions localized"

log "Validate Compliance Scorecard"
api_get "/api/v1/projects/${PROJECT_ID}/compliance-scorecard" > "$TMP_DIR/compliance_scorecard.json"
assert_jq "$TMP_DIR/compliance_scorecard.json" '.items | length > 0' "Compliance Scorecard exists"
assert_jq "$TMP_DIR/compliance_scorecard.json" '.summary.score_percent >= 0' "Compliance Scorecard score exists"
assert_jq "$TMP_DIR/compliance_scorecard.json" 'any(.items[]; (.gap_summary // .recommended_action // "") | test("Requirement|review|evidence|Compliance|Clarification|Gap|Tugaskan|Dihasilkan|Review"))' "Compliance Scorecard guidance available/localized"

COMPLIANCE_ID="$(jq -r '.items[0].id // empty' "$TMP_DIR/compliance_scorecard.json")"
if [ -z "$COMPLIANCE_ID" ]; then
  fail "Compliance item ID available"
fi

api_patch_json "/api/v1/compliance-items/${COMPLIANCE_ID}" \
  '{"compliance_status":"needs_review","score":55,"notes":"Smoke test compliance update"}' > "$TMP_DIR/compliance_item_update.json"
assert_jq "$TMP_DIR/compliance_item_update.json" '.compliance_status == "needs_review" and .score == 55' "Compliance item update works"

log "Validate Risk Register"
api_get "/api/v1/projects/${PROJECT_ID}/risk-register" > "$TMP_DIR/risk_register.json"
assert_jq "$TMP_DIR/risk_register.json" 'length > 0' "Risk Register exists"
assert_jq "$TMP_DIR/risk_register.json" 'any(.[]; (.mitigation_plan // .notes // "") | test("Mitigasi|Review|Validasi|Kumpulkan|Escalate|Dihasilkan|Clarification"))' "Risk Register mitigation available/localized"

RISK_ID="$(jq -r '.[0].id // empty' "$TMP_DIR/risk_register.json")"
if [ -z "$RISK_ID" ]; then
  fail "Risk item ID available"
fi

api_patch_json "/api/v1/risk-items/${RISK_ID}" \
  '{"status":"mitigating","notes":"Smoke test risk update"}' > "$TMP_DIR/risk_item_update.json"
assert_jq "$TMP_DIR/risk_item_update.json" '.status == "mitigating"' "Risk item update works"

log "Validate Approval Workflow"
api_get "/api/v1/projects/${PROJECT_ID}/approval-workflow" > "$TMP_DIR/approval_workflow.json"
assert_jq "$TMP_DIR/approval_workflow.json" '.steps | length > 0' "Approval Workflow exists"

APPROVAL_ID="$(jq -r '.request.id // empty' "$TMP_DIR/approval_workflow.json")"
if [ -z "$APPROVAL_ID" ]; then
  fail "Approval workflow ID available"
fi

api_post_json "/api/v1/approval-workflows/${APPROVAL_ID}/submit" \
  '{"submitted_by":"smoke_test","notes":"Smoke test approval submission"}' > "$TMP_DIR/approval_submit.json"
assert_jq "$TMP_DIR/approval_submit.json" '.request.status == "pending"' "Approval Workflow submit works"

APPROVAL_STEP_ID="$(jq -r '.steps[0].id // empty' "$TMP_DIR/approval_submit.json")"
if [ -z "$APPROVAL_STEP_ID" ]; then
  fail "Approval step ID available"
fi

api_patch_json "/api/v1/approval-steps/${APPROVAL_STEP_ID}" \
  '{"status":"approved","decision_note":"Smoke test approved","decided_by":"smoke_test"}' > "$TMP_DIR/approval_step_update.json"
assert_jq "$TMP_DIR/approval_step_update.json" '.status == "approved"' "Approval step approve works"

log "Validate Clarification Response Tracker"
api_get "/api/v1/projects/${PROJECT_ID}/clarification-response-tracker" > "$TMP_DIR/clarification_response_tracker.json"
assert_jq "$TMP_DIR/clarification_response_tracker.json" '.items | length > 0' "Clarification Response Tracker exists"
assert_jq "$TMP_DIR/clarification_response_tracker.json" '.summary.total_items > 0' "Clarification Response Tracker summary exists"
assert_jq "$TMP_DIR/clarification_response_tracker.json" 'any(.items[]; (.recommended_follow_up // .notes // "") | test("Track|Pantau|Review|follow-up|Dihasilkan"))' "Clarification Response Tracker guidance available/localized"

CLARIFICATION_RESPONSE_ID="$(jq -r '.items[0].id // empty' "$TMP_DIR/clarification_response_tracker.json")"
if [ -z "$CLARIFICATION_RESPONSE_ID" ]; then
  fail "Clarification response item ID available"
fi

api_patch_json "/api/v1/clarification-response-items/${CLARIFICATION_RESPONSE_ID}" \
  '{"response_status":"answered","client_response":"Smoke test client response","notes":"Smoke test clarification response update"}' > "$TMP_DIR/clarification_response_update.json"
assert_jq "$TMP_DIR/clarification_response_update.json" '.response_status == "answered" and (.client_response | test("Smoke test"))' "Clarification response item update works"

log "Validate Addendum Impact Analysis"
api_get "/api/v1/projects/${PROJECT_ID}/addendum-impacts" > "$TMP_DIR/addendum_impacts.json"
assert_jq "$TMP_DIR/addendum_impacts.json" '.items | length > 0' "Addendum Impact Analysis exists"
assert_jq "$TMP_DIR/addendum_impacts.json" '.summary.total_items > 0' "Addendum Impact Analysis summary exists"
assert_jq "$TMP_DIR/addendum_impacts.json" 'any(.items[]; (.recommended_action // .notes // "") | test("Review|review|Validasi|Konfirmasi|Generated|Dihasilkan|Update"))' "Addendum Impact Analysis guidance available/localized"

ADDENDUM_IMPACT_ID="$(jq -r '.items[0].id // empty' "$TMP_DIR/addendum_impacts.json")"
if [ -z "$ADDENDUM_IMPACT_ID" ]; then
  fail "Addendum impact item ID available"
fi

api_patch_json "/api/v1/addendum-impact-items/${ADDENDUM_IMPACT_ID}" \
  '{"status":"reviewed","notes":"Smoke test addendum impact update"}' > "$TMP_DIR/addendum_impact_update.json"
assert_jq "$TMP_DIR/addendum_impact_update.json" '.status == "reviewed"' "Addendum impact item update works"

log "Validate Decision Gate Approval History"
api_get "/api/v1/projects/${PROJECT_ID}/decision-gate-history" > "$TMP_DIR/decision_gate_history.json"
assert_jq "$TMP_DIR/decision_gate_history.json" '.events | length > 0' "Decision Gate Approval History exists"
assert_jq "$TMP_DIR/decision_gate_history.json" '.summary.total_events > 0' "Decision Gate Approval History summary available"
assert_jq "$TMP_DIR/decision_gate_history.json" 'any(.events[]; .action == "generate_decision_gate")' "Decision Gate history includes decision event"
assert_jq "$TMP_DIR/decision_gate_history.json" 'any(.events[]; (.action | test("approval")))' "Decision Gate history includes approval event"

log "Validate Audit Log"
api_get "/api/v1/projects/${PROJECT_ID}/audit-logs" > "$TMP_DIR/audit_logs.json"
assert_jq "$TMP_DIR/audit_logs.json" 'length > 0' "Audit logs exist"
assert_jq "$TMP_DIR/audit_logs.json" \
  'any(.[]; .action == "generate_response_plan") and any(.[]; .action == "generate_proposal_outline") and any(.[]; .action == "generate_decision_gate") and any(.[]; .action == "generate_compliance_scorecard") and any(.[]; .action == "generate_risk_register") and any(.[]; .action == "generate_approval_workflow") and any(.[]; .action == "generate_addendum_impact_analysis") and any(.[]; .action == "generate_clarification_response_tracker")' \
  "Audit logs contain generated artifact actions"

log "Validate Proposal Template Customization"
TEMPLATE_MARKER="BidReady Custom Executive Proposal Smoke"
TEMPLATE_PAYLOAD="$TMP_DIR/proposal_template_payload.json"

cat > "$TEMPLATE_PAYLOAD" <<JSON
{
  "template_name": "Executive Custom Template",
  "executive_title": "${TEMPLATE_MARKER}",
  "cover_note": "Cover note from template customization smoke test.",
  "company_profile": "Company profile from template customization smoke test.",
  "win_theme": "Win theme from template customization smoke test.",
  "proposal_tone": "executive",
  "custom_sections": [
    {
      "title": "Custom Differentiator Section",
      "content": "This custom section is inserted by the proposal template."
    }
  ],
  "footer_note": "Footer note from proposal template customization."
}
JSON

echo "Proposal template payload:"
cat "$TEMPLATE_PAYLOAD"

curl -fsS -X PATCH "$API_BASE/api/v1/projects/${PROJECT_ID}/proposal-template" \
  -H "X-Internal-API-Key: $KEY" \
  -H "X-Actor: smoke_test" \
  -H "Content-Type: application/json" \
  --data-binary @"$TEMPLATE_PAYLOAD" \
  > "$TMP_DIR/proposal_template_update.json"

assert_jq "$TMP_DIR/proposal_template_update.json" '.executive_title == "BidReady Custom Executive Proposal Smoke" and .proposal_tone == "executive"' "Proposal Template update works"

api_get "/api/v1/projects/${PROJECT_ID}/proposal-template" > "$TMP_DIR/proposal_template.json"
assert_jq "$TMP_DIR/proposal_template.json" '.template_name == "Executive Custom Template" and (.custom_sections | length) == 1' "Proposal Template read works"

TEMPLATE_DOCX="$TMP_DIR/bidready_template_customized_${PROJECT_ID}.docx"
curl -fsS -L \
  -H "X-Internal-API-Key: $KEY" \
  "$API_BASE/api/v1/projects/${PROJECT_ID}/exports/proposal-draft.docx" \
  -o "$TEMPLATE_DOCX"

python3 - "$TEMPLATE_DOCX" "$TEMPLATE_MARKER" <<'PYDOCX'
import re
import sys
from pathlib import Path
from zipfile import ZipFile

path = Path(sys.argv[1])
marker = sys.argv[2]

with ZipFile(path) as zf:
    xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")

text = re.sub(r"<[^>]+>", " ", xml)
text = re.sub(r"\s+", " ", text)

required = [
    marker,
    "Cover note from template customization smoke test.",
    "Company profile from template customization smoke test.",
    "Win theme from template customization smoke test.",
    "Custom Differentiator Section",
    "This custom section is inserted by the proposal template.",
    "Footer note from proposal template customization.",
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"Missing template text in DOCX: {missing}")
PYDOCX

pass "Proposal Template DOCX content validated"

log "Export Executive Pack"
EXEC_PACK="$TMP_DIR/bidready_ai_executive_pack_project_${PROJECT_ID}.zip"
curl -fsS -L \
  -H "X-Internal-API-Key: $KEY" \
  "$API_BASE/api/v1/projects/${PROJECT_ID}/exports/executive-pack.zip" \
  -o "$EXEC_PACK"
python3 - "$EXEC_PACK" <<'PY'
import json
import sys
from pathlib import Path
from zipfile import ZipFile

path = Path(sys.argv[1])
required = {
    "bidready_ai_tender_report.xlsx",
    "bidready_ai_proposal_draft.docx",
    "executive_summary.md",
    "executive_summary.json",
    "decision_gate_history.json",
    "approval_workflow.json",
    "compliance_scorecard.json",
    "risk_register.json",
    "action_tracker.json",
    "clarification_response_tracker.json",
    "addendum_impact_analysis.json",
    "audit_logs.json",
}
with ZipFile(path) as zf:
    names = set(zf.namelist())
    missing = required - names
    if missing:
        raise SystemExit(f"Missing executive pack files: {sorted(missing)}")
    summary = json.loads(zf.read("executive_summary.json").decode("utf-8"))
    if not summary.get("project", {}).get("id"):
        raise SystemExit("executive_summary.json missing project id")
    if "decision_gate" not in summary:
        raise SystemExit("executive_summary.json missing decision_gate")
PY
pass "Executive Pack ZIP export is valid"
pass "Executive Pack ZIP contains required files"

log "Export Excel and DOCX"
curl -sS -f -L -o "$TMP_DIR/bidready_ai_tender_report_project_${PROJECT_ID}_id.xlsx" \
  -H "X-Internal-API-Key: $KEY" \
  "$API_BASE/api/v1/projects/${PROJECT_ID}/exports/checklist.xlsx"

curl -sS -f -L -o "$TMP_DIR/bidready_ai_proposal_draft_project_${PROJECT_ID}_id.docx" \
  -H "X-Internal-API-Key: $KEY" \
  "$API_BASE/api/v1/projects/${PROJECT_ID}/exports/proposal-draft.docx"

file "$TMP_DIR/bidready_ai_tender_report_project_${PROJECT_ID}_id.xlsx" | grep -Eq "Microsoft Excel|Microsoft OOXML" \
  && pass "Excel export file is valid" \
  || fail "Excel export file is invalid"

file "$TMP_DIR/bidready_ai_proposal_draft_project_${PROJECT_ID}_id.docx" | grep -Eq "Microsoft Word|Microsoft OOXML" \
  && pass "DOCX export file is valid" \
  || fail "DOCX export file is invalid"

log "Validate Excel content inside API container"
docker compose exec -T api python - <<PY > "$TMP_DIR/xlsx_validation.txt"
from openpyxl import load_workbook

project_id = ${PROJECT_ID}
path = f"/app/exports/project_{project_id}/bidready_ai_tender_report_project_{project_id}.xlsx"
wb = load_workbook(path, read_only=True)

if "Decision Gate" not in wb.sheetnames:
    raise SystemExit(f"Decision Gate sheet missing. Sheets: {wb.sheetnames}")

ws = wb["Decision Gate"]
values = []
for row in ws.iter_rows(values_only=True):
    values.extend([x for x in row if x])

text = "\\n".join(str(x) for x in values)

required = [
    "BidReady AI - Decision Gate Eksekutif",
    "Status Keputusan",
    "Rekomendasi",
    "Skor Readiness",
    "Approval yang Dibutuhkan",
    "Tindak Lanjut",
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"Missing Excel labels: {missing}")

print("OK Excel i18n labels found")
PY

grep -q "OK Excel" "$TMP_DIR/xlsx_validation.txt" \
  && pass "Excel i18n content validated" \
  || fail "Excel i18n content validation failed"

log "Validate DOCX content inside API container"
docker compose exec -T api python - <<PY > "$TMP_DIR/docx_validation.txt"
from docx import Document

project_id = ${PROJECT_ID}
path = f"/app/exports/project_{project_id}/bidready_ai_proposal_draft_project_{project_id}.docx"
doc = Document(path)

parts = []
for p in doc.paragraphs:
    parts.append(p.text)

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            parts.append(cell.text)

text = "\\n".join(parts)

required = [
    "Decision Gate Eksekutif",
    "Perlu Review Eksekutif",
    "Proposal ini merespons",
    "Tindak Lanjut",
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"Missing DOCX text: {missing}")

print("OK DOCX i18n content found")
PY

grep -q "OK DOCX" "$TMP_DIR/docx_validation.txt" \
  && pass "DOCX i18n content validated" \
  || fail "DOCX i18n content validation failed"

log "Final Summary"
echo "Project ID: $PROJECT_ID"
echo "API Base: $API_BASE"
echo "Artifacts:"
echo "- $TMP_DIR/bidready_ai_tender_report_project_${PROJECT_ID}_id.xlsx"
echo "- $TMP_DIR/bidready_ai_proposal_draft_project_${PROJECT_ID}_id.docx"
echo "Passed checks: $PASS_COUNT"
echo "Failed checks: $FAIL_COUNT"
echo
echo "✅ BIDREADY SMOKE TEST PASSED"
