from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderRequirement
from app.models.response_plan import TenderResponseItem
from app.models.compliance_scorecard import TenderComplianceItem
from app.schemas.tender import (
    GenerateResponsePlanResponse,
    ResponseItemResponse,
    ResponseItemUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.response_plan_generator import generate_response_plan_items
from app.services.i18n_service import get_project_output_language, localize_response_plan_payload


router = APIRouter(tags=["response_plan"])


ALLOWED_COMPLIANCE = {
    "likely_compliant",
    "partially_compliant",
    "non_compliant",
    "needs_review",
    "needs_clarification",
    "blocked",
}

ALLOWED_STATUS = {
    "draft",
    "in_review",
    "ready",
    "approved",
    "blocked",
}


def snapshot_response_item(item: TenderResponseItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "requirement_id": item.requirement_id,
        "category": item.category,
        "requirement_text": item.requirement_text,
        "compliance_status": item.compliance_status,
        "response_strategy": item.response_strategy,
        "draft_response": item.draft_response,
        "evidence_needed": item.evidence_needed,
        "assumptions": item.assumptions,
        "risks": item.risks,
        "owner": item.owner,
        "status": item.status,
        "confidence": item.confidence,
        "source_page": item.source_page,
        "evidence_quote": item.evidence_quote,
        "notes": item.notes,
        "generation_mode": item.generation_mode,
    }



@router.post(
    "/api/v1/projects/{project_id}/generate-response-plan",
    response_model=GenerateResponsePlanResponse,
)
def generate_project_response_plan(
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
        .order_by(TenderRequirement.category.asc(), TenderRequirement.id.asc())
        .all()
    )

    if not requirements:
        raise HTTPException(status_code=400, detail="No requirements found. Run extraction first.")

    old_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .all()
    )

    # Compliance scorecard is a derived artifact from requirements/response/evidence.
    # Clear old scorecard rows before response items are regenerated to avoid FK/stale-reference conflicts.
    db.query(TenderComplianceItem).filter(
        TenderComplianceItem.project_id == project_id
    ).delete(synchronize_session=False)
    before = [snapshot_response_item(item) for item in old_items]

    db.query(TenderResponseItem).filter(
        TenderResponseItem.project_id == project_id
    ).delete(synchronize_session=False)

    generated_payloads = generate_response_plan_items(requirements)

    output_language = get_project_output_language(db, project_id)
    created = []

    for payload in generated_payloads:
        payload = localize_response_plan_payload(payload, output_language)
        item = TenderResponseItem(**payload)
        db.add(item)
        created.append(item)

    db.flush()

    after = [snapshot_response_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_response_plan",
        entity_type="response_plan_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after)},
        ip_address=request.client.host if request.client else None,
        notes="Response plan generated from requirement matrix",
    )

    db.commit()

    for item in created:
        db.refresh(item)

    return {
        "generated_count": len(created),
        "items": created,
    }


@router.get(
    "/api/v1/projects/{project_id}/response-plan",
    response_model=list[ResponseItemResponse],
)
def list_project_response_plan(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.category.asc(), TenderResponseItem.id.asc())
        .all()
    )


@router.patch(
    "/api/v1/response-items/{item_id}",
    response_model=ResponseItemResponse,
)
def update_response_item(
    item_id: int,
    payload: ResponseItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderResponseItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Response item not found")

    data = payload.model_dump(exclude_unset=True)

    if "compliance_status" in data and data["compliance_status"] not in ALLOWED_COMPLIANCE:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid compliance_status. Allowed: {sorted(ALLOWED_COMPLIANCE)}",
        )

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}",
        )

    before = snapshot_response_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_response_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_response_item",
        entity_type="response_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Response plan item updated",
    )

    db.commit()
    db.refresh(item)

    return item
