from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.models.response_plan import TenderResponseItem
from app.models.evidence_pack import TenderEvidenceItem
from app.models.decision_gate import TenderDecisionGate
from app.models.action_item import TenderActionItem
from app.schemas.tender import ActionItemResponse, ActionItemUpdate, GenerateActionItemsResponse
from app.services.action_item_generator import generate_action_item_payloads
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language


router = APIRouter(tags=["action_items"])


ALLOWED_PRIORITY = {"high", "medium", "low"}
ALLOWED_STATUS = {"open", "in_progress", "done", "blocked", "cancelled"}


def snapshot_action_item(item: TenderActionItem) -> dict:
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
        "related_proposal_section_ids": item.related_proposal_section_ids,
        "owner": item.owner,
        "priority": item.priority,
        "status": item.status,
        "due_date": item.due_date,
        "confidence": item.confidence,
        "notes": item.notes,
        "generation_mode": item.generation_mode,
    }


@router.post(
    "/api/v1/projects/{project_id}/generate-action-items",
    response_model=GenerateActionItemsResponse,
)
def generate_project_action_items(
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

    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .order_by(TenderClarificationQuestion.priority.desc(), TenderClarificationQuestion.id.asc())
        .all()
    )

    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.category.asc(), TenderResponseItem.id.asc())
        .all()
    )

    evidence_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .order_by(
            TenderEvidenceItem.priority.desc(),
            TenderEvidenceItem.evidence_category.asc(),
            TenderEvidenceItem.id.asc(),
        )
        .all()
    )

    decision_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    old_items = (
        db.query(TenderActionItem)
        .filter(TenderActionItem.project_id == project_id)
        .all()
    )
    before = [snapshot_action_item(item) for item in old_items]

    db.query(TenderActionItem).filter(
        TenderActionItem.project_id == project_id
    ).delete(synchronize_session=False)

    output_language = get_project_output_language(db, project_id)

    payloads = generate_action_item_payloads(
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        output_language=output_language,
    )

    created = []
    for payload in payloads:
        item = TenderActionItem(
            project_id=project_id,
            **payload,
        )
        db.add(item)
        created.append(item)

    db.flush()

    after = [snapshot_action_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_action_items",
        entity_type="action_item_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after)},
        ip_address=request.client.host if request.client else None,
        notes="Action items generated from tender artifacts",
    )

    db.commit()

    for item in created:
        db.refresh(item)

    return {
        "generated_count": len(created),
        "items": created,
    }


@router.get(
    "/api/v1/projects/{project_id}/action-items",
    response_model=list[ActionItemResponse],
)
def list_project_action_items(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderActionItem)
        .filter(TenderActionItem.project_id == project_id)
        .order_by(
            TenderActionItem.priority.asc(),
            TenderActionItem.status.asc(),
            TenderActionItem.owner.asc(),
            TenderActionItem.id.asc(),
        )
        .all()
    )


@router.patch(
    "/api/v1/action-items/{item_id}",
    response_model=ActionItemResponse,
)
def update_action_item(
    item_id: int,
    payload: ActionItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    data = payload.model_dump(exclude_unset=True)

    if "priority" in data and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}")

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    before = snapshot_action_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_action_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_action_item",
        entity_type="action_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Action item updated",
    )

    db.commit()
    db.refresh(item)

    return item
