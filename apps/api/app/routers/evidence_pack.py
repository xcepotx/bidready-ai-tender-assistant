from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.project_metadata import TenderProjectMetadata
from app.models.response_plan import TenderResponseItem
from app.models.proposal_outline import TenderProposalSection
from app.models.evidence_pack import TenderEvidenceItem
from app.schemas.tender import (
    EvidenceItemResponse,
    EvidenceItemUpdate,
    GenerateEvidencePackResponse,
)
from app.services.audit_service import create_audit_log
from app.services.evidence_pack_generator import generate_evidence_pack_items
from app.services.i18n_service import get_project_output_language, localize_payload


router = APIRouter(tags=["evidence_pack"])


ALLOWED_STATUS = {
    "open",
    "requested",
    "received",
    "validated",
    "not_applicable",
    "blocked",
}

ALLOWED_PRIORITY = {
    "low",
    "medium",
    "high",
}


def snapshot_evidence_item(item: TenderEvidenceItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "evidence_name": item.evidence_name,
        "evidence_category": item.evidence_category,
        "owner": item.owner,
        "status": item.status,
        "priority": item.priority,
        "source_type": item.source_type,
        "source_ids": item.source_ids,
        "related_requirement_ids": item.related_requirement_ids,
        "related_response_item_ids": item.related_response_item_ids,
        "related_proposal_section_ids": item.related_proposal_section_ids,
        "notes": item.notes,
        "generation_mode": item.generation_mode,
    }


@router.post(
    "/api/v1/projects/{project_id}/generate-evidence-pack",
    response_model=GenerateEvidencePackResponse,
)
def generate_project_evidence_pack(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    metadata = (
        db.query(TenderProjectMetadata)
        .filter(TenderProjectMetadata.project_id == project_id)
        .order_by(TenderProjectMetadata.id.desc())
        .first()
    )

    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.category.asc(), TenderResponseItem.id.asc())
        .all()
    )

    proposal_sections = (
        db.query(TenderProposalSection)
        .filter(TenderProposalSection.project_id == project_id)
        .order_by(TenderProposalSection.section_order.asc(), TenderProposalSection.id.asc())
        .all()
    )

    if not metadata and not response_items and not proposal_sections:
        raise HTTPException(
            status_code=400,
            detail="No metadata, response plan, or proposal outline found. Generate upstream artifacts first.",
        )

    old_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .all()
    )
    before = [snapshot_evidence_item(item) for item in old_items]

    db.query(TenderEvidenceItem).filter(
        TenderEvidenceItem.project_id == project_id
    ).delete(synchronize_session=False)

    generated_payloads = generate_evidence_pack_items(
        metadata=metadata,
        response_items=response_items,
        proposal_sections=proposal_sections,
    )

    output_language = get_project_output_language(db, project_id)
    generated_payloads = localize_payload(generated_payloads, output_language)

    created = []

    for payload in generated_payloads:
        item = TenderEvidenceItem(
            project_id=project_id,
            **payload,
        )
        db.add(item)
        created.append(item)

    db.flush()

    after = [snapshot_evidence_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_evidence_pack",
        entity_type="evidence_pack_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after)},
        ip_address=request.client.host if request.client else None,
        notes="Evidence pack generated from metadata, response plan, and proposal outline",
    )

    db.commit()

    for item in created:
        db.refresh(item)

    return {
        "generated_count": len(created),
        "items": created,
    }


@router.get(
    "/api/v1/projects/{project_id}/evidence-pack",
    response_model=list[EvidenceItemResponse],
)
def list_project_evidence_pack(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .order_by(TenderEvidenceItem.priority.desc(), TenderEvidenceItem.evidence_category.asc(), TenderEvidenceItem.id.asc())
        .all()
    )


@router.patch(
    "/api/v1/evidence-items/{item_id}",
    response_model=EvidenceItemResponse,
)
def update_evidence_item(
    item_id: int,
    payload: EvidenceItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderEvidenceItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence item not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "priority" in data and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}")

    before = snapshot_evidence_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_evidence_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_evidence_item",
        entity_type="evidence_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Evidence pack item updated",
    )

    db.commit()
    db.refresh(item)

    return item
