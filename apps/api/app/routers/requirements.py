from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderRequirement, TenderDocument, DocumentPage
from app.schemas.tender import RequirementResponse, RequirementUpdate, RequirementEvidenceResponse, RequirementBulkUpdate, BulkUpdateResponse
from app.services.audit_service import create_audit_log


router = APIRouter(prefix="/api/v1/requirements", tags=["requirements"])


ALLOWED_STATUS = {
    "needs_review",
    "accepted",
    "rejected",
    "done",
    "blocked",
    "not_applicable",
    "needs_clarification",
}

ALLOWED_RISK = {
    "low",
    "medium",
    "high",
}

ALLOWED_PRIORITY = {
    "mandatory",
    "optional",
    "needs_review",
}


def snapshot_requirement(requirement: TenderRequirement) -> dict:
    return {
        "id": requirement.id,
        "project_id": requirement.project_id,
        "document_id": requirement.document_id,
        "category": requirement.category,
        "requirement_text": requirement.requirement_text,
        "priority": requirement.priority,
        "risk_level": requirement.risk_level,
        "source_page": requirement.source_page,
        "evidence_quote": requirement.evidence_quote,
        "confidence": requirement.confidence,
        "suggested_owner": requirement.suggested_owner,
        "status": requirement.status,
        "notes": requirement.notes,
    }




@router.get("/{requirement_id}/evidence", response_model=RequirementEvidenceResponse)
def get_requirement_evidence(
    requirement_id: int,
    db: Session = Depends(get_db),
):
    requirement = db.get(TenderRequirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    document = None
    page = None

    if requirement.document_id:
        document = db.get(TenderDocument, requirement.document_id)

        if requirement.source_page:
            page = (
                db.query(DocumentPage)
                .filter(DocumentPage.document_id == requirement.document_id)
                .filter(DocumentPage.page_number == requirement.source_page)
                .first()
            )

    return {
        "requirement_id": requirement.id,
        "project_id": requirement.project_id,
        "document_id": requirement.document_id,
        "filename": document.filename if document else None,
        "source_page": requirement.source_page,
        "evidence_quote": requirement.evidence_quote,
        "page_text": page.text if page else None,
    }



@router.patch("/bulk-update", response_model=BulkUpdateResponse)
def bulk_update_requirements(
    payload: RequirementBulkUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    if not payload.requirement_ids:
        raise HTTPException(status_code=400, detail="requirement_ids is required")

    data = payload.model_dump(exclude_unset=True)
    ids = data.pop("requirement_ids", [])

    if "status" in data and data["status"] is not None and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "risk_level" in data and data["risk_level"] is not None and data["risk_level"] not in ALLOWED_RISK:
        raise HTTPException(status_code=400, detail=f"Invalid risk_level. Allowed: {sorted(ALLOWED_RISK)}")

    if "priority" in data and data["priority"] is not None and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}")

    patch = {key: value for key, value in data.items() if value is not None}

    if not patch:
        raise HTTPException(status_code=400, detail="No update fields provided")

    requirements = (
        db.query(TenderRequirement)
        .filter(TenderRequirement.id.in_(ids))
        .all()
    )

    if not requirements:
        raise HTTPException(status_code=404, detail="No matching requirements found")

    project_ids = {item.project_id for item in requirements}
    project_id = list(project_ids)[0] if len(project_ids) == 1 else None

    before = [snapshot_requirement(item) for item in requirements]

    for requirement in requirements:
        for field, value in patch.items():
            setattr(requirement, field, value)

    db.flush()

    after = [snapshot_requirement(item) for item in requirements]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="bulk_update_requirements",
        entity_type="requirement_batch",
        entity_id=None,
        before_json={"items": before},
        after_json={"items": after, "patch": patch},
        ip_address=request.client.host if request.client else None,
        notes=f"Bulk updated {len(requirements)} requirement(s)",
    )

    db.commit()

    return {
        "updated_count": len(requirements),
        "ids": [item.id for item in requirements],
    }

@router.patch("/{requirement_id}", response_model=RequirementResponse)
def update_requirement(
    requirement_id: int,
    payload: RequirementUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    requirement = db.get(TenderRequirement, requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}",
        )

    if "risk_level" in data and data["risk_level"] not in ALLOWED_RISK:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid risk_level. Allowed: {sorted(ALLOWED_RISK)}",
        )

    if "priority" in data and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}",
        )

    before = snapshot_requirement(requirement)

    for field, value in data.items():
        setattr(requirement, field, value)

    db.flush()

    after = snapshot_requirement(requirement)

    create_audit_log(
        db,
        project_id=requirement.project_id,
        actor=x_actor,
        action="update_requirement",
        entity_type="requirement",
        entity_id=requirement.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Requirement updated from API",
    )

    db.commit()
    db.refresh(requirement)

    return requirement
