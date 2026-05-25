from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.models.response_plan import TenderResponseItem
from app.models.evidence_pack import TenderEvidenceItem
from app.models.decision_gate import TenderDecisionGate
from app.models.risk_item import TenderRiskItem
from app.schemas.tender import RiskItemResponse, RiskItemUpdate, GenerateRiskRegisterResponse
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language
from app.services.risk_register_generator import generate_risk_item_payloads


router = APIRouter(tags=["risk_register"])


ALLOWED_LEVELS = {"high", "medium", "low"}
ALLOWED_SEVERITY = {"critical", "high", "medium", "low"}
ALLOWED_STATUS = {"open", "mitigating", "monitored", "accepted", "closed", "escalated"}


def snapshot_risk_item(item: TenderRiskItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "title": item.title,
        "description": item.description,
        "source_type": item.source_type,
        "source_id": item.source_id,
        "related_requirement_ids": item.related_requirement_ids,
        "related_response_item_ids": item.related_response_item_ids,
        "related_clarification_ids": item.related_clarification_ids,
        "related_evidence_item_ids": item.related_evidence_item_ids,
        "risk_category": item.risk_category,
        "impact_area": item.impact_area,
        "probability": item.probability,
        "impact": item.impact,
        "severity": item.severity,
        "owner": item.owner,
        "status": item.status,
        "due_date": item.due_date,
        "mitigation_plan": item.mitigation_plan,
        "contingency_plan": item.contingency_plan,
        "trigger_event": item.trigger_event,
        "confidence": item.confidence,
        "notes": item.notes,
        "generation_mode": item.generation_mode,
    }


@router.post(
    "/api/v1/projects/{project_id}/generate-risk-register",
    response_model=GenerateRiskRegisterResponse,
)
def generate_project_risk_register(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    requirements = (
        db.query(TenderRequirement)
        .filter(TenderRequirement.project_id == project_id)
        .order_by(TenderRequirement.risk_level.desc(), TenderRequirement.priority.desc(), TenderRequirement.id.asc())
        .all()
    )

    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .order_by(TenderClarificationQuestion.priority.desc(), TenderClarificationQuestion.id.asc())
        .all()
    )

    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.compliance_status.desc(), TenderResponseItem.id.asc())
        .all()
    )

    evidence_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .order_by(TenderEvidenceItem.priority.desc(), TenderEvidenceItem.id.asc())
        .all()
    )

    decision_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    old_items = (
        db.query(TenderRiskItem)
        .filter(TenderRiskItem.project_id == project_id)
        .all()
    )
    before = [snapshot_risk_item(item) for item in old_items]

    db.query(TenderRiskItem).filter(
        TenderRiskItem.project_id == project_id
    ).delete(synchronize_session=False)

    output_language = get_project_output_language(db, project_id)

    payloads = generate_risk_item_payloads(
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        output_language=output_language,
    )

    created = []
    for payload in payloads:
        item = TenderRiskItem(project_id=project_id, **payload)
        db.add(item)
        created.append(item)

    db.flush()

    after = [snapshot_risk_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_risk_register",
        entity_type="risk_item_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after)},
        ip_address=request.client.host if request.client else None,
        notes="Risk register generated from tender artifacts",
    )

    db.commit()

    for item in created:
        db.refresh(item)

    return {
        "generated_count": len(created),
        "items": created,
    }


@router.get(
    "/api/v1/projects/{project_id}/risk-register",
    response_model=list[RiskItemResponse],
)
def list_project_risk_register(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderRiskItem)
        .filter(TenderRiskItem.project_id == project_id)
        .order_by(
            TenderRiskItem.severity.asc(),
            TenderRiskItem.status.asc(),
            TenderRiskItem.owner.asc(),
            TenderRiskItem.id.asc(),
        )
        .all()
    )


@router.patch(
    "/api/v1/risk-items/{item_id}",
    response_model=RiskItemResponse,
)
def update_risk_item(
    item_id: int,
    payload: RiskItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderRiskItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Risk item not found")

    data = payload.model_dump(exclude_unset=True)

    if "probability" in data and data["probability"] not in ALLOWED_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid probability. Allowed: {sorted(ALLOWED_LEVELS)}")

    if "impact" in data and data["impact"] not in ALLOWED_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid impact. Allowed: {sorted(ALLOWED_LEVELS)}")

    if "severity" in data and data["severity"] not in ALLOWED_SEVERITY:
        raise HTTPException(status_code=400, detail=f"Invalid severity. Allowed: {sorted(ALLOWED_SEVERITY)}")

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    before = snapshot_risk_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_risk_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_risk_item",
        entity_type="risk_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Risk item updated",
    )

    db.commit()
    db.refresh(item)

    return item
