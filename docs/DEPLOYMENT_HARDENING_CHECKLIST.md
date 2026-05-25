# BidReady AI Tender Assistant â€” Deployment Hardening Checklist

## Current Baseline

- Roadmap completed through Proposal Template Customization.
- Smoke test: 73/73 pass.
- Exports validated: Excel, DOCX, Executive Pack ZIP.
- Backend: FastAPI.
- Frontend: React.
- Runtime: Docker Compose.
- Path: `/data/tender-ai/app/tender-review-assistant`.

## 1. Environment and Secrets

- Keep `.env` and `.env.example` aligned.
- Use a strong `INTERNAL_API_KEY` per environment.
- Do not commit real secrets.
- Rotate keys that were copied into logs or chat.
- Set `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` explicitly in production.
- Confirm export and upload directories are writable only by expected users/containers.

## 2. Docker Compose

- Add healthchecks for API and database.
- Use restart policy for API, web, and database.
- Pin stable image versions where practical.
- Review mounted volumes.
- Confirm logs do not expose API keys or document content.

Useful checks:

```bash
docker compose ps
docker compose logs --tail=120 api
curl -fsS http://127.0.0.1/api/health
```

## 3. Database Safety

- Confirm PostgreSQL data volume is persistent.
- Add scheduled database backup.
- Test restore from backup.
- Add Alembic migration workflow before production data grows.
- Add indexes only after query patterns are clear.

Backup example:

```bash
mkdir -p /tmp/bidready_db_backups
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "/tmp/bidready_db_backups/bidready_$(date +%Y%m%d¥µd•!d•4¤).sql"
```

## 4. Authentication and Authorization

Current API is protected by internal API key. Production should add:

- User login.
- Role-based permissions.
- Roles such as Admin, Bid Manager, Commercial Owner, Legal Reviewer, Executive Sponsor, Viewer.
- Authenticated audit actor identity instead of relying only on `X-Actor`.
- Rate limiting for expensive generation and export endpoints.

## 5. File Upload and Storage

- Limit upload file size.
- Allow only expected document types.
- Validate MIME type.
- Store uploads outside public frontend paths.
- Use private object storage or encrypted volume for sensitive RFP files.
- Add retention policy for uploads and generated exports.
- Add cleanup job for old exports.

## 6. Export Security

- Keep export endpoints protected.
- Avoid public predictable file URLs.
- Use safe download headers.
- Review Executive Pack contents before production use.
- Consider limiting `audit_logs.json` in Executive Pack to business-safe fields.
- Add retention policy for generated ZIP/DOCX/XLSX files.

## 7. API Reliability

- Keep `/api/health` lightweight.
- Add database readiness check.
- Add timeout for long generation/export requests.
- Consider background job queue for heavy generators.
- Prevent concurrent regenerate-all runs per project.
- Add pagination for large list endpoints.

Important endpoints to monitor:

- `/api/health`
- `/api/v1/projects/{project_id}/requirements`
- `/api/v1/projects/{project_id}/decision-gate`
- `/api/v1/projects/{project_id}/exports/proposal-draft.docx`
- `/api/v1/projects/{project_id}/exports/executive-pack.zip`

## 8. Frontend Production

- Build frontend in production mode.
- Confirm static asset caching.
- Add better loading states for long exports.
- Add confirmation for destructive/regenerate actions.
- Ensure all tabs have useful empty states.
- Keep API error messages useful but not verbose enough to leak stack traces.

Build check:

```bash
cd apps/web
npm run build
```

## 9. Reverse Proxy / Nginx

- Enable HTTPS.
- Redirect HTTP to HTTPS.
- Set upload size limit, for example `client_max_body_size 50M;`.
- Set reasonable proxy timeouts for export endpoints.
- Block access to internal paths.
- Do not serve generated exports as public static files.

## 10. Observability

Minimum:

- Retain API/web/database logs.
- Monitor `/api/health`.
- Run smoke test after deployment.
- Log export failures with project id and actor.
- Keep audit log accessible.

Better:

- Structured JSON logs.
- Error tracking.
- Metrics dashboard.
- Alert on repeated 500 errors.
- Alert on smoke test failure.

## 11. Smoke Test Gate

Run before each deploy:

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

Do not deploy if API health is unstable, any smoke check fails, Executive Pack ZIP validation fails, or DOCX template validation fails.

## 12. Release Process

1. Confirm working tree is clean.
2. Run full smoke test.
3. Commit changes.
4. Push to GitHub.
5. Create annotated tag.
6. Deploy.
7. Run smoke test against deployed URL.
8. Record release notes.

## 13. Recommended Next Engineering Tasks

Priority 1:

- Add Alembic migrations.
- Add login and RBAC.
- Add upload file limits and validation.
- Add export cleanup/retention.
- Add production `.env.example` guidance.

Priority 2:

- Add background job queue.
- Add project-level artifact versioning.
- Add API pagination.
- Add structured logging.
- Add monitoring and alerts.

Priority 3:

- Add multi-tenant workspace support.
- Add object storage integration.
- Add notification workflow for approvals and clarifications.
- Add richer proposal template builder.
