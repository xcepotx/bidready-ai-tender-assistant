from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderDocument, DocumentPage
from app.models.project_metadata import TenderProjectMetadata
from app.schemas.tender import ProjectMetadataResponse
from app.services.audit_service import create_audit_log
from app.services.metadata_extractor import extract_project_metadata_from_pages


router = APIRouter(tags=["metadata"])


@router.post(
    "/api/v1/projects/{project_id}/extract-metadata",
    response_model=ProjectMetadataResponse,
)
def extract_project_metadata(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = (
        db.query(TenderDocument)
        .filter(TenderDocument.project_id == project_id)
        .filter(TenderDocument.processing_status == "processed")
        .all()
    )

    if not documents:
        raise HTTPException(status_code=400, detail="No processed documents found")

    document_ids = [document.id for document in documents]

    pages = (
        db.query(DocumentPage)
        .filter(DocumentPage.document_id.in_(document_ids))
        .order_by(DocumentPage.document_id.asc(), DocumentPage.page_number.asc())
        .all()
    )

    if not pages:
        raise HTTPException(status_code=400, detail="No extracted page text found")

    page_payload = [
        {
            "document_id": page.document_id,
            "page_number": page.page_number,
            "text": page.text,
        }
        for page in pages
    ]

    payload = extract_project_metadata_from_pages(page_payload, project=project)

    old_metadata = (
        db.query(TenderProjectMetadata)
        .filter(TenderProjectMetadata.project_id == project_id)
        .first()
    )

    before_json = None
    if old_metadata:
        before_json = {
            "package_name": old_metadata.package_name,
            "issuer": old_metadata.issuer,
            "submission_deadline": old_metadata.submission_deadline,
            "clarification_deadline": old_metadata.clarification_deadline,
            "proposal_validity": old_metadata.proposal_validity,
            "service_domain": old_metadata.service_domain,
            "submission_requirements": old_metadata.submission_requirements,
            "source_evidence": old_metadata.source_evidence,
            "extraction_mode": old_metadata.extraction_mode,
            "notes": old_metadata.notes,
        }

        db.delete(old_metadata)
        db.flush()

    metadata = TenderProjectMetadata(
        project_id=project_id,
        package_name=payload["package_name"],
        issuer=payload["issuer"],
        submission_deadline=payload["submission_deadline"],
        clarification_deadline=payload["clarification_deadline"],
        proposal_validity=payload["proposal_validity"],
        service_domain=payload["service_domain"],
        submission_requirements=payload["submission_requirements"],
        source_evidence=payload["source_evidence"],
        extraction_mode=payload["extraction_mode"],
        notes=payload["notes"],
        updated_at=datetime.utcnow(),
    )

    db.add(metadata)
    db.flush()

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="extract_metadata",
        entity_type="project_metadata",
        entity_id=metadata.id,
        before_json=before_json,
        after_json=payload,
        ip_address=request.client.host if request.client else None,
        notes="Project metadata extracted from document pages",
    )

    db.commit()
    db.refresh(metadata)

    return metadata


@router.get(
    "/api/v1/projects/{project_id}/metadata",
    response_model=ProjectMetadataResponse,
)
def get_project_metadata(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    metadata = (
        db.query(TenderProjectMetadata)
        .filter(TenderProjectMetadata.project_id == project_id)
        .order_by(TenderProjectMetadata.id.desc())
        .first()
    )

    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata not extracted yet")

    return metadata
