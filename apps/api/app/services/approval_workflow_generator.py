def _is_id(output_language: str) -> bool:
    return output_language == "id"


def _text(output_language: str, en: str, id_text: str) -> str:
    return id_text if _is_id(output_language) else en


def _normalize_role(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""

    if "legal" in text:
        return "legal_reviewer"
    if "finance" in text or "commercial" in text or "pricing" in text:
        return "commercial_owner"
    if "solution" in text or "technical" in text or "delivery" in text:
        return "solution_owner"
    if "executive" in text or "sponsor" in text or "director" in text:
        return "executive_sponsor"
    if "bid" in text or "proposal" in text:
        return "bid_manager"

    return text.replace(" ", "_")


def _role_label(role: str, output_language: str) -> str:
    labels = {
        "bid_manager": ("Bid Manager", "Bid Manager"),
        "solution_owner": ("Solution Owner", "Owner Solusi"),
        "commercial_owner": ("Commercial / Finance Owner", "Owner Komersial / Finance"),
        "legal_reviewer": ("Legal Reviewer", "Reviewer Legal"),
        "executive_sponsor": ("Executive Sponsor", "Executive Sponsor"),
    }
    en, id_text = labels.get(role, (role.replace("_", " ").title(), role.replace("_", " ").title()))
    return _text(output_language, en, id_text)


def build_approval_summary(request, steps) -> dict:
    steps = steps or []
    total = len(steps)
    approved = len([item for item in steps if item.status == "approved"])
    rejected = len([item for item in steps if item.status == "rejected"])
    changes_requested = len([item for item in steps if item.status == "changes_requested"])
    pending = len([item for item in steps if item.status == "pending"])
    not_started = len([item for item in steps if item.status == "not_started"])

    current_step = next((item for item in steps if item.status == "pending"), None)
    if not current_step:
        current_step = next((item for item in steps if item.status == "not_started"), None)

    progress_percent = int(round((approved / total) * 100)) if total else 0

    return {
        "status": request.status if request else "not_generated",
        "total_steps": total,
        "approved_steps": approved,
        "pending_steps": pending,
        "not_started_steps": not_started,
        "rejected_steps": rejected,
        "changes_requested_steps": changes_requested,
        "current_step_order": current_step.step_order if current_step else None,
        "current_role": current_step.role if current_step else None,
        "progress_percent": progress_percent,
    }


def generate_approval_workflow_payload(
    *,
    project,
    decision_gate=None,
    compliance_items=None,
    risk_items=None,
    action_items=None,
    output_language: str = "en",
) -> dict:
    compliance_items = compliance_items or []
    risk_items = risk_items or []
    action_items = action_items or []

    score = 0
    if compliance_items:
        weighted = sum((item.score or 0) * (item.weight or 1.0) for item in compliance_items)
        max_score = sum((item.max_score or 100) * (item.weight or 1.0) for item in compliance_items) or 1
        score = int(round((weighted / max_score) * 100))

    critical_risks = len([item for item in risk_items if item.severity in {"critical", "high"} and item.status not in {"closed", "accepted"}])
    non_compliant = len([item for item in compliance_items if item.compliance_status in {"non_compliant", "needs_clarification"}])
    open_actions = len([item for item in action_items if item.status not in {"done", "completed", "closed"}])

    required_roles = ["bid_manager", "solution_owner", "commercial_owner"]

    if non_compliant or critical_risks:
        required_roles.append("legal_reviewer")

    if decision_gate and getattr(decision_gate, "required_approvals", None):
        for item in decision_gate.required_approvals:
            role = _normalize_role(item)
            if role and role not in required_roles:
                required_roles.append(role)

    if critical_risks or (decision_gate and getattr(decision_gate, "decision_status", None) in {"needs_executive_review", "recommend_bid"}):
        if "executive_sponsor" not in required_roles:
            required_roles.append("executive_sponsor")

    # Keep deterministic order.
    role_order = ["bid_manager", "solution_owner", "commercial_owner", "legal_reviewer", "executive_sponsor"]
    required_roles = sorted(set(required_roles), key=lambda role: role_order.index(role) if role in role_order else 99)

    title = _text(
        output_language,
        f"Approval workflow for {project.title}",
        f"Approval workflow untuk {project.title}",
    )

    description = _text(
        output_language,
        f"Approval workflow generated from decision gate, compliance score {score}%, {critical_risks} critical/high risk(s), and {open_actions} open action(s).",
        f"Approval workflow dibuat dari decision gate, compliance score {score}%, {critical_risks} risiko critical/high, dan {open_actions} action item terbuka.",
    )

    notes = _text(
        output_language,
        "Generated workflow should be reviewed before formal submission.",
        "Workflow yang dihasilkan perlu direview sebelum submission approval formal.",
    )

    steps = []
    for index, role in enumerate(required_roles, start=1):
        steps.append({
            "step_order": index,
            "role": role,
            "approver_name": _role_label(role, output_language),
            "approver_email": None,
            "status": "not_started",
            "due_date": None,
            "decision_note": None,
            "decided_by": None,
            "decided_at": None,
        })

    return {
        "request": {
            "title": title,
            "description": description,
            "status": "draft",
            "current_step_order": None,
            "total_steps": len(steps),
            "approved_steps": 0,
            "submitted_by": None,
            "submitted_at": None,
            "completed_at": None,
            "final_decision": None,
            "notes": notes,
            "generation_mode": "rules_only",
        },
        "steps": steps,
    }
