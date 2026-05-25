from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.audit import AuditLog
from app.models.tender import TenderProject, TenderDocument, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.models.project_metadata import TenderProjectMetadata
from app.models.response_plan import TenderResponseItem
from app.models.proposal_outline import TenderProposalSection
from app.models.proposal_template import TenderProposalTemplate
from app.models.evidence_pack import TenderEvidenceItem
from app.models.decision_gate import TenderDecisionGate
from app.models.approval_workflow import TenderApprovalRequest, TenderApprovalStep
from app.models.compliance_scorecard import TenderComplianceItem
from app.models.risk_item import TenderRiskItem
from app.models.action_item import TenderActionItem
from app.models.clarification_response_tracker import TenderClarificationResponseItem
from app.models.addendum_impact import TenderAddendumImpactItem
from app.services.decision_gate_history_builder import (
    APPROVAL_ACTIONS,
    DECISION_ACTIONS,
    build_decision_gate_history_events,
    build_decision_gate_history_summary,
)
from app.services.executive_pack_exporter import export_executive_pack
from app.services.i18n_service import get_project_output_language


router = APIRouter(tags=["executive_pack"])


@router.get("/api/v1/projects/{project_id}/exports/executive-pack.zip")
def export_project_executive_pack(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = db.query(TenderDocument).filter(TenderDocument.project_id == project_id).order_by(TenderDocument.id.asc()).all()
    requirements = db.query(TenderRequirement).filter(TenderRequirement.project_id == project_id).order_by(TenderRequirement.category.asc(), TenderRequirement.id.asc()).all()
    clarifications = db.query(TenderClarificationQuestion).filter(TenderClarificationQuestion.project_id == project_id).order_by(TenderClarificationQuestion.priority.desc(), TenderClarificationQuestion.id.asc()).all()
    response_items = db.query(TenderResponseItem).filter(TenderResponseItem.project_id == project_id).order_by(TenderResponseItem.category.asc(), TenderResponseItem.id.asc()).all()
    proposal_sections = db.query(TenderProposalSection).filter(TenderProposalSection.project_id == project_id).order_by(TenderProposalSection.section_order.asc(), TenderProposalSection.id.asc()).all()
    evidence_items = db.query(TenderEvidenceItem).filter(TenderEvidenceItem.project_id == project_id).order_by(TenderEvidenceItem.priority.desc(), TenderEvidenceItem.id.asc()).all()

    metadata = db.query(TenderProjectMetadata).filter(TenderProjectMetadata.project_id == project_id).order_by(TenderProjectMetadata.id.desc()).first()
    proposal_template = db.query(TenderProposalTemplate).filter(TenderProposalTemplate.project_id == project_id).first()
    decision_gate = db.query(TenderDecisionGate).filter(TenderDecisionGate.project_id == project_id).order_by(TenderDecisionGate.id.desc()).first()

    approval_request = db.query(TenderApprovalRequest).filter(TenderApprovalRequest.project_id == project_id).order_by(TenderApprovalRequest.id.desc()).first()
    approval_steps = []
    if approval_request:
        approval_steps = db.query(TenderApprovalStep).filter(TenderApprovalStep.approval_request_id == approval_request.id).order_by(TenderApprovalStep.step_order.asc(), TenderApprovalStep.id.asc()).all()

    compliance_items = db.query(TenderComplianceItem).filter(TenderComplianceItem.project_id == project_id).order_by(TenderComplianceItem.score.asc(), TenderComplianceItem.id.asc()).all()
    risk_items = db.query(TenderRiskItem).filter(TenderRiskItem.project_id == project_id).order_by(TenderRiskItem.severity.asc(), TenderRiskItem.id.asc()).all()
    action_items = db.query(TenderActionItem).filter(TenderActionItem.project_id == project_id).order_by(TenderActionItem.priority.desc(), TenderActionItem.id.asc()).all()
    clarification_tracker_items = db.query(TenderClarificationResponseItem).filter(TenderClarificationResponseItem.project_id == project_id).order_by(TenderClarificationResponseItem.response_status.asc(), TenderClarificationResponseItem.id.asc()).all()
    addendum_items = db.query(TenderAddendumImpactItem).filter(TenderAddendumImpactItem.project_id == project_id).order_by(TenderAddendumImpactItem.severity.asc(), TenderAddendumImpactItem.id.asc()).all()

    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.project_id == project_id)
        .order_by(AuditLog.id.desc())
        .limit(500)
        .all()
    )

    history_logs = [
        log
        for log in audit_logs
        if log.action in (DECISION_ACTIONS | APPROVAL_ACTIONS)
    ]
    history_events = build_decision_gate_history_events(history_logs)
    decision_gate_history = {
        "summary": build_decision_gate_history_summary(
            events=history_events,
            decision_gate=decision_gate,
            approval_request=approval_request,
            approval_steps=approval_steps,
        ),
        "events": history_events,
    }

    if not requirements:
        raise HTTPException(status_code=400, detail="No requirements found. Run extraction first.")

    if not proposal_sections:
        raise HTTPException(status_code=400, detail="No proposal outline found. Generate proposal outline first.")

    output_language = get_project_output_language(db, project_id)
    export_dir = Path(settings.export_dir) / f"project_{project_id}" / "executive_pack"

    zip_path = export_executive_pack(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        proposal_sections=proposal_sections,
        evidence_items=evidence_items,
        metadata=metadata,
        decision_gate=decision_gate,
        decision_gate_history=decision_gate_history,
        approval_request=approval_request,
        approval_steps=approval_steps,
        compliance_items=compliance_items,
        risk_items=risk_items,
        action_items=action_items,
        clarification_tracker_items=clarification_tracker_items,
        addendum_items=addendum_items,
        audit_logs=audit_logs,
        output_dir=str(export_dir),
        output_language=output_language,
        proposal_template=proposal_template,
    )

    return FileResponse(
        path=zip_path,
        filename=f"bidready_ai_executive_pack_project_{project_id}.zip",
        media_type="application/zip",
    )
