def _count(items, predicate):
    return len([item for item in items if predicate(item)])


def _unique(items):
    output = []
    seen = set()

    for item in items:
        if not item:
            continue

        key = str(item).strip().lower()
        if not key or key in seen:
            continue

        seen.add(key)
        output.append(str(item).strip())

    return output


def generate_decision_gate_payload(
    *,
    project,
    readiness_summary,
    metadata=None,
    requirements=None,
    clarifications=None,
    response_items=None,
    proposal_sections=None,
    evidence_items=None,
) -> dict:
    requirements = requirements or []
    clarifications = clarifications or []
    response_items = response_items or []
    proposal_sections = proposal_sections or []
    evidence_items = evidence_items or []

    readiness_score = int(readiness_summary.get("readiness_score", 0))
    readiness_recommendation = readiness_summary.get("recommendation", "Not available")

    high_risk_requirements = _count(requirements, lambda r: r.risk_level == "high")
    blocked_requirements = _count(requirements, lambda r: r.status == "blocked")
    needs_review_requirements = _count(requirements, lambda r: r.status == "needs_review")
    open_clarifications = _count(clarifications, lambda q: q.status == "open")
    high_priority_clarifications = _count(clarifications, lambda q: q.priority == "high")

    blocked_response_items = _count(response_items, lambda item: item.status == "blocked" or item.compliance_status == "blocked")
    non_compliant_items = _count(response_items, lambda item: item.compliance_status == "non_compliant")
    draft_proposal_sections = _count(proposal_sections, lambda section: section.status == "draft")
    blocked_evidence = _count(evidence_items, lambda item: item.status == "blocked")
    open_high_priority_evidence = _count(evidence_items, lambda item: item.priority == "high" and item.status in {"open", "requested"})

    blockers = []

    if blocked_requirements:
        blockers.append(f"{blocked_requirements} requirement(s) are blocked.")

    if non_compliant_items:
        blockers.append(f"{non_compliant_items} response item(s) are marked non-compliant.")

    if blocked_response_items:
        blockers.append(f"{blocked_response_items} response item(s) are blocked.")

    if blocked_evidence:
        blockers.append(f"{blocked_evidence} evidence item(s) are blocked.")

    if high_priority_clarifications:
        blockers.append(f"{high_priority_clarifications} high-priority clarification question(s) are still present.")

    if open_high_priority_evidence:
        blockers.append(f"{open_high_priority_evidence} high-priority evidence item(s) are still open/requested.")

    key_reasons = []

    if readiness_score >= 65:
        key_reasons.append(f"Readiness score is {readiness_score}, indicating the bid can proceed with controlled review.")
    else:
        key_reasons.append(f"Readiness score is {readiness_score}, indicating additional review is required before commitment.")

    if len(requirements) > 0:
        key_reasons.append(f"{len(requirements)} requirement item(s) have been extracted and structured.")

    if len(response_items) > 0:
        key_reasons.append(f"{len(response_items)} response plan item(s) are available for proposal preparation.")

    if len(proposal_sections) > 0:
        key_reasons.append(f"{len(proposal_sections)} proposal outline section(s) have been prepared.")

    if len(evidence_items) > 0:
        key_reasons.append(f"{len(evidence_items)} evidence item(s) are tracked in the evidence pack.")

    if needs_review_requirements:
        key_reasons.append(f"{needs_review_requirements} requirement(s) still need owner review.")

    if open_clarifications:
        key_reasons.append(f"{open_clarifications} clarification question(s) remain open.")

    required_approvals = []

    if high_risk_requirements or blocked_requirements:
        required_approvals.append("Bid Manager approval for high-risk and blocked requirements.")

    if non_compliant_items or blocked_response_items:
        required_approvals.append("Solution / Delivery approval for blocked or non-compliant response items.")

    if open_high_priority_evidence or blocked_evidence:
        required_approvals.append("Evidence owner confirmation for high-priority or blocked supporting documents.")

    if any((r.category or "") == "commercial_pricing" for r in requirements):
        required_approvals.append("Commercial approval for pricing, tax, validity, and assumptions.")

    if any((r.category or "") in {"security_compliance", "data_ai"} for r in requirements):
        required_approvals.append("Security / Compliance approval for data, AI, security, and regulatory obligations.")

    if not required_approvals:
        required_approvals.append("Final bid manager approval before submission.")

    next_actions = []

    if needs_review_requirements:
        next_actions.append("Complete human review for all needs_review requirements.")

    if open_clarifications:
        next_actions.append("Resolve open clarification questions or document assumptions.")

    if len(response_items) == 0:
        next_actions.append("Generate response plan from requirement matrix.")

    if len(proposal_sections) == 0:
        next_actions.append("Generate proposal outline from response plan.")

    if len(evidence_items) == 0:
        next_actions.append("Generate evidence pack and assign evidence owners.")

    if open_high_priority_evidence:
        next_actions.append("Collect and validate high-priority evidence before submission.")

    if draft_proposal_sections:
        next_actions.append("Move proposal sections from draft to in_review or ready.")

    if not next_actions:
        next_actions.append("Proceed to final executive review and submission approval.")

    # Decision logic
    if blocked_requirements > 0 or non_compliant_items > 0 or readiness_score < 30:
        decision_status = "recommend_no_bid"
        recommendation = "Recommend No-Bid or Executive Exception Review"
        confidence = 0.82
    elif blockers or readiness_score < 65:
        decision_status = "needs_executive_review"
        recommendation = "Needs Executive Review Before Bid Commitment"
        confidence = 0.78
    elif readiness_score >= 85 and not blockers:
        decision_status = "recommend_bid"
        recommendation = "Recommend Bid - Ready for Final Approval"
        confidence = 0.86
    else:
        decision_status = "recommend_bid"
        recommendation = "Recommend Bid with Controlled Risk Review"
        confidence = 0.80

    package_name = metadata.package_name if metadata and metadata.package_name else project.title
    issuer = metadata.issuer if metadata and metadata.issuer else project.issuer
    deadline = metadata.submission_deadline if metadata else None

    deadline_text = f" Submission deadline: {deadline}." if deadline else ""

    executive_summary = (
        f"This decision gate evaluates whether to pursue {package_name} "
        f"from {issuer or 'the client'}. Current readiness recommendation is "
        f"'{readiness_recommendation}' with a score of {readiness_score}."
        f"{deadline_text} The system identified {len(requirements)} requirement(s), "
        f"{len(response_items)} response item(s), {len(proposal_sections)} proposal section(s), "
        f"and {len(evidence_items)} evidence item(s)."
    )

    return {
        "decision_status": decision_status,
        "recommendation": recommendation,
        "readiness_score": readiness_score,
        "confidence": confidence,
        "executive_summary": executive_summary,
        "key_reasons": _unique(key_reasons),
        "blockers": _unique(blockers) or ["No hard blocker detected from current decision data."],
        "required_approvals": _unique(required_approvals),
        "next_actions": _unique(next_actions),
        "owner": "bid_manager",
        "due_date": deadline,
        "notes": "Generated by rule-based decision gate generator v1",
        "generation_mode": "rules_only",
    }
