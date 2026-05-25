IMPORTANT_CATEGORIES = {
    "cybersecurity_compliance",
    "managed_services_sla",
    "cloud_infrastructure",
    "commercial_pricing",
    "legal_contractual",
    "delivery_transition",
    "integration",
    "staffing_certification",
    "timeline",
    "submission",
}


def _shorten(text: str, limit: int = 220) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _priority_for(req) -> str:
    if req.risk_level == "high":
        return "high"
    if req.category in IMPORTANT_CATEGORIES:
        return "medium"
    return "low"


def _owner_for(req) -> str:
    if req.category == "cybersecurity_compliance":
        return "security_compliance_team"
    if req.category == "managed_services_sla":
        return "managed_services_team"
    if req.category == "cloud_infrastructure":
        return "cloud_infrastructure_team"
    if req.category == "commercial_pricing":
        return "commercial_team"
    if req.category == "legal_contractual":
        return "legal_team"
    if req.category == "delivery_transition":
        return "delivery_manager"
    if req.category == "integration":
        return "solution_architect"
    if req.category == "staffing_certification":
        return "resource_manager"
    if req.category in {"timeline", "submission"}:
        return "bid_manager"
    return req.suggested_owner or "bid_manager"


def generate_question_for_requirement(req) -> dict | None:
    text = _shorten(req.requirement_text)
    category = req.category

    should_generate = (
        req.risk_level == "high"
        or req.status in {"blocked", "needs_clarification"}
        or category in IMPORTANT_CATEGORIES
    )

    if not should_generate:
        return None

    if category == "cybersecurity_compliance":
        question = (
            "Please confirm the required security, compliance, data protection, audit, "
            f"and evidence expectations for this requirement: {text}"
        )
        reason = "Security/compliance requirements often require explicit confirmation and supporting evidence."

    elif category == "managed_services_sla":
        question = (
            "Please confirm support coverage, severity levels, response/resolution targets, "
            f"service credits, and SLA measurement method for: {text}"
        )
        reason = "Managed service/SLA obligations can impact delivery model, staffing, and pricing."

    elif category == "cloud_infrastructure":
        question = (
            "Please confirm target cloud/infrastructure environment, availability, backup, DR, "
            f"monitoring, and environment scope for: {text}"
        )
        reason = "Cloud/infrastructure scope can affect architecture, cost, and operational responsibility."

    elif category == "commercial_pricing":
        question = (
            "Please clarify commercial requirements including pricing format, tax inclusion, "
            f"proposal validity period, payment terms, assumptions, and exclusions for: {text}"
        )
        reason = "Commercial ambiguity can affect pricing structure, validity, margin, and proposal comparability."

    elif category == "legal_contractual":
        question = (
            "Please clarify contractual expectations, liability, penalties, warranty, confidentiality, "
            f"and data protection clauses related to: {text}"
        )
        reason = "Legal/contractual clauses require review before bid commitment."

    elif category == "delivery_transition":
        question = (
            "Please confirm transition timeline, knowledge transfer scope, handover expectations, "
            f"governance, and acceptance criteria for: {text}"
        )
        reason = "Transition requirements can affect project planning and delivery risk."

    elif category == "integration":
        question = (
            "Please confirm integration scope, systems involved, API/interface ownership, access, "
            f"test environment, and dependency assumptions for: {text}"
        )
        reason = "Integration scope often has hidden dependencies and delivery risks."

    elif category == "staffing_certification":
        question = (
            "Please confirm required roles, certification level, CV format, named resource requirement, "
            f"and substitution rules for: {text}"
        )
        reason = "Staffing/certification requirements can affect resource availability and bid feasibility."

    elif category in {"timeline", "submission"}:
        question = (
            "Please confirm submission deadline, allowed file format, submission channel, "
            f"required attachments, and clarification deadline for: {text}"
        )
        reason = "Submission/timeline requirements are mandatory and time-sensitive."

    else:
        question = (
            "Please clarify the expected response, required evidence, owner, and acceptance criteria "
            f"for this requirement: {text}"
        )
        reason = "Requirement needs human clarification before final bid response."

    return {
        "requirement_id": req.id,
        "category": category,
        "question_text": question,
        "reason": reason,
        "priority": _priority_for(req),
        "risk_level": req.risk_level,
        "source_page": req.source_page,
        "owner": _owner_for(req),
        "status": "open",
        "notes": None,
    }


def generate_clarification_questions(requirements) -> list[dict]:
    results = []
    seen = set()

    for req in requirements:
        item = generate_question_for_requirement(req)
        if not item:
            continue

        key = item["question_text"].lower()
        if key in seen:
            continue

        seen.add(key)
        results.append(item)

    return results
