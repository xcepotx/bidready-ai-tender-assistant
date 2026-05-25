DECISION_ACTIONS = {"generate_decision_gate", "update_decision_gate"}
APPROVAL_ACTIONS = {
    "generate_approval_workflow",
    "submit_approval_workflow",
    "update_approval_step",
}


def _get(data, *path, default=None):
    current = data or {}
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default


def _compact(value, limit=180):
    if value is None:
        return None
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _changed_fields(before: dict | None, after: dict | None, keys: list[str]) -> list[str]:
    fields = []
    before = before or {}
    after = after or {}

    for key in keys:
        if before.get(key) != after.get(key):
            fields.append(key)

    return fields


def _event_type(action: str) -> str:
    if action in DECISION_ACTIONS:
        return "decision_gate"
    if action == "update_approval_step":
        return "approval_step"
    if action in APPROVAL_ACTIONS:
        return "approval_workflow"
    return "other"


def _event_title(action: str) -> str:
    return {
        "generate_decision_gate": "Decision gate generated",
        "update_decision_gate": "Decision gate updated",
        "generate_approval_workflow": "Approval workflow generated",
        "submit_approval_workflow": "Approval workflow submitted",
        "update_approval_step": "Approval step updated",
    }.get(action, action.replace("_", " ").title())


def _extract_status(action: str, before_json: dict | None, after_json: dict | None) -> tuple[str | None, str | None]:
    if action in DECISION_ACTIONS:
        return (
            _get(before_json, "decision_status"),
            _get(after_json, "decision_status"),
        )

    if action == "update_approval_step":
        return (
            _get(before_json, "step", "status"),
            _get(after_json, "step", "status"),
        )

    if action in {"generate_approval_workflow", "submit_approval_workflow"}:
        return (
            _get(before_json, "status") or _get(before_json, "request", "status"),
            _get(after_json, "status") or _get(after_json, "request", "status"),
        )

    return None, None


def _extract_actor_target(action: str, after_json: dict | None) -> str | None:
    if action == "update_approval_step":
        role = _get(after_json, "step", "role")
        approver = _get(after_json, "step", "approver_name")
        return approver or role

    if action in {"generate_approval_workflow", "submit_approval_workflow"}:
        return _get(after_json, "submitted_by") or _get(after_json, "request", "submitted_by")

    return _get(after_json, "owner")


def _extract_score(action: str, before_json: dict | None, after_json: dict | None) -> tuple[int | None, int | None]:
    if action in DECISION_ACTIONS:
        return (
            _get(before_json, "readiness_score"),
            _get(after_json, "readiness_score"),
        )

    if action in APPROVAL_ACTIONS:
        return (
            _get(before_json, "approved_steps") or _get(before_json, "request", "approved_steps"),
            _get(after_json, "approved_steps") or _get(after_json, "request", "approved_steps"),
        )

    return None, None


def build_decision_gate_history_events(audit_logs) -> list[dict]:
    events = []

    for log in audit_logs:
        action = log.action
        before_json = log.before_json or {}
        after_json = log.after_json or {}
        status_from, status_to = _extract_status(action, before_json, after_json)
        score_from, score_to = _extract_score(action, before_json, after_json)

        if action in DECISION_ACTIONS:
            changed_fields = _changed_fields(
                before_json,
                after_json,
                [
                    "decision_status",
                    "recommendation",
                    "readiness_score",
                    "executive_summary",
                    "key_reasons",
                    "blockers",
                    "required_approvals",
                    "next_actions",
                    "owner",
                    "due_date",
                    "notes",
                ],
            )
            summary = _compact(_get(after_json, "recommendation") or log.notes or _event_title(action))
            details = {
                "recommendation": _get(after_json, "recommendation"),
                "readiness_score": _get(after_json, "readiness_score"),
                "blockers": _get(after_json, "blockers", default=[]),
                "required_approvals": _get(after_json, "required_approvals", default=[]),
                "next_actions": _get(after_json, "next_actions", default=[]),
            }
        elif action == "update_approval_step":
            before_step = _get(before_json, "step", default={})
            after_step = _get(after_json, "step", default={})
            changed_fields = _changed_fields(
                before_step,
                after_step,
                [
                    "status",
                    "approver_name",
                    "approver_email",
                    "due_date",
                    "decision_note",
                    "decided_by",
                    "decided_at",
                ],
            )
            summary = _compact(
                _get(after_json, "step", "decision_note")
                or f"{_get(after_json, 'step', 'role', default='Approval step')} moved to {status_to}"
            )
            details = {
                "role": _get(after_json, "step", "role"),
                "approver_name": _get(after_json, "step", "approver_name"),
                "decision_note": _get(after_json, "step", "decision_note"),
                "decided_by": _get(after_json, "step", "decided_by"),
                "decided_at": _get(after_json, "step", "decided_at"),
            }
        else:
            changed_fields = ["status"] if status_from != status_to else []
            summary = _compact(
                _get(after_json, "description")
                or _get(after_json, "request", "description")
                or log.notes
                or _event_title(action)
            )
            details = {
                "title": _get(after_json, "title") or _get(after_json, "request", "title"),
                "total_steps": _get(after_json, "total_steps") or _get(after_json, "request", "total_steps"),
                "approved_steps": _get(after_json, "approved_steps") or _get(after_json, "request", "approved_steps"),
                "submitted_by": _get(after_json, "submitted_by") or _get(after_json, "request", "submitted_by"),
            }

        events.append({
            "id": log.id,
            "project_id": log.project_id,
            "created_at": log.created_at,
            "actor": log.actor,
            "action": action,
            "event_type": _event_type(action),
            "title": _event_title(action),
            "summary": summary,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "status_from": status_from,
            "status_to": status_to,
            "score_from": score_from,
            "score_to": score_to,
            "target": _extract_actor_target(action, after_json),
            "changed_fields": changed_fields,
            "details": details,
            "before_json": before_json,
            "after_json": after_json,
            "notes": log.notes,
        })

    return events


def build_decision_gate_history_summary(
    *,
    events: list[dict],
    decision_gate=None,
    approval_request=None,
    approval_steps=None,
) -> dict:
    approval_steps = approval_steps or []

    decision_events = [event for event in events if event["event_type"] == "decision_gate"]
    approval_events = [event for event in events if event["event_type"] in {"approval_workflow", "approval_step"}]

    latest_decision_status = getattr(decision_gate, "decision_status", None)
    latest_recommendation = getattr(decision_gate, "recommendation", None)
    readiness_score = getattr(decision_gate, "readiness_score", None)

    latest_approval_status = getattr(approval_request, "status", None)
    approved_steps = len([step for step in approval_steps if step.status == "approved"])
    pending_steps = len([step for step in approval_steps if step.status == "pending"])
    rejected_steps = len([step for step in approval_steps if step.status == "rejected"])
    changes_requested_steps = len([step for step in approval_steps if step.status == "changes_requested"])

    last_event = events[0] if events else None

    return {
        "total_events": len(events),
        "decision_events": len(decision_events),
        "approval_events": len(approval_events),
        "latest_decision_status": latest_decision_status,
        "latest_recommendation": latest_recommendation,
        "readiness_score": readiness_score,
        "latest_approval_status": latest_approval_status,
        "approved_steps": approved_steps,
        "pending_steps": pending_steps,
        "rejected_steps": rejected_steps,
        "changes_requested_steps": changes_requested_steps,
        "last_event_at": last_event["created_at"] if last_event else None,
        "last_actor": last_event["actor"] if last_event else None,
    }
