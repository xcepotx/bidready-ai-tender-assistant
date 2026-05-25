def _is_id(output_language: str) -> bool:
    return output_language == "id"


def _text(output_language: str, en: str, id_text: str) -> str:
    return id_text if _is_id(output_language) else en


def _priority_rank(priority: str | None) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority or "medium", 1)


def _normalize_priority(value: str | None) -> str:
    if value in {"high", "medium", "low"}:
        return value
    return "medium"


def generate_action_item_payloads(
    *,
    requirements=None,
    clarifications=None,
    response_items=None,
    evidence_items=None,
    decision_gate=None,
    output_language: str = "en",
) -> list[dict]:
    requirements = requirements or []
    clarifications = clarifications or []
    response_items = response_items or []
    evidence_items = evidence_items or []

    payloads: list[dict] = []
    seen: set[tuple] = set()

    def add(payload: dict):
        key = (payload.get("source_type"), payload.get("source_id"), payload.get("title"))
        if key in seen:
            return
        seen.add(key)
        payloads.append(payload)

    # 1. High-risk / needs-review requirements
    for req in requirements:
        risk_level = getattr(req, "risk_level", None)
        status = getattr(req, "status", None)

        if risk_level == "high" or status in {"needs_review", "blocked", "needs_clarification"}:
            req_id = getattr(req, "id", None)
            category = getattr(req, "category", None) or "general"
            owner = getattr(req, "owner", None) or f"{category}_owner"

            add({
                "title": _text(
                    output_language,
                    "Review high-risk requirement",
                    "Review requirement berisiko tinggi",
                ),
                "description": _text(
                    output_language,
                    f"Review requirement #{req_id} and confirm compliance, risks, assumptions, and response strategy.",
                    f"Review requirement #{req_id} dan konfirmasi compliance, risiko, asumsi, serta strategi response.",
                ),
                "source_type": "requirement",
                "source_id": req_id,
                "related_requirement_ids": [req_id] if req_id else [],
                "related_response_item_ids": [],
                "related_clarification_ids": [],
                "related_evidence_item_ids": [],
                "related_proposal_section_ids": [],
                "owner": owner,
                "priority": "high" if risk_level == "high" or status == "blocked" else "medium",
                "status": "open",
                "due_date": None,
                "confidence": 0.75,
                "notes": _text(
                    output_language,
                    "Generated from requirement risk/status.",
                    "Dihasilkan dari risk/status requirement.",
                ),
                "generation_mode": "rules_only",
            })

    # 2. Open clarifications
    for q in clarifications:
        status = getattr(q, "status", None)
        if status and status not in {"open", "draft", "pending"}:
            continue

        q_id = getattr(q, "id", None)
        priority = _normalize_priority(getattr(q, "priority", None))
        owner = getattr(q, "owner", None) or "bid_manager"
        related_req_id = getattr(q, "requirement_id", None)

        add({
            "title": _text(
                output_language,
                "Resolve open clarification question",
                "Selesaikan clarification question yang masih open",
            ),
            "description": _text(
                output_language,
                f"Follow up clarification question #{q_id}, capture client answer, and update affected requirements or response plan.",
                f"Follow up clarification question #{q_id}, catat jawaban client, dan update requirement atau response plan yang terdampak.",
            ),
            "source_type": "clarification",
            "source_id": q_id,
            "related_requirement_ids": [related_req_id] if related_req_id else [],
            "related_response_item_ids": [],
            "related_clarification_ids": [q_id] if q_id else [],
            "related_evidence_item_ids": [],
            "related_proposal_section_ids": [],
            "owner": owner,
            "priority": priority,
            "status": "open",
            "due_date": None,
            "confidence": 0.76,
            "notes": _text(
                output_language,
                "Generated from open clarification question.",
                "Dihasilkan dari clarification question yang masih open.",
            ),
            "generation_mode": "rules_only",
        })

    # 3. Response plan review items
    for item in response_items:
        compliance_status = getattr(item, "compliance_status", None)
        status = getattr(item, "status", None)

        if compliance_status not in {"needs_review", "needs_clarification", "blocked", "non_compliant", "partially_compliant"} and status not in {"draft", "blocked"}:
            continue

        item_id = getattr(item, "id", None)
        owner = getattr(item, "owner", None) or "bid_manager"
        req_id = getattr(item, "requirement_id", None)

        add({
            "title": _text(
                output_language,
                "Review response plan item",
                "Review item response plan",
            ),
            "description": _text(
                output_language,
                f"Review response item #{item_id}, finalize response strategy, evidence, assumptions, and risks.",
                f"Review response item #{item_id}, finalisasi strategi response, evidence, asumsi, dan risiko.",
            ),
            "source_type": "response_plan",
            "source_id": item_id,
            "related_requirement_ids": [req_id] if req_id else [],
            "related_response_item_ids": [item_id] if item_id else [],
            "related_clarification_ids": [],
            "related_evidence_item_ids": [],
            "related_proposal_section_ids": [],
            "owner": owner,
            "priority": "high" if compliance_status in {"blocked", "non_compliant"} or status == "blocked" else "medium",
            "status": "open",
            "due_date": None,
            "confidence": 0.72,
            "notes": _text(
                output_language,
                "Generated from response plan status/compliance.",
                "Dihasilkan dari status/compliance response plan.",
            ),
            "generation_mode": "rules_only",
        })

    # 4. Evidence items
    for ev in evidence_items:
        status = getattr(ev, "status", None)
        if status not in {"open", "requested", "blocked"}:
            continue

        ev_id = getattr(ev, "id", None)
        ev_name = getattr(ev, "evidence_name", None) or f"Evidence #{ev_id}"
        owner = getattr(ev, "owner", None) or "bid_manager"
        priority = _normalize_priority(getattr(ev, "priority", None))

        add({
            "title": _text(
                output_language,
                f"Collect and validate evidence: {ev_name}",
                f"Kumpulkan dan validasi evidence: {ev_name}",
            ),
            "description": _text(
                output_language,
                f"Collect, validate, and attach evidence item '{ev_name}' before submission.",
                f"Kumpulkan, validasi, dan lampirkan evidence '{ev_name}' sebelum submission.",
            ),
            "source_type": "evidence_pack",
            "source_id": ev_id,
            "related_requirement_ids": getattr(ev, "related_requirement_ids", None) or [],
            "related_response_item_ids": getattr(ev, "related_response_item_ids", None) or [],
            "related_clarification_ids": [],
            "related_evidence_item_ids": [ev_id] if ev_id else [],
            "related_proposal_section_ids": getattr(ev, "related_proposal_section_ids", None) or [],
            "owner": owner,
            "priority": "high" if status == "blocked" else priority,
            "status": "open",
            "due_date": None,
            "confidence": 0.8,
            "notes": _text(
                output_language,
                "Generated from open/requested evidence item.",
                "Dihasilkan dari evidence item berstatus open/requested.",
            ),
            "generation_mode": "rules_only",
        })

    # 5. Decision Gate next actions
    if decision_gate:
        next_actions = getattr(decision_gate, "next_actions", None) or []
        due_date = getattr(decision_gate, "due_date", None)
        owner = getattr(decision_gate, "owner", None) or "bid_manager"
        gate_id = getattr(decision_gate, "id", None)

        for index, action in enumerate(next_actions, start=1):
            add({
                "title": action,
                "description": _text(
                    output_language,
                    f"Complete decision gate next action #{index}.",
                    f"Selesaikan tindak lanjut decision gate #{index}.",
                ),
                "source_type": "decision_gate",
                "source_id": gate_id,
                "related_requirement_ids": [],
                "related_response_item_ids": [],
                "related_clarification_ids": [],
                "related_evidence_item_ids": [],
                "related_proposal_section_ids": [],
                "owner": owner,
                "priority": "high",
                "status": "open",
                "due_date": due_date,
                "confidence": 0.78,
                "notes": _text(
                    output_language,
                    "Generated from decision gate next actions.",
                    "Dihasilkan dari tindak lanjut decision gate.",
                ),
                "generation_mode": "rules_only",
            })

    payloads.sort(key=lambda item: (_priority_rank(item.get("priority")), item.get("owner") or "", item.get("source_type") or ""))
    return payloads
