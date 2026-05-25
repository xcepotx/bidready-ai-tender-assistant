from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit import AuditLog
from app.models.tender import TenderProject
from app.models.decision_gate import TenderDecisionGate
from app.models.approval_workflow import TenderApprovalRequest, TenderApprovalStep
from app.schemas.tender import DecisionGateApprovalHistoryResponse
from app.services.decision_gate_history_builder import (
    APPROVAL_ACTIONS,
    DECISION_ACTIONS,
    build_decision_gate_history_events,
    build_decision_gate_history_summary,
)


router = APIRouter(tags=["decision_gate_history"])


@router.get(
    "/api/v1/projects/{project_id}/decision-gate-history",
    response_model=DecisionGateApprovalHistoryResponse,
)
def get_project_decision_gate_history(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.project_id == project_id)
        .filter(AuditLog.action.in_(sorted(DECISION_ACTIONS | APPROVAL_ACTIONS)))
        .order_by(AuditLog.id.desc())
        .limit(300)
        .all()
    )

    decision_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    approval_request = (
        db.query(TenderApprovalRequest)
        .filter(TenderApprovalRequest.project_id == project_id)
        .order_by(TenderApprovalRequest.id.desc())
        .first()
    )

    approval_steps = []
    if approval_request:
        approval_steps = (
            db.query(TenderApprovalStep)
            .filter(TenderApprovalStep.approval_request_id == approval_request.id)
            .order_by(TenderApprovalStep.step_order.asc(), TenderApprovalStep.id.asc())
            .all()
        )

    events = build_decision_gate_history_events(audit_logs)
    summary = build_decision_gate_history_summary(
        events=events,
        decision_gate=decision_gate,
        approval_request=approval_request,
        approval_steps=approval_steps,
    )

    return {
        "summary": summary,
        "events": events,
    }
