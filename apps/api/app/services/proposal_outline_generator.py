from collections import defaultdict


def _unique_list(items):
    cleaned = []
    seen = set()

    for item in items:
        if not item:
            continue

        key = str(item).strip().lower()
        if not key or key in seen:
            continue

        seen.add(key)
        cleaned.append(str(item).strip())

    return cleaned


def _items_by_category(response_items):
    grouped = defaultdict(list)

    for item in response_items:
        grouped[item.category or "general"].append(item)

    return grouped


def _collect_ids(items):
    return [item.id for item in items if item.id]


def _collect_evidence(items):
    evidence = []

    for item in items:
        evidence.extend(item.evidence_needed or [])

    return _unique_list(evidence)


def _collect_risks(items):
    risks = []

    for item in items:
        risks.extend(item.risks or [])

    return _unique_list(risks)


def _draft_from_items(title, items, fallback_message):
    if not items:
        return fallback_message

    lines = [
        f"This section addresses {len(items)} response item(s) related to {title.lower()}."
    ]

    for item in items[:8]:
        lines.append(f"- {item.requirement_text}")

    return "\n".join(lines)


def generate_proposal_outline_sections(project, response_items, metadata=None) -> list[dict]:
    grouped = _items_by_category(response_items)

    all_items = list(response_items)

    cloud_items = grouped.get("cloud_infrastructure", []) + grouped.get("application_services", [])
    delivery_items = grouped.get("delivery_transition", []) + grouped.get("scope", [])
    security_items = grouped.get("security_compliance", []) + grouped.get("data_ai", [])
    commercial_items = grouped.get("commercial_pricing", [])
    staffing_items = grouped.get("staffing_certification", [])
    submission_items = grouped.get("submission", [])
    general_items = grouped.get("general", [])

    project_title = getattr(project, "title", "this tender")
    issuer = getattr(project, "issuer", None) or "the client"
    service_domain = getattr(project, "tender_type", None) or "the requested service scope"

    if metadata:
        service_domain = metadata.service_domain or service_domain
        project_title = metadata.package_name or project_title
        issuer = metadata.issuer or issuer

    sections = [
        {
            "section_key": "executive_summary",
            "title": "Executive Summary",
            "section_order": 1,
            "purpose": "Provide a concise business-level overview of the proposed response and why the bidder is suitable.",
            "content_outline": [
                f"Summarize understanding of {project_title}.",
                f"Position the response around {service_domain}.",
                "Highlight key strengths, delivery confidence, and readiness.",
                "Mention that detailed compliance, evidence, and assumptions are addressed in later sections.",
            ],
            "draft_content": (
                f"This proposal responds to {project_title} issued by {issuer}. "
                f"The response is structured to demonstrate understanding of the requirements, proposed solution, "
                f"delivery approach, governance, compliance considerations, and supporting evidence. "
                f"The current response plan contains {len(all_items)} mapped response item(s)."
            ),
            "source_response_item_ids": _collect_ids(all_items[:10]),
            "evidence_needed": _collect_evidence(all_items),
            "risks": _collect_risks(all_items),
            "owner": "bid_manager",
        },
        {
            "section_key": "understanding_of_requirements",
            "title": "Understanding of Requirements",
            "section_order": 2,
            "purpose": "Show that the bidder understands the client's scope, constraints, and mandatory requirements.",
            "content_outline": [
                "Summarize the client context and requested scope.",
                "Map key RFP requirements into business, technical, commercial, and administrative themes.",
                "Call out assumptions and areas requiring clarification.",
            ],
            "draft_content": _draft_from_items(
                "Understanding of Requirements",
                all_items,
                "This section should summarize the client's stated requirements and constraints.",
            ),
            "source_response_item_ids": _collect_ids(all_items),
            "evidence_needed": _collect_evidence(all_items),
            "risks": _collect_risks(all_items),
            "owner": "bid_manager",
        },
        {
            "section_key": "proposed_solution",
            "title": "Proposed Solution",
            "section_order": 3,
            "purpose": "Describe the proposed technical and service solution mapped to the RFP requirements.",
            "content_outline": [
                "Describe proposed architecture or service model.",
                "Explain service scope and responsibility matrix.",
                "Align solution components with application, cloud, infrastructure, or managed service requirements.",
                "Reference relevant evidence and assumptions.",
            ],
            "draft_content": _draft_from_items(
                "Proposed Solution",
                cloud_items + general_items,
                "This section should describe the proposed solution and how it meets the RFP requirements.",
            ),
            "source_response_item_ids": _collect_ids(cloud_items + general_items),
            "evidence_needed": _collect_evidence(cloud_items + general_items),
            "risks": _collect_risks(cloud_items + general_items),
            "owner": "solution_architect",
        },
        {
            "section_key": "delivery_methodology",
            "title": "Delivery Methodology",
            "section_order": 4,
            "purpose": "Explain implementation, transition, governance, timeline, and acceptance approach.",
            "content_outline": [
                "Describe delivery phases and transition approach.",
                "Provide timeline and milestones.",
                "Explain governance, reporting cadence, escalation, and acceptance process.",
                "Include staffing and certification approach where relevant.",
            ],
            "draft_content": _draft_from_items(
                "Delivery Methodology",
                delivery_items + staffing_items,
                "This section should explain the delivery methodology, transition plan, and staffing approach.",
            ),
            "source_response_item_ids": _collect_ids(delivery_items + staffing_items),
            "evidence_needed": _collect_evidence(delivery_items + staffing_items),
            "risks": _collect_risks(delivery_items + staffing_items),
            "owner": "delivery_manager",
        },
        {
            "section_key": "governance_sla",
            "title": "Governance & SLA",
            "section_order": 5,
            "purpose": "Define service governance, operating model, SLA, reporting, and issue management.",
            "content_outline": [
                "Describe governance model and stakeholder roles.",
                "Explain SLA or support commitments.",
                "Define issue, incident, escalation, and reporting process.",
                "Clarify assumptions and dependencies.",
            ],
            "draft_content": (
                "This section should define the governance model, operational cadence, reporting mechanism, "
                "and service management practices required to operate the proposed service."
            ),
            "source_response_item_ids": _collect_ids(cloud_items + delivery_items),
            "evidence_needed": _collect_evidence(cloud_items + delivery_items),
            "risks": _collect_risks(cloud_items + delivery_items),
            "owner": "delivery_manager",
        },
        {
            "section_key": "security_compliance",
            "title": "Security & Compliance",
            "section_order": 6,
            "purpose": "Address security, data protection, compliance, auditability, and certification requirements.",
            "content_outline": [
                "Describe security controls and compliance approach.",
                "Explain data protection and access management.",
                "List relevant policy, process, certification, or audit evidence.",
                "Identify areas that require legal or security review.",
            ],
            "draft_content": _draft_from_items(
                "Security & Compliance",
                security_items,
                "This section should address security, compliance, data protection, and audit requirements.",
            ),
            "source_response_item_ids": _collect_ids(security_items),
            "evidence_needed": _collect_evidence(security_items),
            "risks": _collect_risks(security_items),
            "owner": "security_compliance_team",
        },
        {
            "section_key": "commercial_assumptions",
            "title": "Commercial Assumptions",
            "section_order": 7,
            "purpose": "State pricing basis, tax treatment, payment terms, validity, exclusions, and commercial assumptions.",
            "content_outline": [
                "Summarize pricing basis and tax treatment.",
                "State proposal validity and payment assumptions.",
                "List exclusions, dependencies, and commercial risks.",
                "Reference commercial response items requiring approval.",
            ],
            "draft_content": _draft_from_items(
                "Commercial Assumptions",
                commercial_items,
                "This section should capture pricing assumptions, taxes, payment terms, validity, and exclusions.",
            ),
            "source_response_item_ids": _collect_ids(commercial_items),
            "evidence_needed": _collect_evidence(commercial_items),
            "risks": _collect_risks(commercial_items),
            "owner": "commercial_team",
        },
        {
            "section_key": "submission_checklist",
            "title": "Submission Checklist & Appendices",
            "section_order": 8,
            "purpose": "Prepare administrative attachments, required forms, supporting evidence, and final submission checklist.",
            "content_outline": [
                "List administrative documents required by the RFP.",
                "List technical, commercial, staffing, and compliance appendices.",
                "Confirm signing, formatting, deadline, and submission method.",
                "Track evidence owners and readiness status.",
            ],
            "draft_content": _draft_from_items(
                "Submission Checklist & Appendices",
                submission_items,
                "This section should list administrative attachments and supporting appendices required for submission.",
            ),
            "source_response_item_ids": _collect_ids(submission_items),
            "evidence_needed": _collect_evidence(submission_items + all_items),
            "risks": _collect_risks(submission_items),
            "owner": "bid_manager",
        },
    ]

    for section in sections:
        section["status"] = "draft"
        section["notes"] = "Generated by rule-based proposal outline generator v1"
        section["generation_mode"] = "rules_only"

    return sections
