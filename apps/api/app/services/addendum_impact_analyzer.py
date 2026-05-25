def _is_id(output_language: str) -> bool:
    return output_language == "id"


def _text(output_language: str, en: str, id_text: str) -> str:
    return id_text if _is_id(output_language) else en


def _short(value, limit=260):
    if value is None:
        return None
    text = str(value).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _owner(*values):
    for value in values:
        if value:
            return value
    return "bid_manager"


def _severity(value: str | None, default: str = "medium") -> str:
    value = str(value or default).strip().lower().replace("-", "_").replace(" ", "_")
    mapped = {
        "mandatory": "high",
        "blocked": "critical",
        "non_compliant": "critical",
        "needs_clarification": "high",
        "partially_compliant": "medium",
    }.get(value, value)
    return mapped if mapped in {"critical", "high", "medium", "low"} else default


def _rank(value: str | None) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(value or "medium", 2)


def build_addendum_impact_summary(items: list[dict]) -> dict:
    severity_counts = {}
    artifact_counts = {}
    status_counts = {}

    for item in items:
        severity_counts[item["severity"]] = severity_counts.get(item["severity"], 0) + 1
        artifact_counts[item["impacted_artifact"]] = artifact_counts.get(item["impacted_artifact"], 0) + 1
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    critical = severity_counts.get("critical", 0)
    high = severity_counts.get("high", 0)

    if critical:
        recommendation = "Critical document impacts require immediate review before bid submission."
    elif high:
        recommendation = "High impact addendum changes should be reviewed by owners before approval."
    elif items:
        recommendation = "Addendum impacts are manageable but should be tracked to closure."
    else:
        recommendation = "No addendum impact items generated."

    return {
        "total_items": len(items),
        "open_items": status_counts.get("open", 0),
        "critical_items": critical,
        "high_items": high,
        "severity_counts": severity_counts,
        "artifact_counts": artifact_counts,
        "status_counts": status_counts,
        "recommendation": recommendation,
    }


def generate_addendum_impact_payloads(
    *,
    document=None,
    document_text: str = "",
    requirements=None,
    clarifications=None,
    response_items=None,
    compliance_items=None,
    risk_items=None,
    approval_steps=None,
    decision_gate=None,
    output_language: str = "en",
) -> list[dict]:
    requirements = requirements or []
    clarifications = clarifications or []
    response_items = response_items or []
    compliance_items = compliance_items or []
    risk_items = risk_items or []
    approval_steps = approval_steps or []

    document_id = getattr(document, "id", None)
    document_name = getattr(document, "filename", None)
    doc_excerpt = _short(document_text, 320)

    payloads = []
    seen = set()

    def add(payload):
        payload["document_id"] = document_id
        payload["source_document_name"] = document_name
        payload["status"] = payload.get("status") or "open"
        payload["confidence"] = payload.get("confidence") or 0.70
        payload["generation_mode"] = "rules_only"

        key = (
            payload.get("impacted_artifact"),
            payload.get("title"),
            tuple(payload.get("related_requirement_ids") or []),
            tuple(payload.get("related_response_item_ids") or []),
            tuple(payload.get("related_clarification_ids") or []),
            tuple(payload.get("related_compliance_item_ids") or []),
            tuple(payload.get("related_risk_item_ids") or []),
        )
        if key in seen:
            return
        seen.add(key)
        payloads.append(payload)

    for req in requirements:
        req_id = getattr(req, "id", None)
        status = getattr(req, "status", None)
        priority = getattr(req, "priority", None)
        risk_level = getattr(req, "risk_level", None)
        category = getattr(req, "category", None) or "general"
        req_text = getattr(req, "requirement_text", None) or ""

        if priority not in {"mandatory", "high"} and risk_level != "high" and status not in {"blocked", "needs_review", "needs_clarification"}:
            continue

        sev = "critical" if status == "blocked" else "high" if priority in {"mandatory", "high"} or risk_level == "high" else "medium"

        add({
            "title": _text(output_language, f"Requirement may be impacted: {category}", f"Requirement kemungkinan terdampak: {category}"),
            "summary": _text(output_language, "Review whether revised document changes scope, deadline, compliance, or response wording.", "Review apakah dokumen revisi mengubah scope, deadline, compliance, atau wording response."),
            "impact_type": "requirement_change",
            "impacted_artifact": "requirements",
            "severity": _severity(sev),
            "source_excerpt": _short(getattr(req, "evidence_quote", None) or req_text, 320) or doc_excerpt,
            "recommended_action": _text(output_language, "Confirm if requirement text, owner, priority, and risk rating need update.", "Konfirmasi apakah teks requirement, owner, priority, dan risk rating perlu diupdate."),
            "owner": _owner(getattr(req, "suggested_owner", None)),
            "due_date": None,
            "related_requirement_ids": [req_id] if req_id else [],
            "related_response_item_ids": [],
            "related_clarification_ids": [],
            "related_compliance_item_ids": [],
            "related_risk_item_ids": [],
            "related_approval_step_ids": [],
            "notes": _text(output_language, "Generated from document impact scan against requirements.", "Dihasilkan dari scan dampak dokumen terhadap requirements."),
        })

    for q in clarifications:
        q_id = getattr(q, "id", None)
        status = getattr(q, "status", None)
        priority = getattr(q, "priority", None)
        risk_level = getattr(q, "risk_level", None)

        if status not in {"open", "draft", "pending", "blocked"} and priority != "high" and risk_level != "high":
            continue

        add({
            "title": _text(output_language, "Clarification may need revision", "Clarification mungkin perlu direvisi"),
            "summary": _short(getattr(q, "question_text", None), 260),
            "impact_type": "clarification_change",
            "impacted_artifact": "clarifications",
            "severity": "high" if priority == "high" or risk_level == "high" or status == "blocked" else "medium",
            "source_excerpt": _short(getattr(q, "question_text", None), 320) or doc_excerpt,
            "recommended_action": _text(output_language, "Check whether revised document answers this clarification or requires a revised client question.", "Cek apakah dokumen revisi menjawab clarification ini atau membutuhkan pertanyaan revisi ke client."),
            "owner": _owner(getattr(q, "owner", None)),
            "due_date": None,
            "related_requirement_ids": [getattr(q, "requirement_id", None)] if getattr(q, "requirement_id", None) else [],
            "related_response_item_ids": [],
            "related_clarification_ids": [q_id] if q_id else [],
            "related_compliance_item_ids": [],
            "related_risk_item_ids": [],
            "related_approval_step_ids": [],
            "notes": _text(output_language, "Generated from open/high-risk clarification after document scan.", "Dihasilkan dari clarification open/high-risk setelah scan dokumen."),
        })

    for comp in compliance_items:
        comp_id = getattr(comp, "id", None)
        status = getattr(comp, "compliance_status", None)
        score = getattr(comp, "score", None) or 0
        risk_level = getattr(comp, "risk_level", None)
        evidence_coverage = getattr(comp, "evidence_coverage", None)

        if status == "compliant" and evidence_coverage == "covered" and score >= 85:
            continue

        sev = "critical" if status in {"non_compliant", "needs_clarification"} or score < 35 else "high" if score < 65 or risk_level == "high" else "medium"

        add({
            "title": _text(output_language, "Compliance scorecard impact", "Dampak pada compliance scorecard"),
            "summary": _text(output_language, f"Compliance score is {score} with status {status}; review may be required.", f"Compliance score {score} dengan status {status}; review mungkin dibutuhkan."),
            "impact_type": "compliance_change",
            "impacted_artifact": "compliance_scorecard",
            "severity": sev,
            "source_excerpt": _short(getattr(comp, "requirement_text", None), 320) or doc_excerpt,
            "recommended_action": _text(output_language, "Revalidate compliance status, evidence coverage, and gap summary against the revised document.", "Validasi ulang status compliance, coverage evidence, dan gap summary terhadap dokumen revisi."),
            "owner": _owner(getattr(comp, "owner", None)),
            "due_date": None,
            "related_requirement_ids": [getattr(comp, "requirement_id", None)] if getattr(comp, "requirement_id", None) else [],
            "related_response_item_ids": [getattr(comp, "response_item_id", None)] if getattr(comp, "response_item_id", None) else [],
            "related_clarification_ids": [],
            "related_compliance_item_ids": [comp_id] if comp_id else [],
            "related_risk_item_ids": [],
            "related_approval_step_ids": [],
            "notes": _text(output_language, "Generated from compliance scorecard status/score after document scan.", "Dihasilkan dari status/score compliance scorecard setelah scan dokumen."),
        })

    for item in response_items:
        item_id = getattr(item, "id", None)
        status = getattr(item, "status", None)
        compliance_status = getattr(item, "compliance_status", None)
        risks = getattr(item, "risks", None) or []

        if status not in {"blocked", "needs_review", "draft", "open"} and compliance_status not in {"partially_compliant", "needs_clarification", "non_compliant"} and not risks:
            continue

        add({
            "title": _text(output_language, "Response plan may need update", "Response plan mungkin perlu diupdate"),
            "summary": _short(getattr(item, "requirement_text", None), 260),
            "impact_type": "response_change",
            "impacted_artifact": "response_plan",
            "severity": "high" if compliance_status in {"needs_clarification", "non_compliant"} or status == "blocked" else "medium",
            "source_excerpt": _short(getattr(item, "requirement_text", None), 320) or doc_excerpt,
            "recommended_action": _text(output_language, "Update response strategy, draft response, assumptions, risks, and evidence checklist if scope changed.", "Update response strategy, draft response, assumptions, risks, dan evidence checklist jika scope berubah."),
            "owner": _owner(getattr(item, "owner", None)),
            "due_date": None,
            "related_requirement_ids": [getattr(item, "requirement_id", None)] if getattr(item, "requirement_id", None) else [],
            "related_response_item_ids": [item_id] if item_id else [],
            "related_clarification_ids": [],
            "related_compliance_item_ids": [],
            "related_risk_item_ids": [],
            "related_approval_step_ids": [],
            "notes": _text(output_language, "Generated from response plan status/compliance/risks after document scan.", "Dihasilkan dari status/compliance/risks response plan setelah scan dokumen."),
        })

    for risk in risk_items:
        risk_id = getattr(risk, "id", None)
        sev = getattr(risk, "severity", None)
        status = getattr(risk, "status", None)

        if sev not in {"critical", "high"} and status not in {"open", "escalated"}:
            continue

        add({
            "title": _text(output_language, "Risk register impact", "Dampak pada risk register"),
            "summary": _short(getattr(risk, "description", None) or getattr(risk, "title", None), 260),
            "impact_type": "risk_change",
            "impacted_artifact": "risk_register",
            "severity": _severity(sev, "high"),
            "source_excerpt": _short(getattr(risk, "trigger_event", None) or getattr(risk, "description", None), 320) or doc_excerpt,
            "recommended_action": _text(output_language, "Review mitigation, contingency, owner, and escalation status against the revised document.", "Review mitigation, contingency, owner, dan status escalation terhadap dokumen revisi."),
            "owner": _owner(getattr(risk, "owner", None)),
            "due_date": getattr(risk, "due_date", None),
            "related_requirement_ids": getattr(risk, "related_requirement_ids", None) or [],
            "related_response_item_ids": getattr(risk, "related_response_item_ids", None) or [],
            "related_clarification_ids": getattr(risk, "related_clarification_ids", None) or [],
            "related_compliance_item_ids": [],
            "related_risk_item_ids": [risk_id] if risk_id else [],
            "related_approval_step_ids": [],
            "notes": _text(output_language, "Generated from high/open risk after document scan.", "Dihasilkan dari high/open risk setelah scan dokumen."),
        })

    if decision_gate:
        blockers = getattr(decision_gate, "blockers", None) or []
        required_approvals = getattr(decision_gate, "required_approvals", None) or []
        if blockers or required_approvals or getattr(decision_gate, "decision_status", None) != "approved":
            add({
                "title": _text(output_language, "Decision gate may require re-approval", "Decision gate mungkin perlu re-approval"),
                "summary": _text(output_language, "Revised document can affect go/no-go rationale, blockers, approvals, and next actions.", "Dokumen revisi dapat memengaruhi rationale go/no-go, blockers, approvals, dan next actions."),
                "impact_type": "approval_change",
                "impacted_artifact": "decision_gate",
                "severity": "high" if blockers else "medium",
                "source_excerpt": _short(getattr(decision_gate, "recommendation", None), 320) or doc_excerpt,
                "recommended_action": _text(output_language, "Re-run decision gate and confirm whether approval workflow should be resubmitted.", "Generate ulang decision gate dan konfirmasi apakah approval workflow perlu disubmit ulang."),
                "owner": _owner(getattr(decision_gate, "owner", None)),
                "due_date": getattr(decision_gate, "due_date", None),
                "related_requirement_ids": [],
                "related_response_item_ids": [],
                "related_clarification_ids": [],
                "related_compliance_item_ids": [],
                "related_risk_item_ids": [],
                "related_approval_step_ids": [getattr(step, "id", None) for step in approval_steps if getattr(step, "id", None)],
                "notes": _text(output_language, "Generated from decision gate and approval workflow after document scan.", "Dihasilkan dari decision gate dan approval workflow setelah scan dokumen."),
            })

    payloads.sort(key=lambda item: (_rank(item["severity"]), item["impacted_artifact"], item["title"]))
    return payloads[:120]
