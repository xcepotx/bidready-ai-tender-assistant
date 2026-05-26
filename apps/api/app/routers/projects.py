from pathlib import Path
import hashlib
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.tender import TenderProject, TenderDocument, DocumentPage, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.models.response_plan import TenderResponseItem
from app.models.proposal_outline import TenderProposalSection
from app.models.evidence_pack import TenderEvidenceItem
from app.models.action_item import TenderActionItem
from app.models.risk_item import TenderRiskItem
from app.models.compliance_scorecard import TenderComplianceItem
from app.models.decision_gate import TenderDecisionGate
from app.schemas.tender import (
    ProjectCreate,
    ProjectResponse,
    DocumentResponse,
    DocumentPageResponse,
    RequirementResponse,
    ReadinessSummaryResponse,
)
from app.services.pdf_parser import extract_pdf_pages, write_extracted_text
from app.services.requirement_extractor import extract_requirements_from_pages
from app.services.excel_exporter import export_project_checklist
from app.services.traceability_excel_exporter import export_traceability_matrix_xlsx
from app.services.readiness_service import compute_readiness_summary
from app.services.ai_gateway import build_rule_based_bid_brief
from app.services.i18n_service import get_project_output_language
from app.services.project_workflow_status import build_project_workflow_status


router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = TenderProject(
        title=payload.title,
        issuer=payload.issuer,
        tender_type=payload.tender_type,
        status="draft",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(TenderProject).order_by(TenderProject.id.desc()).all()



@router.get("/{project_id}/workflow-status")
def get_project_workflow_status(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return build_project_workflow_status(db, project_id)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/documents", response_model=DocumentResponse)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    filename = file.filename or "uploaded.pdf"
    suffix = Path(filename).suffix.lower()

    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF upload is supported in MVP")

    project_upload_dir = Path(settings.upload_dir) / f"project_{project_id}"
    project_upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex}_{Path(filename).name}"
    storage_path = project_upload_dir / safe_name

    sha256 = hashlib.sha256()
    size = 0

    with storage_path.open("wb") as buffer:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            sha256.update(chunk)
            buffer.write(chunk)

    document = TenderDocument(
        project_id=project_id,
        filename=filename,
        content_type=file.content_type,
        file_size=size,
        file_hash=sha256.hexdigest(),
        storage_path=str(storage_path),
        processing_status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        pages = extract_pdf_pages(str(storage_path))

        extracted_dir = Path(settings.upload_dir) / f"project_{project_id}" / "extracted"
        extracted_path = extracted_dir / f"document_{document.id}.txt"
        write_extracted_text(str(extracted_path), pages)

        for page in pages:
            db.add(
                DocumentPage(
                    document_id=document.id,
                    page_number=page["page_number"],
                    text=page["text"],
                    char_count=page["char_count"],
                )
            )

        document.page_count = len(pages)
        document.extracted_text_path = str(extracted_path)
        document.processing_status = "processed"
        project.status = "document_uploaded"

        db.commit()
        db.refresh(document)
        return document

    except Exception as exc:
        document.processing_status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}") from exc


@router.get("/{project_id}/documents", response_model=list[DocumentResponse])
def list_documents(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderDocument)
        .filter(TenderDocument.project_id == project_id)
        .order_by(TenderDocument.id.desc())
        .all()
    )


@router.post("/{project_id}/extract-requirements", response_model=list[RequirementResponse])
def extract_project_requirements(project_id: int, db: Session = Depends(get_db)):
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

    # Re-analysis must remove dependent clarification questions first,
    # because clarification questions reference tender_requirements.requirement_id.
    db.query(TenderClarificationQuestion).filter(
        TenderClarificationQuestion.project_id == project_id
    ).delete(synchronize_session=False)

    db.query(TenderRequirement).filter(
        TenderRequirement.project_id == project_id
    ).delete(synchronize_session=False)

    created_requirements = []

    for document in documents:
        pages = (
            db.query(DocumentPage)
            .filter(DocumentPage.document_id == document.id)
            .order_by(DocumentPage.page_number.asc())
            .all()
        )

        page_payload = [
            {
                "page_number": page.page_number,
                "text": page.text,
            }
            for page in pages
        ]

        extracted = extract_requirements_from_pages(page_payload)

        for item in extracted:
            requirement = TenderRequirement(
                project_id=project_id,
                document_id=document.id,
                category=item["category"],
                requirement_text=item["requirement_text"],
                priority=item["priority"],
                risk_level=item["risk_level"],
                source_page=item["source_page"],
                evidence_quote=item["evidence_quote"],
                confidence=item["confidence"],
                suggested_owner=item["suggested_owner"],
                status=item["status"],
                notes=item["notes"],
            )
            db.add(requirement)
            created_requirements.append(requirement)

    project.status = "requirements_extracted"
    db.commit()

    for requirement in created_requirements:
        db.refresh(requirement)

    return created_requirements


@router.get("/{project_id}/requirements", response_model=list[RequirementResponse])
def list_project_requirements(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderRequirement)
        .filter(TenderRequirement.project_id == project_id)
        .order_by(TenderRequirement.category.asc(), TenderRequirement.id.asc())
        .all()
    )




@router.get("/{project_id}/readiness-summary", response_model=ReadinessSummaryResponse)
def get_project_readiness_summary(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = (
        db.query(TenderDocument)
        .filter(TenderDocument.project_id == project_id)
        .all()
    )

    requirements = (
        db.query(TenderRequirement)
        .filter(TenderRequirement.project_id == project_id)
        .all()
    )

    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .all()
    )

    return compute_readiness_summary(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
    )

@router.get("/{project_id}/exports/checklist.xlsx")
def export_project_requirements_excel(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = (
        db.query(TenderDocument)
        .filter(TenderDocument.project_id == project_id)
        .order_by(TenderDocument.id.asc())
        .all()
    )

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
        .order_by(TenderEvidenceItem.priority.desc(), TenderEvidenceItem.evidence_category.asc(), TenderEvidenceItem.id.asc())
        .all()
    )

    decision_gate = (
        db.query(TenderDecisionGate)
        .filter(TenderDecisionGate.project_id == project_id)
        .order_by(TenderDecisionGate.id.desc())
        .first()
    )

    if not requirements:
        raise HTTPException(status_code=400, detail="No requirements found. Run extraction first.")

    readiness_summary = compute_readiness_summary(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
    )

    bid_brief = build_rule_based_bid_brief(
        project=project,
        readiness_summary=readiness_summary,
        requirements=requirements,
        clarifications=clarifications,
    )

    export_dir = Path(settings.export_dir) / f"project_{project_id}"
    output_language = get_project_output_language(db, project_id)

    output_path = export_dir / f"bidready_ai_tender_report_project_{project_id}.xlsx"

    export_project_checklist(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
        bid_brief=bid_brief,
        response_items=response_items,
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        output_path=str(output_path),
        output_language=output_language,
    )

    return FileResponse(
        path=str(output_path),
        filename=f"bidready_ai_tender_report_project_{project_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/{project_id}/exports/traceability-matrix.xlsx")
def export_project_traceability_matrix_excel(project_id: int, db: Session = Depends(get_db)):
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

    proposal_sections = (
        db.query(TenderProposalSection)
        .filter(TenderProposalSection.project_id == project_id)
        .order_by(TenderProposalSection.section_order.asc(), TenderProposalSection.id.asc())
        .all()
    )

    evidence_items = (
        db.query(TenderEvidenceItem)
        .filter(TenderEvidenceItem.project_id == project_id)
        .order_by(TenderEvidenceItem.priority.desc(), TenderEvidenceItem.evidence_category.asc(), TenderEvidenceItem.id.asc())
        .all()
    )

    compliance_items = (
        db.query(TenderComplianceItem)
        .filter(TenderComplianceItem.project_id == project_id)
        .order_by(TenderComplianceItem.score.asc(), TenderComplianceItem.id.asc())
        .all()
    )

    risk_items = (
        db.query(TenderRiskItem)
        .filter(TenderRiskItem.project_id == project_id)
        .order_by(TenderRiskItem.severity.asc(), TenderRiskItem.id.asc())
        .all()
    )

    action_items = (
        db.query(TenderActionItem)
        .filter(TenderActionItem.project_id == project_id)
        .order_by(TenderActionItem.priority.asc(), TenderActionItem.status.asc(), TenderActionItem.id.asc())
        .all()
    )

    output_language = get_project_output_language(db, project_id)
    export_dir = Path(settings.export_dir) / f"project_{project_id}"
    output_path = export_dir / f"bidready_ai_traceability_matrix_project_{project_id}.xlsx"

    export_traceability_matrix_xlsx(
        project=project,
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        proposal_sections=proposal_sections,
        evidence_items=evidence_items,
        compliance_items=compliance_items,
        risk_items=risk_items,
        action_items=action_items,
        output_path=str(output_path),
        output_language=output_language,
    )

    return FileResponse(
        path=str(output_path),
        filename=f"bidready_ai_traceability_matrix_project_{project_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

@router.get("/documents/{document_id}/pages", response_model=list[DocumentPageResponse])
def list_document_pages(document_id: int, db: Session = Depends(get_db)):
    document = db.get(TenderDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return (
        db.query(DocumentPage)
        .filter(DocumentPage.document_id == document_id)
        .order_by(DocumentPage.page_number.asc())
        .all()
    )
