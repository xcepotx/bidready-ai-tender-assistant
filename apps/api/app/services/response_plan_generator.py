def _default_owner(category: str, suggested_owner: str | None = None) -> str:
    if suggested_owner:
        return suggested_owner

    mapping = {
        "commercial_pricing": "commercial_team",
        "delivery_transition": "delivery_manager",
        "cloud_infrastructure": "solution_architect",
        "application_services": "solution_architect",
        "security_compliance": "security_compliance_team",
        "staffing_certification": "resource_manager",
        "submission": "bid_manager",
        "legal_contract": "legal_team",
    }

    return mapping.get(category, "bid_manager")


def _compliance_status(requirement) -> str:
    if requirement.status in {"accepted", "done"} and requirement.risk_level in {"low", "medium"}:
        return "likely_compliant"

    if requirement.status == "blocked":
        return "blocked"

    if requirement.status == "needs_clarification":
        return "needs_clarification"

    if requirement.risk_level == "high":
        return "needs_review"

    return "needs_review"


def _evidence_needed(requirement) -> list[str]:
    text = (requirement.requirement_text or "").lower()
    category = requirement.category or "general"

    evidence = []

    if category == "submission":
        evidence.append("Submission document checklist")
        evidence.append("Administrative document copy")

    if category == "commercial_pricing":
        evidence.append("Commercial proposal")
        evidence.append("Pricing assumptions and exclusions")
        evidence.append("Tax and validity confirmation")

    if category in {"delivery_transition", "scope"}:
        evidence.append("Implementation methodology")
        evidence.append("Delivery plan and timeline")
        evidence.append("Acceptance criteria")

    if category in {"cloud_infrastructure", "application_services"}:
        evidence.append("Solution architecture")
        evidence.append("Service scope and responsibility matrix")
        evidence.append("SLA / support model")

    if category == "security_compliance":
        evidence.append("Security compliance statement")
        evidence.append("Data protection approach")
        evidence.append("Relevant certification or policy reference")

    if category == "staffing_certification":
        evidence.append("Resource CV")
        evidence.append("Certification evidence")
        evidence.append("Resource availability confirmation")

    if "nib" in text:
        evidence.append("NIB document")

    if "npwp" in text:
        evidence.append("NPWP document")

    if "sertifikat" in text or "certification" in text:
        evidence.append("Certification document")

    if not evidence:
        evidence.append("Relevant proposal section and supporting evidence")

    return list(dict.fromkeys(evidence))


def _risks(requirement) -> list[str]:
    risks = []

    if requirement.risk_level == "high":
        risks.append("High-risk requirement requiring focused owner review.")

    if requirement.status == "needs_review":
        risks.append("Requirement has not been reviewed by responsible team.")

    if requirement.status == "blocked":
        risks.append("Requirement is currently blocked and may impact bid readiness.")

    if requirement.status == "needs_clarification":
        risks.append("Clarification is required before final response.")

    if not risks:
        risks.append("No major risk identified from current requirement status.")

    return risks


def _strategy(requirement) -> str:
    category = requirement.category or "general"

    if category == "commercial_pricing":
        return (
            "Confirm pricing structure, tax inclusion, commercial assumptions, exclusions, "
            "proposal validity, and payment terms before final submission."
        )

    if category == "delivery_transition":
        return (
            "Prepare a delivery methodology covering transition approach, timeline, governance, "
            "handover, and acceptance criteria."
        )

    if category in {"cloud_infrastructure", "application_services"}:
        return (
            "Prepare a solution response that maps service scope, architecture, support model, "
            "SLA, roles and responsibilities, and operational approach."
        )

    if category == "security_compliance":
        return (
            "Prepare security and compliance response covering data protection, access control, "
            "relevant certifications, auditability, and compliance obligations."
        )

    if category == "staffing_certification":
        return (
            "Confirm resource availability, role fit, certification evidence, CV format, and "
            "substitution rules."
        )

    if category == "submission":
        return (
            "Validate administrative submission checklist, document format, deadline, signing, "
            "and mandatory attachments."
        )

    return (
        "Review requirement with bid owner, prepare supporting evidence, and align response "
        "with proposal strategy."
    )


def _draft_response(requirement) -> str:
    category = requirement.category or "general"
    text = requirement.requirement_text

    if category == "submission":
        return (
            f"We acknowledge the submission requirement: {text}. "
            "The bid team will prepare and validate the required administrative documents prior to submission."
        )

    if category == "commercial_pricing":
        return (
            f"We acknowledge the commercial requirement: {text}. "
            "Our commercial response will clearly state pricing basis, tax treatment, assumptions, exclusions, "
            "payment terms, and proposal validity."
        )

    if category in {"delivery_transition", "scope"}:
        return (
            f"We acknowledge the delivery requirement: {text}. "
            "Our proposal will include the delivery methodology, implementation plan, governance model, "
            "handover approach, and acceptance criteria."
        )

    if category in {"cloud_infrastructure", "application_services"}:
        return (
            f"We acknowledge the service requirement: {text}. "
            "Our response will describe the proposed solution, service scope, operating model, support process, "
            "and responsibilities."
        )

    if category == "security_compliance":
        return (
            f"We acknowledge the security/compliance requirement: {text}. "
            "Our response will describe the applicable security controls, compliance approach, and supporting evidence."
        )

    if category == "staffing_certification":
        return (
            f"We acknowledge the staffing/certification requirement: {text}. "
            "We will provide resource profile, role mapping, certification evidence, and availability confirmation as required."
        )

    return (
        f"We acknowledge the requirement: {text}. "
        "The response will be reviewed by the responsible owner and supported with relevant evidence."
    )


def generate_response_plan_items(requirements) -> list[dict]:
    items = []

    for requirement in requirements:
        item = {
            "requirement_id": requirement.id,
            "project_id": requirement.project_id,
            "category": requirement.category or "general",
            "requirement_text": requirement.requirement_text,
            "compliance_status": _compliance_status(requirement),
            "response_strategy": _strategy(requirement),
            "draft_response": _draft_response(requirement),
            "evidence_needed": _evidence_needed(requirement),
            "assumptions": [
                "Response must be reviewed and approved by the responsible owner.",
                "Final client-facing language may need adjustment based on official proposal format.",
            ],
            "risks": _risks(requirement),
            "owner": _default_owner(requirement.category or "general", requirement.suggested_owner),
            "status": "draft",
            "confidence": min(max(requirement.confidence or 0.6, 0.3), 0.95),
            "source_page": requirement.source_page,
            "evidence_quote": requirement.evidence_quote,
            "notes": "Generated by rule-based response plan generator v1",
            "generation_mode": "rules_only",
        }
        items.append(item)

    return items
