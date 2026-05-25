def _is_id(output_language: str) -> bool:
    return output_language == "id"


def _text(output_language: str, en: str, id_text: str) -> str:
    return id_text if _is_id(output_language) else en


def _normalize_level(value: str | None, default: str = "medium") -> str:
    if not value:
        return default

    normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "critical": "high",
        "urgent": "high",
        "p1": "high",
        "p2": "medium",
        "p3": "low",
        "needs_review": "medium",
        "blocked": "high",
        "non_compliant": "high",
        "partially_compliant": "medium",
        "compliant": "low",
        "accepted": "low",
    }
    normalized = mapping.get(normalized, normalized)

    if normalized in {"high", "medium", "low"}:
        return normalized
    return default


def _severity(probability: str | None, impact: str | None) -> str:
    p = _normalize_level(probability)
    i = _normalize_level(impact)

    if p == "high" and i == "high":
        return "critical"
    if p == "high" or i == "high":
        return "high"
    if p == "low" and i == "low":
        return "low"
    return "medium"


def _severity_rank(value: str | None) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(value or "medium", 2)


def _owner(obj, fallback: str = "bid_manager") -> str:
    return (
        getattr(obj, "owner", None)
        or getattr(obj, "suggested_owner", None)
        or fallback
    )


def _short_text(value, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item) for item in value if item) or fallback
    return str(value) or fallback


def generate_risk_item_payloads(
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
        probability = _normalize_level(payload.get("probability"))
        impact = _normalize_level(payload.get("impact"))
        payload["probability"] = probability
        payload["impact"] = impact
        payload["severity"] = payload.get("severity") or _severity(probability, impact)

        key = (
            payload.get("source_type"),
            payload.get("source_id"),
            payload.get("title"),
            payload.get("risk_category"),
        )
        if key in seen:
            return
        seen.add(key)
        payloads.append(payload)

    # 1. Requirement risks
    for req in requirements:
        req_id = getattr(req, "id", None)
        risk_level = _normalize_level(getattr(req, "risk_level", None))
        priority = _normalize_level(getattr(req, "priority", None))
        status = getattr(req, "status", None)
        category = getattr(req, "category", None) or "general"

        if risk_level == "low" and priority == "low" and status not in {"blocked", "needs_review", "needs_clarification"}:
            continue

        impact = "high" if priority == "high" or status == "blocked" else "medium"
        title = _text(
            output_language,
            f"Requirement risk: {category}",
            f"Risiko requirement: {category}",
        )

        add({
            "title": title,
            "description": _short_text(
                getattr(req, "requirement_text", None),
                _text(output_language, "Requirement needs risk review.", "Requirement perlu review risiko."),
            ),
            "source_type": "requirement",
            "source_id": req_id,
            "related_requirement_ids": [req_id] if req_id else [],
            "related_response_item_ids": [],
            "related_clarification_ids": [],
            "related_evidence_item_ids": [],
            "risk_category": category,
            "impact_area": "compliance",
            "probability": risk_level,
            "impact": impact,
            "owner": _owner(req, f"{category}_owner"),
            "status": "open" if status != "blocked" else "escalated",
            "due_date": None,
            "mitigation_plan": _text(
                output_language,
                "Review compliance evidence, response wording, assumptions, and owner accountability before submission.",
                "Review evidence compliance, wording response, asumsi, dan owner sebelum submission.",
            ),
            "contingency_plan": _text(
                output_language,
                "Escalate to solution/commercial owner if the requirement cannot be fully met.",
                "Escalate ke owner solusi/komersial jika requirement tidak bisa dipenuhi penuh.",
            ),
            "trigger_event": _text(
                output_language,
                "Requirement remains high risk, blocked, or unresolved near submission deadline.",
                "Requirement tetap high risk, blocked, atau belum terselesaikan mendekati deadline submission.",
            ),
            "confidence": getattr(req, "confidence", None) or 0.72,
            "notes": _text(
                output_language,
                "Generated from requirement priority/risk/status.",
                "Dihasilkan dari priority/risk/status requirement.",
            ),
            "generation_mode": "rules_only",
        })

    # 2. Clarification risks
    for q in clarifications:
        q_id = getattr(q, "id", None)
        status = getattr(q, "status", None) or "open"
        priority = _normalize_level(getattr(q, "priority", None))
        risk_level = _normalize_level(getattr(q, "risk_level", None))
        related_req_id = getattr(q, "requirement_id", None)

        if status not in {"open", "draft", "pending", "blocked"} and priority != "high" and risk_level != "high":
            continue

        add({
            "title": _text(
                output_language,
                "Open clarification may change bid response",
                "Clarification terbuka dapat mengubah response tender",
            ),
            "description": _short_text(
                getattr(q, "question_text", None),
                _text(output_language, "Clarification answer is still pending.", "Jawaban clarification masih pending."),
            ),
            "source_type": "clarification",
            "source_id": q_id,
            "related_requirement_ids": [related_req_id] if related_req_id else [],
            "related_response_item_ids": [],
            "related_clarification_ids": [q_id] if q_id else [],
            "related_evidence_item_ids": [],
            "risk_category": "clarification",
            "impact_area": "scope",
            "probability": risk_level,
            "impact": "high" if priority == "high" else "medium",
            "owner": _owner(q),
            "status": "open",
            "due_date": None,
            "mitigation_plan": _text(
                output_language,
                "Track client response, update affected requirements, and revise response plan immediately after answer is received.",
                "Pantau jawaban client, update requirement terdampak, dan revisi response plan segera setelah jawaban diterima.",
            ),
            "contingency_plan": _text(
                output_language,
                "Document assumptions and exclusions if clarification response is not received before submission.",
                "Dokumentasikan asumsi dan exclusion jika jawaban clarification tidak diterima sebelum submission.",
            ),
            "trigger_event": _text(
                output_language,
                "Clarification remains unanswered or changes scope/compliance position.",
                "Clarification belum terjawab atau mengubah scope/posisi compliance.",
            ),
            "confidence": 0.76,
            "notes": _text(
                output_language,
                "Generated from open clarification item.",
                "Dihasilkan dari clarification item yang masih open.",
            ),
            "generation_mode": "rules_only",
        })

    # 3. Response plan risks and assumptions
    for item in response_items:
        item_id = getattr(item, "id", None)
        req_id = getattr(item, "requirement_id", None)
        compliance_status = getattr(item, "compliance_status", None)
        status = getattr(item, "status", None)
        risks = getattr(item, "risks", None) or []

        risk_entries = risks if isinstance(risks, list) and risks else []
        if not risk_entries and compliance_status in {"blocked", "non_compliant", "partially_compliant", "needs_clarification", "needs_review"}:
            risk_entries = [
                _text(
                    output_language,
                    f"Response item has compliance status: {compliance_status}.",
                    f"Response item memiliki status compliance: {compliance_status}.",
                )
            ]

        for index, risk_text in enumerate(risk_entries[:3], start=1):
            probability = _normalize_level(compliance_status)
            impact = "high" if compliance_status in {"blocked", "non_compliant"} or status == "blocked" else "medium"

            add({
                "title": _text(
                    output_language,
                    f"Response plan risk #{index}",
                    f"Risiko response plan #{index}",
                ),
                "description": _short_text(risk_text),
                "source_type": "response_plan",
                "source_id": item_id,
                "related_requirement_ids": [req_id] if req_id else [],
                "related_response_item_ids": [item_id] if item_id else [],
                "related_clarification_ids": [],
                "related_evidence_item_ids": [],
                "risk_category": getattr(item, "category", None) or "response",
                "impact_area": "proposal",
                "probability": probability,
                "impact": impact,
                "owner": _owner(item),
                "status": "open" if status != "blocked" else "escalated",
                "due_date": None,
                "mitigation_plan": _text(
                    output_language,
                    "Finalize response strategy, validate assumptions, and attach supporting evidence.",
                    "Finalisasi strategi response, validasi asumsi, dan lampirkan evidence pendukung.",
                ),
                "contingency_plan": _text(
                    output_language,
                    "Escalate unresolved compliance gaps to bid lead before final approval.",
                    "Escalate gap compliance yang belum selesai ke bid lead sebelum final approval.",
                ),
                "trigger_event": _text(
                    output_language,
                    "Response remains blocked, partially compliant, or unsupported by evidence.",
                    "Response tetap blocked, partially compliant, atau belum didukung evidence.",
                ),
                "confidence": getattr(item, "confidence", None) or 0.70,
                "notes": _text(
                    output_language,
                    "Generated from response plan risks/compliance.",
                    "Dihasilkan dari risks/compliance response plan.",
                ),
                "generation_mode": "rules_only",
            })

    # 4. Evidence risks
    for ev in evidence_items:
        ev_id = getattr(ev, "id", None)
        status = getattr(ev, "status", None)
        priority = _normalize_level(getattr(ev, "priority", None))
        ev_name = getattr(ev, "evidence_name", None) or f"Evidence #{ev_id}"

        if status not in {"open", "requested", "blocked"} and priority != "high":
            continue

        add({
            "title": _text(
                output_language,
                f"Evidence risk: {ev_name}",
                f"Risiko evidence: {ev_name}",
            ),
            "description": _text(
                output_language,
                f"Evidence item '{ev_name}' may not be ready or validated before submission.",
                f"Evidence '{ev_name}' berisiko belum siap atau belum tervalidasi sebelum submission.",
            ),
            "source_type": "evidence_pack",
            "source_id": ev_id,
            "related_requirement_ids": getattr(ev, "related_requirement_ids", None) or [],
            "related_response_item_ids": getattr(ev, "related_response_item_ids", None) or [],
            "related_clarification_ids": [],
            "related_evidence_item_ids": [ev_id] if ev_id else [],
            "risk_category": getattr(ev, "evidence_category", None) or "evidence",
            "impact_area": "evidence",
            "probability": "high" if status == "blocked" else priority,
            "impact": "high" if priority == "high" or status == "blocked" else "medium",
            "owner": _owner(ev),
            "status": "open" if status != "blocked" else "escalated",
            "due_date": None,
            "mitigation_plan": _text(
                output_language,
                "Collect, validate, and attach evidence; confirm fallback evidence if the primary document is unavailable.",
                "Kumpulkan, validasi, dan lampirkan evidence; konfirmasi fallback evidence jika dokumen utama tidak tersedia.",
            ),
            "contingency_plan": _text(
                output_language,
                "Use approved alternative evidence or document an assumption/exclusion.",
                "Gunakan evidence alternatif yang disetujui atau dokumentasikan asumsi/exclusion.",
            ),
            "trigger_event": _text(
                output_language,
                "Evidence remains requested/open/blocked near submission.",
                "Evidence tetap requested/open/blocked mendekati submission.",
            ),
            "confidence": 0.78,
            "notes": _text(
                output_language,
                "Generated from evidence pack status/priority.",
                "Dihasilkan dari status/priority evidence pack.",
            ),
            "generation_mode": "rules_only",
        })

    # 5. Decision gate blockers
    if decision_gate:
        gate_id = getattr(decision_gate, "id", None)
        blockers = getattr(decision_gate, "blockers", None) or []
        approvals = getattr(decision_gate, "required_approvals", None) or []
        due_date = getattr(decision_gate, "due_date", None)

        for index, blocker in enumerate(blockers[:5], start=1):
            add({
                "title": _text(
                    output_language,
                    f"Executive blocker risk #{index}",
                    f"Risiko blocker eksekutif #{index}",
                ),
                "description": _short_text(blocker),
                "source_type": "decision_gate",
                "source_id": gate_id,
                "related_requirement_ids": [],
                "related_response_item_ids": [],
                "related_clarification_ids": [],
                "related_evidence_item_ids": [],
                "risk_category": "executive",
                "impact_area": "approval",
                "probability": "high",
                "impact": "high",
                "severity": "critical",
                "owner": getattr(decision_gate, "owner", None) or "bid_manager",
                "status": "escalated",
                "due_date": due_date,
                "mitigation_plan": _text(
                    output_language,
                    "Resolve blocker and secure required approval before final submission.",
                    "Selesaikan blocker dan amankan approval yang dibutuhkan sebelum final submission.",
                ),
                "contingency_plan": _text(
                    output_language,
                    "Escalate to executive sponsor and record go/no-go decision rationale.",
                    "Escalate ke executive sponsor dan catat rationale keputusan go/no-go.",
                ),
                "trigger_event": _text(
                    output_language,
                    "Blocker remains unresolved at decision gate.",
                    "Blocker masih belum selesai pada decision gate.",
                ),
                "confidence": getattr(decision_gate, "confidence", None) or 0.82,
                "notes": _text(
                    output_language,
                    "Generated from decision gate blockers.",
                    "Dihasilkan dari blocker decision gate.",
                ),
                "generation_mode": "rules_only",
            })

        if approvals:
            add({
                "title": _text(
                    output_language,
                    "Approval dependency risk",
                    "Risiko dependency approval",
                ),
                "description": _text(
                    output_language,
                    "Required approvals may delay proposal readiness or submission sign-off.",
                    "Approval yang dibutuhkan dapat menunda readiness proposal atau sign-off submission.",
                ),
                "source_type": "decision_gate",
                "source_id": gate_id,
                "related_requirement_ids": [],
                "related_response_item_ids": [],
                "related_clarification_ids": [],
                "related_evidence_item_ids": [],
                "risk_category": "approval",
                "impact_area": "approval",
                "probability": "medium",
                "impact": "high",
                "owner": getattr(decision_gate, "owner", None) or "bid_manager",
                "status": "open",
                "due_date": due_date,
                "mitigation_plan": _text(
                    output_language,
                    "Confirm approval owners, approval sequence, and due dates.",
                    "Konfirmasi owner approval, urutan approval, dan due date.",
                ),
                "contingency_plan": _text(
                    output_language,
                    "Escalate delayed approval to bid sponsor.",
                    "Escalate approval yang terlambat ke bid sponsor.",
                ),
                "trigger_event": _text(
                    output_language,
                    "Approval remains pending close to submission.",
                    "Approval masih pending mendekati submission.",
                ),
                "confidence": 0.74,
                "notes": _text(
                    output_language,
                    "Generated from decision gate required approvals.",
                    "Dihasilkan dari required approvals decision gate.",
                ),
                "generation_mode": "rules_only",
            })

    payloads.sort(
        key=lambda item: (
            _severity_rank(item.get("severity")),
            item.get("owner") or "",
            item.get("source_type") or "",
            item.get("source_id") or 0,
        )
    )
    return payloads
