from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.clarification import TenderClarificationQuestion
from app.models.response_plan import TenderResponseItem
from app.models.compliance_scorecard import TenderComplianceItem
from app.models.risk_item import TenderRiskItem
from app.models.addendum_impact import TenderAddendumImpactItem
from app.models.clarification_response_tracker import TenderClarificationResponseItem
from app.schemas.tender import (
    ClarificationResponseTrackerResponse,
    ClarificationResponseGenerateResponse,
    ClarificationResponseItemResponse,
    ClarificationResponseItemUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language
from app.services.clarification_response_tracker_generator import (
    build_clarification_response_summary,
    generate_clarification_response_payloads,
)


router = APIRouter(tags=["clarification_response_tracker"])

ALLOWED_STATUS = {"open", "sent", "answered", "incorporated", "closed", "overdue"}
ALLOWED_PRIORITY = {"high", "medium", "low"}
ALLOWED_RISK = {"high", "medium", "low"}


def snapshot_item(item: TenderClarificationResponseItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "clarification_id": item.clarification_id,
        "requirement_id": item.requirement_id,
        "category": item.category,
        "question_text": item.question_text,
        "reason": item.reason,
        "client_response": item.client_response,
        "response_status": item.response_status,
        "priority": item.priority,
        "risk_level": item.risk_level,
        "owner": item.owner,
        "due_date": item.due_date,
        "sent_at": item.sent_at,
        "response_received_at": item.response_received_at,
        "incorporated_at": item.incorporated_at,
        "impacted_artifacts": item.impacted_artifacts,
        "related_response_item_ids": item.related_response_item_ids,
        "related_compliance_item_ids": item.related_compliance_item_ids,
        "related_risk_item_ids": item.related_risk_item_ids,
        "related_addendum_impact_ids": item.related_addendum_impact_ids,
        "recommended_follow_up": item.recommended_follow_up,
        "notes": item.notes,
        "confidence": item.confidence,
        "generation_mode": item.generation_mode,
    }


def summary_from_items(items: list[TenderClarificationResponseItem]) -> dict:
    return build_clarification_response_summary([
        {
            "response_status": item.response_status,
            "priority": item.priority,
            "risk_level": item.risk_level,
        }
        for item in items
    ])


@router.post(
    "/api/v1/projects/{project_id}/generate-clarification-response-tracker",
    response_model=ClarificationResponseGenerateResponse,
)
def generate_project_clarification_response_tracker(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .order_by(TenderClarificationQuestion.priority.desc(), TenderClarificationQuestion.id.asc())
        .all()
    )

    if not clarifications:
        raise HTTPException(status_code=400, detail="No clarifications found. Generate clarifications first.")

    old_items = (
        db.query(TenderClarificationResponseItem)
        .filter(TenderClarificationResponseItem.project_id == project_id)
        .all()
    )
    before = [snapshot_item(item) for item in old_items]

    db.query(TenderClarificationResponseItem).filter(
        TenderClarificationResponseItem.project_id == project_id
    ).delete(synchronize_session=False)

    response_items = db.query(TenderResponseItem).filter(TenderResponseItem.project_id == project_id).all()
    compliance_items = db.query(TenderComplianceItem).filter(TenderComplianceItem.project_id == project_id).all()
    risk_items = db.query(TenderRiskItem).filter(TenderRiskItem.project_id == project_id).all()
    addendum_impacts = db.query(TenderAddendumImpactItem).filter(TenderAddendumImpactItem.project_id == project_id).all()

    output_language = get_project_output_language(db, project_id)

    payloads = generate_clarification_response_payloads(
        clarifications=clarifications,
        response_items=response_items,
        compliance_items=compliance_items,
        risk_items=risk_items,
        addendum_impacts=addendum_impacts,
        output_language=output_language,
    )

    created = []
    for payload in payloads:
        item = TenderClarificationResponseItem(project_id=project_id, **payload)
        db.add(item)
        created.append(item)

    db.flush()

    summary = build_clarification_response_summary(payloads)
    after = [snapshot_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_clarification_response_tracker",
        entity_type="clarification_response_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after), "summary": summary},
        ip_address=request.client.host if request.client else None,
        notes="Clarification response tracker generated from clarification questions and related artifacts",
    )

    db.commit()

    for item in created:
        db.refresh(item)

    return {
        "generated_count": len(created),
        "summary": summary,
        "items": created,
    }


@router.get(
    "/api/v1/projects/{project_id}/clarification-response-tracker",
    response_model=ClarificationResponseTrackerResponse,
)
def get_project_clarification_response_tracker(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    items = (
        db.query(TenderClarificationResponseItem)
        .filter(TenderClarificationResponseItem.project_id == project_id)
        .order_by(
            TenderClarificationResponseItem.response_status.asc(),
            TenderClarificationResponseItem.priority.desc(),
            TenderClarificationResponseItem.id.asc(),
        )
        .all()
    )

    return {
        "summary": summary_from_items(items),
        "items": items,
    }


@router.patch(
    "/api/v1/clarification-response-items/{item_id}",
    response_model=ClarificationResponseItemResponse,
)
def update_clarification_response_item(
    item_id: int,
    payload: ClarificationResponseItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderClarificationResponseItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clarification response item not found")

    data = payload.model_dump(exclude_unset=True)

    if "response_status" in data and data["response_status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid response_status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "priority" in data and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}")

    if "risk_level" in data and data["risk_level"] not in ALLOWED_RISK:
        raise HTTPException(status_code=400, detail=f"Invalid risk_level. Allowed: {sorted(ALLOWED_RISK)}")

    before = snapshot_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    if data.get("response_status") == "answered" and not item.response_received_at:
        item.response_received_at = datetime.utcnow().isoformat()

    if data.get("response_status") == "incorporated" and not item.incorporated_at:
        item.incorporated_at = datetime.utcnow().isoformat()

    item.updated_at = datetime.utcnow()
    db.flush()

    after = snapshot_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_clarification_response_item",
        entity_type="clarification_response_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Clarification response tracker item updated",
    )

    db.commit()
    db.refresh(item)

    return item
