from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderDocument, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.models.project_metadata import TenderProjectMetadata
from app.models.response_plan import TenderResponseItem
from app.models.proposal_outline import TenderProposalSection
from app.models.evidence_pack import TenderEvidenceItem
from app.models.decision_gate import TenderDecisionGate
from app.schemas.tender import (
    DecisionGateResponse,
    DecisionGateUpdate,
    GenerateDecisionGateResponse,
)
from app.services.audit_service import create_audit_log
from app.services.readiness_service import compute_readiness_summary
from app.services.decision_gate_generator import generate_decision_gate_payload
from app.services.i18n_service import get_project_output_language, localize_payload


router = APIRouter(tags=["decision_gate"])


ALLOWED_DECISION_STATUS = {
    "recommend_bid",
    "recommend_no_bid",
    "needs_executive_review",
    "approved_to_bid",
    "no_bid",
    "deferred",
}


def snapshot_decision_gate(gate: TenderDecisionGate) -> dict:
    return {
        "id": gate.id,
        "project_id": gate.project_id,
        "decision_status": gate.decision_status,
        "recommendation": gate.recommendation,
        "readiness_score": gate.readiness_score,
        "confidence": gate.confidence,
        "executive_summary": gate.executive_summary,
        "key_reasons": gate.key_reasons,
        "blockers": gate.blockers,
        "required_approvals": gate.required_approvals,
        "next_actions": gate.next_actions,
        "owner": gate.owner,
        "due_date": gate.due_date,
        "notes": gate.notes,
        "generation_mode": gate.generation_mode,
    }


@router.post(
    "/api/v1/projects/{project_id}/generate-decision-gate",
    response_model=GenerateDecisionGateResponse,
)
def generate_project_decision_gate(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = (
        db.query(TenderDocument)
        .filter(TenderDocument.project_id == project_id)
        .all()
    )

    requirements = (
        db.query(TenderRequirement)
        .filter(TenderRequirement.project_id == project_id)
        .all()
    )

    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .all()
    )

    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .all()
    )

    proposal_sections = (
        db.query(TenderProposalSection)
        .filter(TenderProposalSection.project_id == project_id)
        .all()
    )

    evidence_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .all()
    )

    metadata = (
        db.query(TenderProjectMetadata)
        .filter(TenderProjectMetadata.project_id == project_id)
        .order_by(TenderProjectMetadata.id.desc())
        .first()
    )

    readiness_summary = compute_readiness_summary(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
    )

    payload = generate_decision_gate_payload(
        project=project,
        readiness_summary=readiness_summary,
        metadata=metadata,
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        proposal_sections=proposal_sections,
        evidence_items=evidence_items,
    )

    output_language = get_project_output_language(db, project_id)
    payload = localize_payload(payload, output_language)

    old_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    before_json = snapshot_decision_gate(old_gate) if old_gate else None

    if old_gate:
        db.delete(old_gate)
        db.flush()

    gate = TenderDecisionGate(
        project_id=project_id,
        **payload,
    )

    db.add(gate)
    db.flush()

    after_json = snapshot_decision_gate(gate)

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_decision_gate",
        entity_type="decision_gate",
        entity_id=gate.id,
        before_json=before_json,
        after_json=after_json,
        ip_address=request.client.host if request.client else None,
        notes="Decision gate generated from readiness and bid artifacts",
    )

    db.commit()
    db.refresh(gate)

    return {
        "gate": gate,
    }


@router.get(
    "/api/v1/projects/{project_id}/decision-gate",
    response_model=DecisionGateResponse,
)
def get_project_decision_gate(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    if not gate:
        raise HTTPException(status_code=404, detail="Decision gate not generated yet")

    return gate


@router.patch(
    "/api/v1/decision-gates/{gate_id}",
    response_model=DecisionGateResponse,
)
def update_decision_gate(
    gate_id: int,
    payload: DecisionGateUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    gate = db.get(TenderDecisionGate, gate_id)
    if not gate:
        raise HTTPException(status_code=404, detail="Decision gate not found")

    data = payload.model_dump(exclude_unset=True)

    if "decision_status" in data and data["decision_status"] not in ALLOWED_DECISION_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision_status. Allowed: {sorted(ALLOWED_DECISION_STATUS)}",
        )

    before = snapshot_decision_gate(gate)

    for field, value in data.items():
        setattr(gate, field, value)

    gate.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_decision_gate(gate)

    create_audit_log(
        db,
        project_id=gate.project_id,
        actor=x_actor,
        action="update_decision_gate",
        entity_type="decision_gate",
        entity_id=gate.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Decision gate updated",
    )

    db.commit()
    db.refresh(gate)

    return gate
