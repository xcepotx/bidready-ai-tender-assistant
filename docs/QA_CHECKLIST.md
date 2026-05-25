# BidReady AI QA Checklist

## Smoke Test

Run this before demo:

PROJECT_ID=2 \
KEY="your-local-internal-key" \
API_BASE="http://127.0.0.1" \
./scripts/smoke_test_bidready_i18n.sh

Expected result:

BIDREADY SMOKE TEST PASSED

## UI Checklist

- [ ] Project list loads
- [ ] Project can be selected
- [ ] Language selector works
- [ ] Regenerate All Artifacts works
- [ ] Executive Dashboard appears
- [ ] Requirements page loads
- [ ] Clarifications page loads
- [ ] Response Plan page loads
- [ ] Proposal Outline page loads
- [ ] Evidence Pack page loads
- [ ] Decision Gate page loads
- [ ] Audit Log page loads
- [ ] Excel export works
- [ ] DOCX export works

## i18n Checklist

When Output Language is Indonesia:

- [ ] Response Plan strategy is localized
- [ ] Response Plan draft response is localized
- [ ] Response Plan evidence checklist is localized
- [ ] Proposal Outline purpose is localized
- [ ] Proposal Outline draft content is localized
- [ ] Decision Gate recommendation is localized
- [ ] Excel labels are localized
- [ ] DOCX labels are localized

## Backend Checklist

- [ ] /api/health returns OK
- [ ] /api/v1/projects returns project list
- [ ] /api/v1/projects/{id}/language works
- [ ] /api/v1/projects/{id}/requirements works
- [ ] /api/v1/projects/{id}/clarifications works
- [ ] /api/v1/projects/{id}/response-plan works
- [ ] /api/v1/projects/{id}/proposal-outline works
- [ ] /api/v1/projects/{id}/evidence-pack works
- [ ] /api/v1/projects/{id}/decision-gate works
- [ ] /api/v1/projects/{id}/audit-logs works
- [ ] /api/v1/projects/{id}/exports/checklist.xlsx works
- [ ] /api/v1/projects/{id}/exports/proposal-draft.docx works

## Safety Checklist

- [ ] .env is not committed
- [ ] Uploaded tender files are not committed
- [ ] Generated exports are not committed
- [ ] Backup folders are not committed
- [ ] Smoke test passes before demo
