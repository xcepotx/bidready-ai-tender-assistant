from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.action_item import TenderActionItem
from app.models.addendum_impact import TenderAddendumImpactItem
from app.models.approval_workflow import TenderApprovalRequest
from app.models.clarification import TenderClarificationQuestion
from app.models.clarification_response_tracker import TenderClarificationResponseItem
from app.models.compliance_scorecard import TenderComplianceItem
from app.models.decision_gate import TenderDecisionGate
from app.models.evidence_pack import TenderEvidenceItem
from app.models.proposal_outline import TenderProposalSection
from app.models.response_plan import TenderResponseItem
from app.models.risk_item import TenderRiskItem
from app.models.tender import TenderDocument, TenderProject, TenderRequirement


@dataclass(frozen=True)
class WorkflowStep:
    key: str
    label: str
    status: str
    count: int
    description: str


def _count(db: Session, model: Any, project_id: int) -> int:
    try:
        return int(db.query(func.count(model.id)).filter(model.project_id == project_id).scalar() or 0)
    except Exception:
        return 0


def _count_filtered(db: Session, model: Any, project_id: int, *filters: Any) -> int:
    try:
        query = db.query(func.count(model.id)).filter(model.project_id == project_id)
        for condition in filters:
            if condition is not None:
                query = query.filter(condition)
        return int(query.scalar() or 0)
    except Exception:
        return 0


def _column(model: Any, name: str) -> Any | None:
    return getattr(model, name, None)


def _status_done(count: int, required: bool = True) -> str:
    if count > 0:
        return "done"
    return "pending" if required else "optional"


def _not_done_filter(model: Any) -> Any | None:
    status = _column(model, "status")
    if status is None:
        return None

    return ~func.lower(func.coalesce(status, "")).in_(
        ["done", "closed", "completed", "cancelled", "canceled", "resolved", "mitigated"]
    )


def _unassigned_owner_filter(model: Any) -> Any | None:
    owner = _column(model, "owner")
    if owner is None:
        return None
    return (owner.is_(None)) | (func.trim(owner) == "")


def _high_risk_filter(model: Any) -> Any | None:
    severity = _column(model, "severity") or _column(model, "risk_level") or _column(model, "priority")
    if severity is None:
        return None
    return func.lower(func.coalesce(severity, "")).in_(["high", "critical"])


def _requirements_needs_review_count(db: Session, project_id: int) -> int:
    status = _column(TenderRequirement, "status")
    if status is None:
        return 0

    return _count_filtered(
        db,
        TenderRequirement,
        project_id,
        func.lower(func.coalesce(status, "")).in_(["needs_review", "open", "draft"]),
    )


def _overdue_actions_count(db: Session, project_id: int) -> int:
    due_date = _column(TenderActionItem, "due_date")
    if due_date is None:
        return 0

    filters = [due_date < date.today()]
    not_done = _not_done_filter(TenderActionItem)
    if not_done is not None:
        filters.append(not_done)

    return _count_filtered(db, TenderActionItem, project_id, *filters)


def _current_stage(steps: list[WorkflowStep]) -> str:
    for step in steps:
        if step.status == "pending":
            return step.label
    return "Ready for Submission"


def build_project_workflow_status(db: Session, project_id: int) -> dict[str, Any]:
    project = db.get(TenderProject, project_id)

    if project is None:
        return {
            "project_id": project_id,
            "overall_progress": 0,
            "current_stage": "Project Not Found",
            "steps": [],
            "counts": {},
            "next_actions": ["Select or create a valid bid project."],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    counts: dict[str, int] = {
        "documents": _count(db, TenderDocument, project_id),
        "requirements": _count(db, TenderRequirement, project_id),
        "requirements_needs_review": _requirements_needs_review_count(db, project_id),
        "clarifications": _count(db, TenderClarificationQuestion, project_id),
        "clarification_tracker": _count(db, TenderClarificationResponseItem, project_id),
        "response_plan": _count(db, TenderResponseItem, project_id),
        "proposal_sections": _count(db, TenderProposalSection, project_id),
        "evidence_items": _count(db, TenderEvidenceItem, project_id),
        "decision_gates": _count(db, TenderDecisionGate, project_id),
        "compliance_items": _count(db, TenderComplianceItem, project_id),
        "risk_items": _count(db, TenderRiskItem, project_id),
        "action_items": _count(db, TenderActionItem, project_id),
        "approval_requests": _count(db, TenderApprovalRequest, project_id),
        "addendum_impacts": _count(db, TenderAddendumImpactItem, project_id),
    }

    action_not_done = _not_done_filter(TenderActionItem)
    counts["open_actions"] = (
        _count_filtered(db, TenderActionItem, project_id, action_not_done)
        if action_not_done is not None
        else counts["action_items"]
    )

    unassigned_action = _unassigned_owner_filter(TenderActionItem)
    if unassigned_action is not None and action_not_done is not None:
        counts["unassigned_actions"] = _count_filtered(db, TenderActionItem, project_id, unassigned_action, action_not_done)
    elif unassigned_action is not None:
        counts["unassigned_actions"] = _count_filtered(db, TenderActionItem, project_id, unassigned_action)
    else:
        counts["unassigned_actions"] = 0

    counts["overdue_actions"] = _overdue_actions_count(db, project_id)

    high_risk = _high_risk_filter(TenderRiskItem)
    risk_not_done = _not_done_filter(TenderRiskItem)

    if high_risk is not None and risk_not_done is not None:
        counts["high_risk_open"] = _count_filtered(db, TenderRiskItem, project_id, high_risk, risk_not_done)
    elif high_risk is not None:
        counts["high_risk_open"] = _count_filtered(db, TenderRiskItem, project_id, high_risk)
    else:
        counts["high_risk_open"] = 0

    steps = [
        WorkflowStep("rfp_uploaded", "RFP Uploaded", _status_done(counts["documents"]), counts["documents"], "Tender/RFP document has been uploaded and parsed."),
        WorkflowStep("requirements_analyzed", "Requirements Analyzed", _status_done(counts["requirements"]), counts["requirements"], "RFP requirements have been extracted for review."),
        WorkflowStep("readiness_review", "Readiness Review", _status_done(counts["decision_gates"]), counts["decision_gates"], "Decision gate or readiness recommendation is available."),
        WorkflowStep("clarifications", "Clarifications", _status_done(counts["clarifications"], required=False), counts["clarifications"], "Clarification questions are available for ambiguous or high-risk items."),
        WorkflowStep("response_plan", "Response Plan", _status_done(counts["response_plan"]), counts["response_plan"], "Response strategy and draft response items are available."),
        WorkflowStep("proposal_outline", "Proposal Outline", _status_done(counts["proposal_sections"]), counts["proposal_sections"], "Proposal structure and draft sections are available."),
        WorkflowStep("evidence_pack", "Evidence Pack", _status_done(counts["evidence_items"]), counts["evidence_items"], "Supporting evidence has been mapped to proposal content and requirements."),
        WorkflowStep("compliance_scorecard", "Compliance Scorecard", _status_done(counts["compliance_items"]), counts["compliance_items"], "Compliance scoring has been generated."),
        WorkflowStep("risk_register", "Risk Register", _status_done(counts["risk_items"], required=False), counts["risk_items"], "Bid and delivery risks are captured."),
        WorkflowStep("action_tracker", "Action Tracker", _status_done(counts["action_items"], required=False), counts["action_items"], "Follow-up tasks have been created for the bid team."),
        WorkflowStep("approval_workflow", "Approval Workflow", _status_done(counts["approval_requests"]), counts["approval_requests"], "Internal approval workflow is ready or submitted."),
    ]

    required_steps = [step for step in steps if step.status != "optional"]
    done_required = sum(1 for step in required_steps if step.status == "done")
    overall_progress = round((done_required / len(required_steps)) * 100) if required_steps else 0

    next_actions: list[str] = []

    if counts["documents"] == 0:
        next_actions.append("Upload and parse the RFP document.")
    elif counts["requirements"] == 0:
        next_actions.append("Analyze the RFP to extract requirements.")
    else:
        if counts["requirements_needs_review"] > 0:
            next_actions.append(f"Review {counts['requirements_needs_review']} requirement(s) still marked for review.")
        if counts["clarifications"] == 0:
            next_actions.append("Generate clarification questions for ambiguous or high-risk requirements.")
        if counts["response_plan"] == 0:
            next_actions.append("Generate the response plan.")
        if counts["proposal_sections"] == 0:
            next_actions.append("Generate the proposal outline.")
        if counts["evidence_items"] == 0:
            next_actions.append("Generate the evidence pack.")
        if counts["compliance_items"] == 0:
            next_actions.append("Generate the compliance scorecard.")
        if counts["risk_items"] == 0:
            next_actions.append("Generate the risk register.")
        elif counts["high_risk_open"] > 0:
            next_actions.append(f"Review mitigation for {counts['high_risk_open']} high-risk item(s).")

        if counts["action_items"] == 0:
            next_actions.append("Generate action items for follow-up ownership.")
        else:
            if counts["overdue_actions"] > 0:
                next_actions.append(f"Resolve {counts['overdue_actions']} overdue action item(s).")
            if counts["unassigned_actions"] > 0:
                next_actions.append(f"Assign owner for {counts['unassigned_actions']} open action item(s).")
            if counts["open_actions"] > 0:
                next_actions.append(f"Close or update {counts['open_actions']} open action item(s).")

        if counts["approval_requests"] == 0:
            next_actions.append("Generate or submit the approval workflow.")
        if counts["decision_gates"] == 0:
            next_actions.append("Generate the decision gate recommendation.")

    return {
        "project_id": project_id,
        "overall_progress": overall_progress,
        "current_stage": _current_stage(steps),
        "steps": [
            {
                "key": step.key,
                "label": step.label,
                "status": step.status,
                "count": step.count,
                "description": step.description,
            }
            for step in steps
        ],
        "counts": counts,
        "next_actions": next_actions[:8],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
