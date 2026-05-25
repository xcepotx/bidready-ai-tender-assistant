# BidReady AI Tender Assistant

<!-- BIDREADY_DEPLOYMENT_HARDENING_CHECKLIST -->
## Deployment Hardening Checklist

Production readiness checklist is available here:

- [`docs/DEPLOYMENT_HARDENING_CHECKLIST.md`](docs/DEPLOYMENT_HARDENING_CHECKLIST.md)


<!-- BIDREADY_RELEASE_CHECKPOINT_V0_2_0 -->
## Release Checkpoint v0.2.0

BidReady AI Tender Assistant has completed the post-MVP roadmap through Proposal Template Customization.

- Roadmap completed: Action Tracker, Risk Register, Compliance Scorecard, Approval Workflow, Decision Gate Approval History, Addendum Impact Analysis, Clarification Response Tracker, Executive Pack Export, and Proposal Template Customization.
- Smoke test: **73/73 pass** via `scripts/smoke_test_bidready_i18n.sh`.
- Exports validated: Excel, DOCX, and Executive Pack ZIP.
- Bilingual output supported: English / Indonesia.

Detailed checkpoint notes:

- [`docs/RELEASE_CHECKPOINT_V0_2_0.md`](docs/RELEASE_CHECKPOINT_V0_2_0.md)


BidReady AI Tender Assistant is an internal tender/RFP review assistant for bid teams.

It helps analyze tender documents, extract requirements, generate clarification questions, build a response plan, prepare a proposal outline, track evidence, create an executive bid/no-bid decision gate, and export Excel/DOCX reports.

## Core Capabilities

- Upload and parse tender/RFP documents
- Extract tender metadata
- Extract and review requirements
- Generate clarification questions
- Generate response plan
- Generate proposal outline
- Generate evidence pack
- Generate executive decision gate
- Executive dashboard for owner-level review
- Audit log for key actions
- Export Excel readiness matrix
- Export DOCX proposal draft
- Bilingual artifact generation: English and Bahasa Indonesia
- Regenerate all artifacts after language change

## Project Structure

```text
.
├── apps
│   ├── api
│   └── web
├── docs
├── scripts
├── docker-compose.yml
└── README.md
