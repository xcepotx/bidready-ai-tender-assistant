# BidReady AI Tender Assistant — Release Checkpoint v0.2.0

## Status

Post-MVP roadmap completed and validated.

- Smoke test: 73/73 pass
- Script: `scripts/smoke_test_bidready_i18n.sh`
- Tested project: Project ID 2
- Exports validated: Excel, DOCX, and Executive Pack ZIP
- Bilingual output: English / Indonesia

## Completed Roadmap

1. Action Tracker / Task Assignment
2. Risk Register
3. Compliance Matrix Scorecard
4. Approval Workflow
5. Decision Gate Approval History
6. Addendum / Document Impact Analysis
7. Clarification Response Tracker
8. One-click Executive Pack Export
9. Proposal Template Customization

## Core Capabilities

- Project workspace
- RFP document upload and parsing
- Project metadata extraction
- Requirement extraction
- Clarification question generation
- Response plan generation
- Proposal outline generation
- Evidence pack generation
- Decision gate generation
- Executive dashboard
- Audit log
- English / Indonesia output
- Regenerate-all-artifacts workflow
- Excel export
- DOCX proposal draft export
- Executive Pack ZIP export
- Proposal template customization

## Main Endpoints Added

### Action Tracker
- `GET /api/v1/projects/{project_id}/action-items`
- `POST /api/v1/projects/{project_id}/generate-action-items`
- `PATCH /api/v1/action-items/{item_id}`

### Risk Register
- `GET /api/v1/projects/{project_id}/risk-register`
- `POST /api/v1/projects/{project_id}/generate-risk-register`
- `PATCH /api/v1/risk-items/{item_id}`

### Compliance Scorecard
- `GET /api/v1/projects/{project_id}/compliance-scorecard`
- `POST /api/v1/projects/{project_id}/generate-compliance-scorecard`
- `PATCH /api/v1/compliance-items/{item_id}`

### Approval Workflow
- `GET /api/v1/projects/{project_id}/approval-workflow`
- `POST /api/v1/projects/{project_id}/generate-approval-workflow`
- `POST /api/v1/approval-workflows/{workflow_id}/submit`
- `PATCH /api/v1/approval-steps/{step_id}`

### Decision Gate Approval History
- `GET /api/v1/projects/{project_id}/decision-gate-history`

### Addendum Impact Analysis
- `GET /api/v1/projects/{project_id}/addendum-impacts`
- `POST /api/v1/projects/{project_id}/generate-addendum-impact-analysis`
- `PATCH /api/v1/addendum-impact-items/{item_id}`

### Clarification Response Tracker
- `GET /api/v1/projects/{project_id}/clarification-response-tracker`
- `POST /api/v1/projects/{project_id}/generate-clarification-response-tracker`
- `PATCH /api/v1/clarification-response-items/{item_id}`

### Executive Pack Export
- `GET /api/v1/projects/{project_id}/exports/executive-pack.zip`

### Proposal Template Customization
- `GET /api/v1/projects/{project_id}/proposal-template`
- `PATCH /api/v1/projects/{project_id}/proposal-template`

## Executive Pack Contents

- `bidready_ai_tender_report.xlsx`
- `bidready_ai_proposal_draft.docx`
- `executive_summary.md`
- `executive_summary.json`
- `decision_gate.json`
- `decision_gate_history.json`
- `approval_workflow.json`
- `compliance_scorecard.json`
- `risk_register.json`
- `action_tracker.json`
- `clarification_response_tracker.json`
- `addendum_impact_analysis.json`
- `audit_logs.json`

## Smoke Test

```bash
cd /data/tender-ai/app/tender-review-assistant
API_BASE="${API_BASE:-http://127.0.0.1}" PROJECT_ID="${PROJECT_ID:-2}" KEY="${KEY:-change-this-internal-key-2026}" scripts/smoke_test_bidready_i18n.sh
```

Expected result:

```text
Passed checks: 73
Failed checks: 0
BIDREADY SMOKE TEST PASSED
```

## Notes

New workflow modules use snapshot-style references for generated artifact IDs. This avoids regeneration conflicts when response plans, compliance scorecards, risks, and other generated artifacts are rebuilt.
