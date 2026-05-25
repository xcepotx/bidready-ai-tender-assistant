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

api_post "/api/v1/projects/${PROJECT_ID}/generate-decision-gate" > "$TMP_DIR/generate_decision_gate.json"
assert_jq "$TMP_DIR/generate_decision_gate.json" '.gate.recommendation | test("Perlu|Rekomendasi")' "Decision Gate generated in Indonesian"

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

log "Validate Audit Log"
api_get "/api/v1/projects/${PROJECT_ID}/audit-logs" > "$TMP_DIR/audit_logs.json"
assert_jq "$TMP_DIR/audit_logs.json" 'length > 0' "Audit logs exist"
assert_jq "$TMP_DIR/audit_logs.json" \
  'any(.[]; .action == "generate_response_plan") and any(.[]; .action == "generate_proposal_outline") and any(.[]; .action == "generate_decision_gate")' \
  "Audit logs contain generated artifact actions"

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
