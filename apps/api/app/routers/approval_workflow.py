from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.decision_gate import TenderDecisionGate
from app.models.compliance_scorecard import TenderComplianceItem
from app.models.risk_item import TenderRiskItem
from app.models.action_item import TenderActionItem
from app.models.approval_workflow import TenderApprovalRequest, TenderApprovalStep
from app.schemas.tender import (
    ApprovalStepResponse,
    ApprovalStepUpdate,
    ApprovalWorkflowResponse,
    ApprovalWorkflowSubmit,
    GenerateApprovalWorkflowResponse,
)
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language
from app.services.approval_workflow_generator import (
    build_approval_summary,
    generate_approval_workflow_payload,
)


router = APIRouter(tags=["approval_workflow"])

ALLOWED_REQUEST_STATUS = {"draft", "pending", "approved", "rejected", "changes_requested", "superseded"}
ALLOWED_STEP_STATUS = {"not_started", "pending", "approved", "rejected", "changes_requested", "skipped"}


def snapshot_request(request: TenderApprovalRequest | None, steps: list[TenderApprovalStep] | None = None) -> dict | None:
    if not request:
        return None

    return {
        "id": request.id,
        "project_id": request.project_id,
        "title": request.title,
        "description": request.description,
        "status": request.status,
        "current_step_order": request.current_step_order,
        "total_steps": request.total_steps,
        "approved_steps": request.approved_steps,
        "submitted_by": request.submitted_by,
        "submitted_at": request.submitted_at.isoformat() if request.submitted_at else None,
        "completed_at": request.completed_at.isoformat() if request.completed_at else None,
        "final_decision": request.final_decision,
        "notes": request.notes,
        "generation_mode": request.generation_mode,
        "steps": [snapshot_step(item) for item in (steps or [])],
    }


def snapshot_step(step: TenderApprovalStep) -> dict:
    return {
        "id": step.id,
        "project_id": step.project_id,
        "approval_request_id": step.approval_request_id,
        "step_order": step.step_order,
        "role": step.role,
        "approver_name": step.approver_name,
        "approver_email": step.approver_email,
        "status": step.status,
        "due_date": step.due_date,
        "decision_note": step.decision_note,
        "decided_by": step.decided_by,
        "decided_at": step.decided_at.isoformat() if step.decided_at else None,
    }


def latest_request(db: Session, project_id: int) -> TenderApprovalRequest | None:
    return (
        db.query(TenderApprovalRequest)
        .filter(TenderApprovalRequest.project_id == project_id)
        .order_by(TenderApprovalRequest.id.desc())
        .first()
    )


def request_steps(db: Session, request_id: int) -> list[TenderApprovalStep]:
    return (
        db.query(TenderApprovalStep)
        .filter(TenderApprovalStep.approval_request_id == request_id)
        .order_by(TenderApprovalStep.step_order.asc(), TenderApprovalStep.id.asc())
        .all()
    )


def response_payload(request: TenderApprovalRequest, steps: list[TenderApprovalStep]) -> dict:
    return {
        "summary": build_approval_summary(request, steps),
        "request": request,
        "steps": steps,
    }


def refresh_request_rollup(request: TenderApprovalRequest, steps: list[TenderApprovalStep]):
    request.total_steps = len(steps)
    request.approved_steps = len([item for item in steps if item.status == "approved"])

    pending = next((item for item in steps if item.status == "pending"), None)
    request.current_step_order = pending.step_order if pending else None

    if any(item.status == "rejected" for item in steps):
        request.status = "rejected"
        request.final_decision = "rejected"
        request.completed_at = datetime.utcnow()
    elif any(item.status == "changes_requested" for item in steps):
        request.status = "changes_requested"
        request.final_decision = "changes_requested"
        request.completed_at = datetime.utcnow()
    elif steps and all(item.status in {"approved", "skipped"} for item in steps):
        request.status = "approved"
        request.final_decision = "approved"
        request.completed_at = datetime.utcnow()
    elif request.status != "draft":
        request.status = "pending"
        request.final_decision = None
        request.completed_at = None

    request.updated_at = datetime.utcnow()


@router.post(
    "/api/v1/projects/{project_id}/generate-approval-workflow",
    response_model=GenerateApprovalWorkflowResponse,
)
def generate_project_approval_workflow(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing = latest_request(db, project_id)
    existing_steps = request_steps(db, existing.id) if existing else []

    decision_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    compliance_items = (
        db.query(TenderComplianceItem)
        .filter(TenderComplianceItem.project_id == project_id)
        .all()
    )

    risk_items = (
        db.query(TenderRiskItem)
        .filter(TenderRiskItem.project_id == project_id)
        .all()
    )

    action_items = (
        db.query(TenderActionItem)
        .filter(TenderActionItem.project_id == project_id)
        .all()
    )

    output_language = get_project_output_language(db, project_id)

    payload = generate_approval_workflow_payload(
        project=project,
        decision_gate=decision_gate,
        compliance_items=compliance_items,
        risk_items=risk_items,
        action_items=action_items,
        output_language=output_language,
    )

    approval_request = TenderApprovalRequest(project_id=project_id, **payload["request"])
    db.add(approval_request)
    db.flush()

    steps = []
    for step_payload in payload["steps"]:
        step = TenderApprovalStep(
            project_id=project_id,
            approval_request_id=approval_request.id,
            **step_payload,
        )
        db.add(step)
        steps.append(step)

    db.flush()
    refresh_request_rollup(approval_request, steps)

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_approval_workflow",
        entity_type="approval_workflow",
        entity_id=approval_request.id,
        before_json=snapshot_request(existing, existing_steps),
        after_json=snapshot_request(approval_request, steps),
        ip_address=request.client.host if request.client else None,
        notes="Approval workflow generated from decision gate, compliance, risks, and actions",
    )

    db.commit()
    db.refresh(approval_request)
    for step in steps:
        db.refresh(step)

    return response_payload(approval_request, steps)


@router.get(
    "/api/v1/projects/{project_id}/approval-workflow",
    response_model=ApprovalWorkflowResponse,
)
def get_project_approval_workflow(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    approval_request = latest_request(db, project_id)
    if not approval_request:
        raise HTTPException(status_code=404, detail="Approval workflow not generated yet")

    steps = request_steps(db, approval_request.id)
    return response_payload(approval_request, steps)


@router.post(
    "/api/v1/approval-workflows/{workflow_id}/submit",
    response_model=ApprovalWorkflowResponse,
)
def submit_approval_workflow(
    workflow_id: int,
    payload: ApprovalWorkflowSubmit,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    approval_request = db.get(TenderApprovalRequest, workflow_id)
    if not approval_request:
        raise HTTPException(status_code=404, detail="Approval workflow not found")

    steps = request_steps(db, approval_request.id)
    if not steps:
        raise HTTPException(status_code=400, detail="Approval workflow has no steps")

    before = snapshot_request(approval_request, steps)

    approval_request.status = "pending"
    approval_request.submitted_by = payload.submitted_by or x_actor
    approval_request.submitted_at = datetime.utcnow()
    approval_request.notes = payload.notes if payload.notes is not None else approval_request.notes

    if not any(step.status == "pending" for step in steps):
        for step in steps:
            if step.status == "not_started":
                step.status = "pending"
                step.updated_at = datetime.utcnow()
                break

    refresh_request_rollup(approval_request, steps)

    db.flush()
    after = snapshot_request(approval_request, steps)

    create_audit_log(
        db,
        project_id=approval_request.project_id,
        actor=x_actor,
        action="submit_approval_workflow",
        entity_type="approval_workflow",
        entity_id=approval_request.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Approval workflow submitted",
    )

    db.commit()
    db.refresh(approval_request)
    steps = request_steps(db, approval_request.id)

    return response_payload(approval_request, steps)


@router.patch(
    "/api/v1/approval-steps/{step_id}",
    response_model=ApprovalStepResponse,
)
def update_approval_step(
    step_id: int,
    payload: ApprovalStepUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    step = db.get(TenderApprovalStep, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Approval step not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in ALLOWED_STEP_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STEP_STATUS)}")

    approval_request = db.get(TenderApprovalRequest, step.approval_request_id)
    if not approval_request:
        raise HTTPException(status_code=404, detail="Approval workflow not found")

    steps = request_steps(db, approval_request.id)
    before = {
        "request": snapshot_request(approval_request, steps),
        "step": snapshot_step(step),
    }

    for field, value in data.items():
        setattr(step, field, value)

    if "status" in data and data["status"] in {"approved", "rejected", "changes_requested", "skipped"}:
        step.decided_by = data.get("decided_by") or x_actor
        step.decided_at = datetime.utcnow()

    step.updated_at = datetime.utcnow()
    db.flush()

    steps = request_steps(db, approval_request.id)

    if step.status == "approved":
        next_step = next((item for item in steps if item.step_order > step.step_order and item.status == "not_started"), None)
        if next_step and not any(item.status == "pending" for item in steps if item.id != next_step.id):
            next_step.status = "pending"
            next_step.updated_at = datetime.utcnow()

    refresh_request_rollup(approval_request, steps)
    db.flush()
    steps = request_steps(db, approval_request.id)

    after = {
        "request": snapshot_request(approval_request, steps),
        "step": snapshot_step(step),
    }

    create_audit_log(
        db,
        project_id=step.project_id,
        actor=x_actor,
        action="update_approval_step",
        entity_type="approval_step",
        entity_id=step.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Approval step updated",
    )

    db.commit()
    db.refresh(step)

    return step
