from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderDocument, DocumentPage, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.models.response_plan import TenderResponseItem
from app.models.compliance_scorecard import TenderComplianceItem
from app.models.risk_item import TenderRiskItem
from app.models.approval_workflow import TenderApprovalRequest, TenderApprovalStep
from app.models.decision_gate import TenderDecisionGate
from app.models.addendum_impact import TenderAddendumImpactItem
from app.schemas.tender import (
    AddendumImpactAnalysisResponse,
    AddendumImpactGenerateRequest,
    AddendumImpactGenerateResponse,
    AddendumImpactItemResponse,
    AddendumImpactItemUpdate,
)
from app.services.addendum_impact_analyzer import (
    build_addendum_impact_summary,
    generate_addendum_impact_payloads,
)
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language


router = APIRouter(tags=["addendum_impact"])

ALLOWED_STATUS = {"open", "reviewed", "accepted", "resolved", "rejected"}
ALLOWED_SEVERITY = {"critical", "high", "medium", "low"}


def snapshot_item(item: TenderAddendumImpactItem) -> dict:
    return {
        "id": item.id,
        "project_id": item.project_id,
        "document_id": item.document_id,
        "source_document_name": item.source_document_name,
        "title": item.title,
        "summary": item.summary,
        "impact_type": item.impact_type,
        "impacted_artifact": item.impacted_artifact,
        "severity": item.severity,
        "status": item.status,
        "source_excerpt": item.source_excerpt,
        "recommended_action": item.recommended_action,
        "owner": item.owner,
        "due_date": item.due_date,
        "related_requirement_ids": item.related_requirement_ids,
        "related_response_item_ids": item.related_response_item_ids,
        "related_clarification_ids": item.related_clarification_ids,
        "related_compliance_item_ids": item.related_compliance_item_ids,
        "related_risk_item_ids": item.related_risk_item_ids,
        "related_approval_step_ids": item.related_approval_step_ids,
        "confidence": item.confidence,
        "notes": item.notes,
        "generation_mode": item.generation_mode,
    }


def summary_from_items(items: list[TenderAddendumImpactItem]) -> dict:
    return build_addendum_impact_summary([
        {
            "severity": item.severity,
            "impacted_artifact": item.impacted_artifact,
            "status": item.status,
        }
        for item in items
    ])


def selected_document(db: Session, project_id: int, document_id: int | None):
    query = db.query(TenderDocument).filter(TenderDocument.project_id == project_id)
    if document_id:
        document = query.filter(TenderDocument.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    return query.order_by(TenderDocument.id.desc()).first()


def document_text(db: Session, document: TenderDocument | None) -> str:
    if not document:
        return ""

    pages = (
        db.query(DocumentPage)
        .filter(DocumentPage.document_id == document.id)
        .order_by(DocumentPage.page_number.asc())
        .all()
    )
    return "\n\n".join(page.text or "" for page in pages)


@router.post(
    "/api/v1/projects/{project_id}/generate-addendum-impact-analysis",
    response_model=AddendumImpactGenerateResponse,
)
def generate_project_addendum_impact_analysis(
    project_id: int,
    request: Request,
    payload: AddendumImpactGenerateRequest | None = None,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    document = selected_document(db, project_id, payload.document_id if payload else None)
    text = document_text(db, document)

    old_items = db.query(TenderAddendumImpactItem).filter(TenderAddendumImpactItem.project_id == project_id).all()
    before = [snapshot_item(item) for item in old_items]

    db.query(TenderAddendumImpactItem).filter(
        TenderAddendumImpactItem.project_id == project_id
    ).delete(synchronize_session=False)

    requirements = db.query(TenderRequirement).filter(TenderRequirement.project_id == project_id).order_by(TenderRequirement.id.asc()).all()
    clarifications = db.query(TenderClarificationQuestion).filter(TenderClarificationQuestion.project_id == project_id).order_by(TenderClarificationQuestion.id.asc()).all()
    response_items = db.query(TenderResponseItem).filter(TenderResponseItem.project_id == project_id).order_by(TenderResponseItem.id.asc()).all()
    compliance_items = db.query(TenderComplianceItem).filter(TenderComplianceItem.project_id == project_id).order_by(TenderComplianceItem.id.asc()).all()
    risk_items = db.query(TenderRiskItem).filter(TenderRiskItem.project_id == project_id).order_by(TenderRiskItem.id.asc()).all()

    approval_request = db.query(TenderApprovalRequest).filter(TenderApprovalRequest.project_id == project_id).order_by(TenderApprovalRequest.id.desc()).first()
    approval_steps = []
    if approval_request:
        approval_steps = db.query(TenderApprovalStep).filter(TenderApprovalStep.approval_request_id == approval_request.id).order_by(TenderApprovalStep.step_order.asc()).all()

    decision_gate = db.query(TenderDecisionGate).filter(TenderDecisionGate.project_id == project_id).order_by(TenderDecisionGate.id.desc()).first()
    output_language = get_project_output_language(db, project_id)

    payloads = generate_addendum_impact_payloads(
        document=document,
        document_text=text,
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        compliance_items=compliance_items,
        risk_items=risk_items,
        approval_steps=approval_steps,
        decision_gate=decision_gate,
        output_language=output_language,
    )

    created = []
    for item_payload in payloads:
        item = TenderAddendumImpactItem(project_id=project_id, **item_payload)
        db.add(item)
        created.append(item)

    db.flush()
    summary = build_addendum_impact_summary(payloads)
    after = [snapshot_item(item) for item in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_addendum_impact_analysis",
        entity_type="addendum_impact_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after), "summary": summary},
        ip_address=request.client.host if request.client else None,
        notes="Addendum/document impact analysis generated from tender artifacts",
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
    "/api/v1/projects/{project_id}/addendum-impacts",
    response_model=AddendumImpactAnalysisResponse,
)
def get_project_addendum_impacts(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    items = (
        db.query(TenderAddendumImpactItem)
        .filter(TenderAddendumImpactItem.project_id == project_id)
        .order_by(TenderAddendumImpactItem.severity.asc(), TenderAddendumImpactItem.status.asc(), TenderAddendumImpactItem.id.asc())
        .all()
    )
    return {
        "summary": summary_from_items(items),
        "items": items,
    }


@router.patch(
    "/api/v1/addendum-impact-items/{item_id}",
    response_model=AddendumImpactItemResponse,
)
def update_addendum_impact_item(
    item_id: int,
    payload: AddendumImpactItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    item = db.get(TenderAddendumImpactItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Addendum impact item not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "severity" in data and data["severity"] not in ALLOWED_SEVERITY:
        raise HTTPException(status_code=400, detail=f"Invalid severity. Allowed: {sorted(ALLOWED_SEVERITY)}")

    before = snapshot_item(item)

    for field, value in data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()
    db.flush()
    after = snapshot_item(item)

    create_audit_log(
        db,
        project_id=item.project_id,
        actor=x_actor,
        action="update_addendum_impact_item",
        entity_type="addendum_impact_item",
        entity_id=item.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Addendum impact item updated",
    )

    db.commit()
    db.refresh(item)
    return item
