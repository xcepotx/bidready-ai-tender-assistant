from datetime import datetime, timezone

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from app.db.session import Base, engine
from app.models import tender  # noqa: F401
from app.models import clarification  # noqa: F401
from app.models import audit  # noqa: F401
from app.models import project_metadata  # noqa: F401
from app.models import response_plan  # noqa: F401
from app.models import proposal_outline  # noqa: F401
from app.models import evidence_pack  # noqa: F401
from app.models import decision_gate  # noqa: F401
from app.models import project_language  # noqa: F401
from app.models import action_item  # noqa: F401
from app.models import risk_item  # noqa: F401
from app.models import compliance_scorecard  # noqa: F401
from app.models import approval_workflow  # noqa: F401
from app.models import addendum_impact  # noqa: F401
from app.models import clarification_response_tracker  # noqa: F401
from app.routers.projects import router as projects_router
from app.routers.requirements import router as requirements_router
from app.routers.clarifications import router as clarifications_router
from app.routers.audit_logs import router as audit_logs_router
from app.routers.ai import router as ai_router
from app.routers.metadata import router as metadata_router
from app.routers.response_plan import router as response_plan_router
from app.routers.proposal_outline import router as proposal_outline_router
from app.routers.evidence_pack import router as evidence_pack_router
from app.routers.decision_gate import router as decision_gate_router
from app.routers.project_language import router as project_language_router
from app.routers.action_items import router as action_items_router
from app.routers.risk_register import router as risk_register_router
from app.routers.compliance_scorecard import router as compliance_scorecard_router
from app.routers.approval_workflow import router as approval_workflow_router
from app.routers.decision_gate_history import router as decision_gate_history_router
from app.routers.addendum_impact import router as addendum_impact_router
from app.routers.clarification_response_tracker import router as clarification_response_tracker_router
from app.security.internal_key import require_internal_api_key


app = FastAPI(
    title="Bid Readiness Assistant API",
    version="0.3.0",
)


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def health_payload():
    return HealthResponse(
        status="ok",
        service="bid-readiness-api",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/health", response_model=HealthResponse)
def health():
    return health_payload()


@app.get("/api/health", response_model=HealthResponse)
def api_health():
    return health_payload()


@app.get("/api/v1/ready")
def ready():
    return {
        "status": "ready",
        "modules": {
            "api": "ok",
            "document_intake": "ok",
            "requirement_extraction": "ok",
            "review_workflow": "ok",
            "exports": "ok",
        },
    }


app.include_router(projects_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(requirements_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(clarifications_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(audit_logs_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(ai_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(metadata_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(response_plan_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(proposal_outline_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(evidence_pack_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(decision_gate_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(project_language_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(action_items_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(risk_register_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(compliance_scorecard_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(approval_workflow_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(decision_gate_history_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(addendum_impact_router, dependencies=[Depends(require_internal_api_key)])
app.include_router(clarification_response_tracker_router, dependencies=[Depends(require_internal_api_key)])
