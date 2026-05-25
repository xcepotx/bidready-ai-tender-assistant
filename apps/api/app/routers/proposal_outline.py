from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.response_plan import TenderResponseItem
from app.models.proposal_outline import TenderProposalSection
from app.models.evidence_pack import TenderEvidenceItem
from app.models.decision_gate import TenderDecisionGate
from app.models.project_metadata import TenderProjectMetadata
from app.models.proposal_template import TenderProposalTemplate
from app.schemas.tender import (
    GenerateProposalOutlineResponse,
    ProposalSectionResponse,
    ProposalSectionUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.proposal_outline_generator import generate_proposal_outline_sections
from app.services.proposal_docx_exporter import export_proposal_draft_docx
from app.services.i18n_service import get_project_output_language, localize_proposal_outline_payload


router = APIRouter(tags=["proposal_outline"])


ALLOWED_STATUS = {
    "draft",
    "in_review",
    "ready",
    "approved",
    "blocked",
}


def snapshot_proposal_section(section: TenderProposalSection) -> dict:
    return {
        "id": section.id,
        "project_id": section.project_id,
        "section_key": section.section_key,
        "title": section.title,
        "section_order": section.section_order,
        "purpose": section.purpose,
        "content_outline": section.content_outline,
        "draft_content": section.draft_content,
        "source_response_item_ids": section.source_response_item_ids,
        "evidence_needed": section.evidence_needed,
        "risks": section.risks,
        "owner": section.owner,
        "status": section.status,
        "notes": section.notes,
        "generation_mode": section.generation_mode,
    }


@router.post(
    "/api/v1/projects/{project_id}/generate-proposal-outline",
    response_model=GenerateProposalOutlineResponse,
)
def generate_project_proposal_outline(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.category.asc(), TenderResponseItem.id.asc())
        .all()
    )

    if not response_items:
        raise HTTPException(status_code=400, detail="No response plan found. Generate response plan first.")

    metadata = (
        db.query(TenderProjectMetadata)
        .filter(TenderProjectMetadata.project_id == project_id)
        .order_by(TenderProjectMetadata.id.desc())
        .first()
    )

    evidence_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .order_by(TenderEvidenceItem.priority.desc(), TenderEvidenceItem.evidence_category.asc(), TenderEvidenceItem.id.asc())
        .all()
    )

    old_sections = (
        db.query(TenderProposalSection)
        .filter(TenderProposalSection.project_id == project_id)
        .all()
    )
    before = [snapshot_proposal_section(section) for section in old_sections]

    db.query(TenderProposalSection).filter(
        TenderProposalSection.project_id == project_id
    ).delete(synchronize_session=False)

    generated_payloads = generate_proposal_outline_sections(
        project=project,
        response_items=response_items,
        metadata=metadata,
    )

    output_language = get_project_output_language(db, project_id)
    generated_payloads = [
        localize_proposal_outline_payload(payload, output_language)
        for payload in generated_payloads
    ]

    created = []

    for payload in generated_payloads:
        section = TenderProposalSection(
            project_id=project_id,
            **payload,
        )
        db.add(section)
        created.append(section)

    db.flush()

    after = [snapshot_proposal_section(section) for section in created]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_proposal_outline",
        entity_type="proposal_outline_batch",
        entity_id=None,
        before_json={"items": before, "old_count": len(before)},
        after_json={"items": after, "new_count": len(after)},
        ip_address=request.client.host if request.client else None,
        notes="Proposal outline generated from response plan",
    )

    db.commit()

    for section in created:
        db.refresh(section)

    return {
        "generated_count": len(created),
        "sections": created,
    }


@router.get(
    "/api/v1/projects/{project_id}/proposal-outline",
    response_model=list[ProposalSectionResponse],
)
def list_project_proposal_outline(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderProposalSection)
        .filter(TenderProposalSection.project_id == project_id)
        .order_by(TenderProposalSection.section_order.asc(), TenderProposalSection.id.asc())
        .all()
    )




@router.get("/api/v1/projects/{project_id}/exports/proposal-draft.docx")
def export_project_proposal_draft_docx(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    proposal_sections = (
        db.query(TenderProposalSection)
        .filter(TenderProposalSection.project_id == project_id)
        .order_by(TenderProposalSection.section_order.asc(), TenderProposalSection.id.asc())
        .all()
    )

    if not proposal_sections:
        raise HTTPException(status_code=400, detail="No proposal outline found. Generate proposal outline first.")

    response_items = (
        db.query(TenderResponseItem)
        .filter(TenderResponseItem.project_id == project_id)
        .order_by(TenderResponseItem.category.asc(), TenderResponseItem.id.asc())
        .all()
    )

    metadata = (
        db.query(TenderProjectMetadata)
        .filter(TenderProjectMetadata.project_id == project_id)
        .order_by(TenderProjectMetadata.id.desc())
        .first()
    )

    decision_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
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

    proposal_template = (
        db.query(TenderProposalTemplate)
        .filter(TenderProposalTemplate.project_id == project_id)
        .first()
    )

    output_language = get_project_output_language(db, project_id)

    export_dir = Path(settings.export_dir) / f"project_{project_id}"
    output_path = export_dir / f"bidready_ai_proposal_draft_project_{project_id}.docx"

    export_proposal_draft_docx(
        project=project,
        metadata=metadata,
        proposal_sections=proposal_sections,
        response_items=response_items,
        output_path=str(output_path),
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        output_language=output_language,
        proposal_template=proposal_template,
    )

    return FileResponse(
        path=str(output_path),
        filename=f"bidready_ai_proposal_draft_project_{project_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

@router.patch(
    "/api/v1/proposal-sections/{section_id}",
    response_model=ProposalSectionResponse,
)
def update_proposal_section(
    section_id: int,
    payload: ProposalSectionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    section = db.get(TenderProposalSection, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Proposal section not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}",
        )

    before = snapshot_proposal_section(section)

    for field, value in data.items():
        setattr(section, field, value)

    section.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_proposal_section(section)

    create_audit_log(
        db,
        project_id=section.project_id,
        actor=x_actor,
        action="update_proposal_section",
        entity_type="proposal_section",
        entity_id=section.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Proposal outline section updated",
    )

    db.commit()
    db.refresh(section)

    return section
