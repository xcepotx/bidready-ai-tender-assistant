def _pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, part / total))


def compute_readiness_summary(project, documents, requirements, clarifications) -> dict:
    document_count = len(documents)
    requirement_count = len(requirements)
    clarification_count = len(clarifications)

    high_risk_requirement_count = len([r for r in requirements if r.risk_level == "high"])
    blocked_requirement_count = len([r for r in requirements if r.status == "blocked"])
    needs_review_requirement_count = len([r for r in requirements if r.status == "needs_review"])
    accepted_requirement_count = len([r for r in requirements if r.status == "accepted"])

    reviewed_requirement_count = len([
        r for r in requirements
        if r.status in {"accepted", "done", "rejected", "not_applicable", "needs_clarification", "blocked"}
    ])

    open_clarification_count = len([q for q in clarifications if q.status == "open"])
    high_priority_clarification_count = len([q for q in clarifications if q.priority == "high"])
    resolved_clarification_count = len([q for q in clarifications if q.status in {"answered", "closed", "cancelled"}])

    # Weighted readiness model v2.
    # This avoids making score 0 just because several risk signals overlap.
    score = 0.0

    # Basic intake completeness
    score += 15 if document_count > 0 else 0
    score += 15 if requirement_count > 0 else 0

    # Human review progress
    score += 25 * _pct(reviewed_requirement_count, requirement_count)

    # Risk quality
    if requirement_count > 0:
        non_high_risk_count = requirement_count - high_risk_requirement_count
        score += 20 * _pct(non_high_risk_count, requirement_count)

    # Clarification progress
    if clarification_count > 0:
        score += 15 * _pct(resolved_clarification_count, clarification_count)
    elif requirement_count > 0:
        # Not automatically bad, but clarification workflow has not been exercised yet.
        score += 5

    # Blocker status
    score += 10 if blocked_requirement_count == 0 else max(0, 10 - (blocked_requirement_count * 3))

    readiness_score = int(round(max(0, min(100, score))))

    signals = []

    if document_count == 0:
        signals.append({
            "severity": "high",
            "label": "No document uploaded",
            "message": "Upload at least one RFP or tender document before readiness review.",
        })

    if requirement_count == 0:
        signals.append({
            "severity": "high",
            "label": "No requirements analyzed",
            "message": "Run RFP analysis to generate the requirement matrix.",
        })

    if high_risk_requirement_count > 0:
        signals.append({
            "severity": "high",
            "label": "High-risk requirements",
            "message": f"{high_risk_requirement_count} requirement(s) are marked high risk and need focused review.",
        })

    if blocked_requirement_count > 0:
        signals.append({
            "severity": "high",
            "label": "Blocked requirements",
            "message": f"{blocked_requirement_count} requirement(s) are blocked and may affect bid readiness.",
        })

    if needs_review_requirement_count > 0:
        signals.append({
            "severity": "medium",
            "label": "Requirements need review",
            "message": f"{needs_review_requirement_count} requirement(s) still need human review.",
        })

    if open_clarification_count > 0:
        signals.append({
            "severity": "medium",
            "label": "Open clarification questions",
            "message": f"{open_clarification_count} clarification question(s) are still open.",
        })

    if high_priority_clarification_count > 0:
        signals.append({
            "severity": "high",
            "label": "High-priority clarifications",
            "message": f"{high_priority_clarification_count} clarification question(s) are high priority.",
        })

    if not signals:
        signals.append({
            "severity": "low",
            "label": "No major blocker detected",
            "message": "No major readiness blocker detected from current review data.",
        })

    if readiness_score >= 85:
        recommendation = "Ready for final review"
    elif readiness_score >= 65:
        recommendation = "Proceed with clarification"
    elif readiness_score >= 40:
        recommendation = "Needs focused bid review"
    else:
        recommendation = "Not ready"

    return {
        "project_id": project.id,
        "project_title": project.title,
        "readiness_score": readiness_score,
        "recommendation": recommendation,
        "document_count": document_count,
        "requirement_count": requirement_count,
        "clarification_count": clarification_count,
        "high_risk_requirement_count": high_risk_requirement_count,
        "blocked_requirement_count": blocked_requirement_count,
        "needs_review_requirement_count": needs_review_requirement_count,
        "accepted_requirement_count": accepted_requirement_count,
        "open_clarification_count": open_clarification_count,
        "high_priority_clarification_count": high_priority_clarification_count,
        "signals": signals,
    }
