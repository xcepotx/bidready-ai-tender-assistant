def _is_id(output_language: str) -> bool:
    return output_language == "id"


def _text(output_language: str, en: str, id_text: str) -> str:
    return id_text if _is_id(output_language) else en


def _short(value, limit=280):
    if value is None:
        return None
    text = str(value).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _priority(value: str | None) -> str:
    value = str(value or "medium").strip().lower()
    return value if value in {"high", "medium", "low"} else "medium"


def _risk(value: str | None) -> str:
    value = str(value or "medium").strip().lower()
    return value if value in {"high", "medium", "low"} else "medium"


def _tracker_status(clarification) -> str:
    status = str(getattr(clarification, "status", None) or "open").strip().lower()
    if status == "answered":
        return "answered"
    if status == "closed":
        return "closed"
    if status == "cancelled":
        return "closed"
    if status == "needs_internal_review":
        return "sent"
    return "open"


def _follow_up(output_language: str, tracker_status: str, priority: str, risk_level: str) -> str:
    if tracker_status == "answered":
        return _text(
            output_language,
            "Review client response, update response plan, compliance scorecard, and risk register where needed.",
            "Review jawaban client, update response plan, compliance scorecard, dan risk register jika diperlukan.",
        )

    if tracker_status == "closed":
        return _text(
            output_language,
            "Confirm the answer has been incorporated into final proposal artifacts.",
            "Pastikan jawaban sudah dimasukkan ke artifact proposal final.",
        )

    if priority == "high" or risk_level == "high":
        return _text(
            output_language,
            "Prioritize follow-up with client and escalate internally if no response is received before the clarification deadline.",
            "Prioritaskan follow-up ke client dan escalate internal jika belum ada jawaban sebelum deadline clarification.",
        )

    return _text(
        output_language,
        "Track response owner, due date, and update affected bid artifacts after answer is received.",
        "Pantau response owner, due date, dan update artifact tender terdampak setelah jawaban diterima.",
    )


def build_clarification_response_summary(items: list[dict]) -> dict:
    status_counts = {}
    priority_counts = {}
    risk_counts = {}

    for item in items:
        status_counts[item["response_status"]] = status_counts.get(item["response_status"], 0) + 1
        priority_counts[item["priority"]] = priority_counts.get(item["priority"], 0) + 1
        risk_counts[item["risk_level"]] = risk_counts.get(item["risk_level"], 0) + 1

    total = len(items)
    open_count = status_counts.get("open", 0)
    answered_count = status_counts.get("answered", 0) + status_counts.get("incorporated", 0) + status_counts.get("closed", 0)
    completion_percent = int(round((answered_count / total) * 100)) if total else 0

    if status_counts.get("overdue", 0):
        recommendation = "Overdue clarification responses require immediate follow-up."
    elif status_counts.get("open", 0):
        recommendation = "Open clarification responses should be tracked until client answers are incorporated."
    elif total:
        recommendation = "Clarification response tracking is in good shape."
    else:
        recommendation = "Generate tracker after clarification questions are available."

    return {
        "total_items": total,
        "open_items": open_count,
        "answered_items": answered_count,
        "overdue_items": status_counts.get("overdue", 0),
        "high_priority_items": priority_counts.get("high", 0),
        "high_risk_items": risk_counts.get("high", 0),
        "completion_percent": completion_percent,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "risk_counts": risk_counts,
        "recommendation": recommendation,
    }


def generate_clarification_response_payloads(
    *,
    clarifications=None,
    response_items=None,
    compliance_items=None,
    risk_items=None,
    addendum_impacts=None,
    output_language: str = "en",
) -> list[dict]:
    clarifications = clarifications or []
    response_items = response_items or []
    compliance_items = compliance_items or []
    risk_items = risk_items or []
    addendum_impacts = addendum_impacts or []

    response_by_req = {}
    for item in response_items:
        req_id = getattr(item, "requirement_id", None)
        if req_id:
            response_by_req.setdefault(req_id, []).append(item)

    compliance_by_req = {}
    for item in compliance_items:
        req_id = getattr(item, "requirement_id", None)
        if req_id:
            compliance_by_req.setdefault(req_id, []).append(item)

    risks_by_req = {}
    for item in risk_items:
        for req_id in getattr(item, "related_requirement_ids", None) or []:
            risks_by_req.setdefault(req_id, []).append(item)

    addendum_by_req = {}
    for item in addendum_impacts:
        for req_id in getattr(item, "related_requirement_ids", None) or []:
            addendum_by_req.setdefault(req_id, []).append(item)

    payloads = []

    for q in clarifications:
        req_id = getattr(q, "requirement_id", None)
        priority = _priority(getattr(q, "priority", None))
        risk_level = _risk(getattr(q, "risk_level", None))
        status = _tracker_status(q)

        related_response = response_by_req.get(req_id, [])
        related_compliance = compliance_by_req.get(req_id, [])
        related_risks = risks_by_req.get(req_id, [])
        related_addendum = addendum_by_req.get(req_id, [])

        impacted = ["clarifications"]
        if related_response:
            impacted.append("response_plan")
        if related_compliance:
            impacted.append("compliance_scorecard")
        if related_risks:
            impacted.append("risk_register")
        if related_addendum:
            impacted.append("addendum_impact")

        payloads.append({
            "clarification_id": getattr(q, "id", None),
            "requirement_id": req_id,
            "category": getattr(q, "category", None) or "general",
            "question_text": getattr(q, "question_text", None) or "",
            "reason": getattr(q, "reason", None),
            "client_response": None,
            "response_status": status,
            "priority": priority,
            "risk_level": risk_level,
            "owner": getattr(q, "owner", None) or "bid_manager",
            "due_date": None,
            "sent_at": None,
            "response_received_at": None,
            "incorporated_at": None,
            "impacted_artifacts": impacted,
            "related_response_item_ids": [getattr(item, "id", None) for item in related_response if getattr(item, "id", None)],
            "related_compliance_item_ids": [getattr(item, "id", None) for item in related_compliance if getattr(item, "id", None)],
            "related_risk_item_ids": [getattr(item, "id", None) for item in related_risks if getattr(item, "id", None)],
            "related_addendum_impact_ids": [getattr(item, "id", None) for item in related_addendum if getattr(item, "id", None)],
            "recommended_follow_up": _follow_up(output_language, status, priority, risk_level),
            "notes": _text(
                output_language,
                "Generated from clarification question and related bid artifacts.",
                "Dihasilkan dari clarification question dan artifact tender terkait.",
            ),
            "confidence": 0.78 if priority == "high" or risk_level == "high" else 0.68,
            "generation_mode": "rules_only",
        })

    payloads.sort(
        key=lambda item: (
            {"overdue": 0, "open": 1, "sent": 2, "answered": 3, "incorporated": 4, "closed": 5}.get(item["response_status"], 9),
            {"high": 0, "medium": 1, "low": 2}.get(item["priority"], 1),
            item["category"],
            item["clarification_id"] or 0,
        )
    )

    return payloads
