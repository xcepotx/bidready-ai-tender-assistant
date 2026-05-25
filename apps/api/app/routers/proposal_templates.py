from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.proposal_template import TenderProposalTemplate
from app.schemas.tender import ProposalTemplateResponse, ProposalTemplateUpdate
from app.services.audit_service import create_audit_log


router = APIRouter(tags=["proposal_templates"])

ALLOWED_TONES = {"formal", "concise", "technical", "executive"}


def default_template_payload(project: TenderProject) -> dict:
    return {
        "id": None,
        "project_id": project.id,
        "template_name": "Standard Executive Proposal",
        "executive_title": None,
        "cover_note": None,
        "company_profile": None,
        "win_theme": None,
        "proposal_tone": "formal",
        "section_order": [],
        "excluded_section_keys": [],
        "custom_sections": [],
        "footer_note": None,
        "notes": None,
        "created_at": None,
        "updated_at": None,
    }


def snapshot_template(template: TenderProposalTemplate | None, project: TenderProject | None = None) -> dict | None:
    if not template:
        if project:
            return default_template_payload(project)
        return None

    return {
        "id": template.id,
        "project_id": template.project_id,
        "template_name": template.template_name,
        "executive_title": template.executive_title,
        "cover_note": template.cover_note,
        "company_profile": template.company_profile,
        "win_theme": template.win_theme,
        "proposal_tone": template.proposal_tone,
        "section_order": template.section_order,
        "excluded_section_keys": template.excluded_section_keys,
        "custom_sections": template.custom_sections,
        "footer_note": template.footer_note,
        "notes": template.notes,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
    }


@router.get(
    "/api/v1/projects/{project_id}/proposal-template",
    response_model=ProposalTemplateResponse,
)
def get_project_proposal_template(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    template = (
        db.query(TenderProposalTemplate)
        .filter(TenderProposalTemplate.project_id == project_id)
        .first()
    )

    if not template:
        return default_template_payload(project)

    return template


@router.patch(
    "/api/v1/projects/{project_id}/proposal-template",
    response_model=ProposalTemplateResponse,
)
def upsert_project_proposal_template(
    project_id: int,
    payload: ProposalTemplateUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    data = payload.model_dump(exclude_unset=True)

    if "proposal_tone" in data and data["proposal_tone"] not in ALLOWED_TONES:
        raise HTTPException(status_code=400, detail=f"Invalid proposal_tone. Allowed: {sorted(ALLOWED_TONES)}")

    template = (
        db.query(TenderProposalTemplate)
        .filter(TenderProposalTemplate.project_id == project_id)
        .first()
    )

    before = snapshot_template(template, project)

    if not template:
        template = TenderProposalTemplate(project_id=project_id)
        db.add(template)

    for field, value in data.items():
        setattr(template, field, value)

    template.updated_at = datetime.utcnow()
    db.flush()

    after = snapshot_template(template)

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="update_proposal_template",
        entity_type="proposal_template",
        entity_id=template.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Proposal template customization updated",
    )

    db.commit()
    db.refresh(template)

    return template
