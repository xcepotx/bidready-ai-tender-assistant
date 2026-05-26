from __future__ import annotations

import json
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.services.excel_exporter import export_project_checklist
from app.services.proposal_docx_exporter import export_proposal_draft_docx
from app.services.traceability_excel_exporter import export_traceability_matrix_xlsx
from app.services.readiness_service import compute_readiness_summary
from app.services.ai_gateway import build_rule_based_bid_brief


def _json_default(value: Any):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _to_dict(model) -> dict:
    if model is None:
        return {}

    if isinstance(model, dict):
        return model

    data = {}
    for column in model.__table__.columns:
        data[column.name] = getattr(model, column.name)
    return data


def _list_dict(items) -> list[dict]:
    return [_to_dict(item) for item in (items or [])]


def _write_json(path: Path, payload: Any):
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )


def _count_by(items, field: str) -> dict:
    counts = {}
    for item in items or []:
        value = getattr(item, field, None)
        if value is None and isinstance(item, dict):
            value = item.get(field)
        value = value or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _approval_summary(approval_request, approval_steps) -> dict:
    approval_steps = approval_steps or []
    return {
        "status": getattr(approval_request, "status", None),
        "total_steps": len(approval_steps),
        "approved_steps": len([s for s in approval_steps if s.status == "approved"]),
        "pending_steps": len([s for s in approval_steps if s.status == "pending"]),
        "rejected_steps": len([s for s in approval_steps if s.status == "rejected"]),
        "changes_requested_steps": len([s for s in approval_steps if s.status == "changes_requested"]),
    }


def _compliance_summary(compliance_items) -> dict:
    compliance_items = compliance_items or []
    if not compliance_items:
        return {
            "total_items": 0,
            "score_percent": 0,
            "status_counts": {},
            "evidence_coverage_counts": {},
        }

    weighted_score = sum((item.score or 0) * (item.weight or 1.0) for item in compliance_items)
    max_score = sum((item.max_score or 100) * (item.weight or 1.0) for item in compliance_items) or 1

    return {
        "total_items": len(compliance_items),
        "score_percent": int(round((weighted_score / max_score) * 100)),
        "status_counts": _count_by(compliance_items, "compliance_status"),
        "evidence_coverage_counts": _count_by(compliance_items, "evidence_coverage"),
        "high_risk_gaps": len([item for item in compliance_items if item.risk_level == "high" and item.compliance_status != "compliant"]),
    }


def _risk_summary(risk_items) -> dict:
    risk_items = risk_items or []
    return {
        "total_items": len(risk_items),
        "severity_counts": _count_by(risk_items, "severity"),
        "status_counts": _count_by(risk_items, "status"),
        "critical_open": len([item for item in risk_items if item.severity == "critical" and item.status not in {"closed", "accepted"}]),
        "high_open": len([item for item in risk_items if item.severity == "high" and item.status not in {"closed", "accepted"}]),
    }


def _action_summary(action_items) -> dict:
    action_items = action_items or []
    return {
        "total_items": len(action_items),
        "status_counts": _count_by(action_items, "status"),
        "priority_counts": _count_by(action_items, "priority"),
        "open_items": len([item for item in action_items if item.status not in {"done", "completed", "closed"}]),
    }


def _clarification_tracker_summary(clarification_tracker_items) -> dict:
    clarification_tracker_items = clarification_tracker_items or []
    total = len(clarification_tracker_items)
    answered = len([item for item in clarification_tracker_items if item.response_status in {"answered", "incorporated", "closed"}])
    return {
        "total_items": total,
        "completion_percent": int(round((answered / total) * 100)) if total else 0,
        "status_counts": _count_by(clarification_tracker_items, "response_status"),
        "high_priority_items": len([item for item in clarification_tracker_items if item.priority == "high"]),
        "high_risk_items": len([item for item in clarification_tracker_items if item.risk_level == "high"]),
    }


def _addendum_summary(addendum_items) -> dict:
    addendum_items = addendum_items or []
    return {
        "total_items": len(addendum_items),
        "severity_counts": _count_by(addendum_items, "severity"),
        "status_counts": _count_by(addendum_items, "status"),
        "critical_items": len([item for item in addendum_items if item.severity == "critical"]),
        "high_items": len([item for item in addendum_items if item.severity == "high"]),
    }


def build_executive_summary_payload(
    *,
    project,
    documents,
    requirements,
    clarifications,
    response_items,
    proposal_sections,
    evidence_items,
    decision_gate,
    approval_request,
    approval_steps,
    compliance_items,
    risk_items,
    action_items,
    clarification_tracker_items,
    addendum_items,
    audit_logs,
) -> dict:
    readiness_summary = compute_readiness_summary(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
    )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "project": _to_dict(project),
        "readiness_summary": readiness_summary,
        "counts": {
            "documents": len(documents),
            "requirements": len(requirements),
            "clarifications": len(clarifications),
            "response_items": len(response_items),
            "proposal_sections": len(proposal_sections),
            "evidence_items": len(evidence_items),
            "audit_logs": len(audit_logs),
        },
        "decision_gate": _to_dict(decision_gate),
        "approval_summary": _approval_summary(approval_request, approval_steps),
        "compliance_summary": _compliance_summary(compliance_items),
        "risk_summary": _risk_summary(risk_items),
        "action_summary": _action_summary(action_items),
        "clarification_response_summary": _clarification_tracker_summary(clarification_tracker_items),
        "addendum_impact_summary": _addendum_summary(addendum_items),
    }


def build_executive_summary_markdown(payload: dict) -> str:
    project = payload.get("project", {})
    decision_gate = payload.get("decision_gate", {})
    readiness = payload.get("readiness_summary", {})
    counts = payload.get("counts", {})

    lines = [
        "# BidReady AI Executive Pack",
        "",
        f"Generated at: {payload.get('generated_at')}",
        "",
        "## Project",
        f"- Project ID: {project.get('id')}",
        f"- Title: {project.get('title')}",
        f"- Issuer: {project.get('issuer')}",
        f"- Tender Type: {project.get('tender_type')}",
        f"- Status: {project.get('status')}",
        "",
        "## Executive Decision",
        f"- Decision Status: {decision_gate.get('decision_status', '-')}",
        f"- Recommendation: {decision_gate.get('recommendation', '-')}",
        f"- Readiness Score: {decision_gate.get('readiness_score', readiness.get('readiness_score', 0))}",
        "",
        "## Key Counts",
        f"- Documents: {counts.get('documents', 0)}",
        f"- Requirements: {counts.get('requirements', 0)}",
        f"- Clarifications: {counts.get('clarifications', 0)}",
        f"- Response Items: {counts.get('response_items', 0)}",
        f"- Proposal Sections: {counts.get('proposal_sections', 0)}",
        f"- Evidence Items: {counts.get('evidence_items', 0)}",
        "",
        "## Scorecards",
        f"- Compliance Score: {payload.get('compliance_summary', {}).get('score_percent', 0)}%",
        f"- Open Actions: {payload.get('action_summary', {}).get('open_items', 0)}",
        f"- Critical Open Risks: {payload.get('risk_summary', {}).get('critical_open', 0)}",
        f"- High Open Risks: {payload.get('risk_summary', {}).get('high_open', 0)}",
        f"- Clarification Completion: {payload.get('clarification_response_summary', {}).get('completion_percent', 0)}%",
        f"- Addendum Critical Items: {payload.get('addendum_impact_summary', {}).get('critical_items', 0)}",
        "",
        "## Included Files",
        "- bidready_ai_tender_report.xlsx",
        "- bidready_ai_proposal_draft.docx",
        "- bidready_ai_traceability_matrix.xlsx",
        "- executive_summary.json",
        "- decision_gate_history.json",
        "- approval_workflow.json",
        "- compliance_scorecard.json",
        "- risk_register.json",
        "- action_tracker.json",
        "- clarification_response_tracker.json",
        "- addendum_impact_analysis.json",
        "- audit_logs.json",
    ]

    return "\n".join(lines) + "\n"


def export_executive_pack(
    *,
    project,
    documents,
    requirements,
    clarifications,
    response_items,
    proposal_sections,
    evidence_items,
    metadata,
    decision_gate,
    decision_gate_history,
    approval_request,
    approval_steps,
    compliance_items,
    risk_items,
    action_items,
    clarification_tracker_items,
    addendum_items,
    audit_logs,
    output_dir: str,
    output_language: str = "en",
    proposal_template=None,
) -> str:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    work_dir = output_root / "executive_pack_work"
    work_dir.mkdir(parents=True, exist_ok=True)

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

    excel_path = work_dir / "bidready_ai_tender_report.xlsx"
    docx_path = work_dir / "bidready_ai_proposal_draft.docx"
    traceability_path = work_dir / "bidready_ai_traceability_matrix.xlsx"

    export_project_checklist(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
        bid_brief=bid_brief,
        response_items=response_items,
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        output_path=str(excel_path),
        output_language=output_language,
    )

    export_proposal_draft_docx(
        project=project,
        metadata=metadata,
        proposal_sections=proposal_sections,
        response_items=response_items,
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        output_path=str(docx_path),
        output_language=output_language,
        proposal_template=proposal_template,
    )

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
        output_path=str(traceability_path),
        output_language=output_language,
    )

    executive_payload = build_executive_summary_payload(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
        response_items=response_items,
        proposal_sections=proposal_sections,
        evidence_items=evidence_items,
        decision_gate=decision_gate,
        approval_request=approval_request,
        approval_steps=approval_steps,
        compliance_items=compliance_items,
        risk_items=risk_items,
        action_items=action_items,
        clarification_tracker_items=clarification_tracker_items,
        addendum_items=addendum_items,
        audit_logs=audit_logs,
    )

    files = {
        "executive_summary.json": executive_payload,
        "decision_gate.json": _to_dict(decision_gate),
        "decision_gate_history.json": decision_gate_history or {"summary": {}, "events": []},
        "approval_workflow.json": {
            "request": _to_dict(approval_request),
            "steps": _list_dict(approval_steps),
            "summary": executive_payload["approval_summary"],
        },
        "compliance_scorecard.json": {
            "summary": executive_payload["compliance_summary"],
            "items": _list_dict(compliance_items),
        },
        "risk_register.json": {
            "summary": executive_payload["risk_summary"],
            "items": _list_dict(risk_items),
        },
        "action_tracker.json": {
            "summary": executive_payload["action_summary"],
            "items": _list_dict(action_items),
        },
        "clarification_response_tracker.json": {
            "summary": executive_payload["clarification_response_summary"],
            "items": _list_dict(clarification_tracker_items),
        },
        "addendum_impact_analysis.json": {
            "summary": executive_payload["addendum_impact_summary"],
            "items": _list_dict(addendum_items),
        },
        "audit_logs.json": _list_dict(audit_logs),
    }

    for filename, payload in files.items():
        _write_json(work_dir / filename, payload)

    (work_dir / "executive_summary.md").write_text(
        build_executive_summary_markdown(executive_payload),
        encoding="utf-8",
    )

    zip_path = output_root / f"bidready_ai_executive_pack_project_{project.id}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(excel_path, "bidready_ai_tender_report.xlsx")
        archive.write(docx_path, "bidready_ai_proposal_draft.docx")
        archive.write(traceability_path, "bidready_ai_traceability_matrix.xlsx")
        for file_path in sorted(work_dir.glob("*.json")):
            archive.write(file_path, file_path.name)
        archive.write(work_dir / "executive_summary.md", "executive_summary.md")

    return str(zip_path)
