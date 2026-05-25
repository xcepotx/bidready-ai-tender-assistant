from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderRequirement
from app.models.response_plan import TenderResponseItem
from app.models.evidence_pack import TenderEvidenceItem
from app.models.clarification import TenderClarificationQuestion
from app.models.compliance_scorecard import TenderComplianceItem
from app.schemas.tender import (
    ComplianceItemResponse,
    ComplianceItemUpdate,
    ComplianceScorecardResponse,
    GenerateComplianceScorecardResponse,
)
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language
from app.services.compliance_scorecard_generator import build_compliance_summary, generate_compliance_item_payloads


router = APIRouter(tags=["compliance_scorecard"])

ALLOWED_STATUS = {
    "compliant",
    "partially_compliant",
    "needs_review",
    "needs_clarification",
    "non_compliant",
    "not_started",
}

ALLOWED_EVIDENCE = {"covered", "partial", "missing"}


def snapshot_compliance_item(item: TenderComplianceItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "requirement_id": item.requirement_id,
        "response_item_id": item.response_item_id,
        "category": item.category,
        "requirement_text": item.requirement_text,
        "compliance_status": item.compliance_status,
        "score": item.score,
        "max_score": item.max_score,
        "weight": item.weight,
        "owner": item.owner,
        "priority": item.priority,
        "risk_level": item.risk_level,
        "evidence_item_ids": item.evidence_item_ids,
        "evidence_coverage": item.evidence_coverage,
        "gap_summary": item.gap_summary,
        "recommended_action": item.recommended_action,
        "notes": item.notes,
        "source_page": item.source_page,
        "confidence": item.confidence,
        "generation_mode": item.generation_mode,
    }


def summary_from_items(items: list[TenderComplianceItem]) -> dict:
    payloads = [
        {
            "score": item.score,
            "max_score": item.max_score,
            "weight": item.weight,
            "category": item.category,
            "compliance_status": item.compliance_status,
            "evidence_coverage": item.evidence_coverage,
            "risk_level": item.risk_level,
        }
        for item in items
    ]
    return build_compliance_summary(payloads)


@router.post(
    "/api/v1/projects/{project_id}/generate-compliance-scorecard",
    response_model=GenerateComplianceScorecardResponse,
)
def generate_project_compliance_scorecard(
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
    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.id.asc())
        .all()
    )
    evidence_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .order_by(TenderEvidenceItem.id.asc())
        .all()
    )
    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .order_by(TenderClarificationQuestion.id.asc())
        .all()
    )

    old_items = (
        db.query(TenderComplianceItem)
        .filter(TenderComplianceItem.project_id == project_id)
        .all()
    )
    before = [snapshot_compliance_item(item) for item in old_items]

    db.query(TenderComplianceItem).filter(
        TenderComplianceItem.project_id == project_id
    ).delete(synchronize_session=False)

    output_language = get_project_output_language(db, project_id)
    payloads = generate_compliance_item_payloads(
        requirements=requirements,
        response_items=response_items,
        evidence_items=evidence_items,
        clarifications=clarifications,
        output_language=output_language,
    )

    created = []
    for payload in payloads:
        item = TenderComplianceItem(project_id=project_id, **payload)
        db.add(item)
        created.append(item)

    db.flush()

    summary = build_compliance_summary(payloads)
    after = [snapshot_compliance_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_compliance_scorecard",
        entity_type="compliance_item_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after), "summary": summary},
        ip_address=request.client.host if request.client else None,
        notes="Compliance matrix scorecard generated from tender artifacts",
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
    "/api/v1/projects/{project_id}/compliance-scorecard",
    response_model=ComplianceScorecardResponse,
)
def get_project_compliance_scorecard(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    items = (
        db.query(TenderComplianceItem)
        .filter(TenderComplianceItem.project_id == project_id)
        .order_by(
            TenderComplianceItem.score.asc(),
            TenderComplianceItem.risk_level.desc(),
            TenderComplianceItem.category.asc(),
            TenderComplianceItem.id.asc(),
        )
        .all()
    )

    return {
        "summary": summary_from_items(items),
        "items": items,
    }


@router.patch(
    "/api/v1/compliance-items/{item_id}",
    response_model=ComplianceItemResponse,
)
def update_compliance_item(
    item_id: int,
    payload: ComplianceItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderComplianceItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Compliance item not found")

    data = payload.model_dump(exclude_unset=True)

    if "compliance_status" in data and data["compliance_status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid compliance_status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "evidence_coverage" in data and data["evidence_coverage"] not in ALLOWED_EVIDENCE:
        raise HTTPException(status_code=400, detail=f"Invalid evidence_coverage. Allowed: {sorted(ALLOWED_EVIDENCE)}")

    if "score" in data and data["score"] is not None:
        data["score"] = max(0, min(100, int(data["score"])))

    before = snapshot_compliance_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()
    db.flush()

    after = snapshot_compliance_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_compliance_item",
        entity_type="compliance_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Compliance scorecard item updated",
    )

    db.commit()
    db.refresh(item)
    return item
