def _is_id(output_language: str) -> bool:
    return output_language == "id"


def _text(output_language: str, en: str, id_text: str) -> str:
    return id_text if _is_id(output_language) else en


def _level(value: str | None, default: str = "medium") -> str:
    if not value:
        return default

    value = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    mapped = {
        "critical": "high",
        "mandatory": "high",
        "must": "high",
        "required": "high",
        "blocked": "high",
        "p1": "high",
        "p2": "medium",
        "optional": "low",
        "p3": "low",
    }.get(value, value)

    return mapped if mapped in {"high", "medium", "low"} else default


def _status(requirement=None, response_item=None, clarification_open: bool = False) -> str:
    raw = (
        getattr(response_item, "compliance_status", None)
        or getattr(response_item, "status", None)
        or getattr(requirement, "status", None)
        or "needs_review"
    )
    raw = str(raw).strip().lower().replace("-", "_").replace(" ", "_")

    mapped = {
        "compliant": "compliant",
        "likely_compliant": "compliant",
        "accepted": "compliant",
        "done": "compliant",
        "complete": "compliant",
        "completed": "compliant",
        "partially_compliant": "partially_compliant",
        "partial": "partially_compliant",
        "needs_review": "needs_review",
        "review": "needs_review",
        "draft": "needs_review",
        "needs_clarification": "needs_clarification",
        "clarification": "needs_clarification",
        "blocked": "non_compliant",
        "non_compliant": "non_compliant",
        "not_started": "not_started",
        "open": "not_started",
    }.get(raw, "needs_review")

    if clarification_open and mapped in {"compliant", "partially_compliant", "needs_review"}:
        return "needs_clarification"

    if getattr(requirement, "status", None) == "blocked":
        return "non_compliant"

    return mapped


def _score(status: str, evidence_coverage: str, priority: str, risk_level: str) -> int:
    base = {
        "compliant": 100,
        "partially_compliant": 65,
        "needs_review": 50,
        "needs_clarification": 40,
        "not_started": 20,
        "non_compliant": 15,
    }.get(status, 50)

    if evidence_coverage == "missing":
        base -= 15
    elif evidence_coverage == "partial":
        base -= 7
    elif evidence_coverage == "covered":
        base += 3

    if priority == "high" and status != "compliant":
        base -= 5
    if risk_level == "high" and status != "compliant":
        base -= 8

    return max(0, min(100, int(round(base))))


def _weight(priority: str, risk_level: str) -> float:
    value = 1.0
    if priority == "high":
        value += 0.5
    if risk_level == "high":
        value += 0.5
    return value


def _owner(requirement=None, response_item=None) -> str:
    return (
        getattr(response_item, "owner", None)
        or getattr(requirement, "suggested_owner", None)
        or "bid_manager"
    )


def _gap(output_language: str, status: str, evidence_coverage: str, clarification_open: bool) -> str:
    parts = []

    if status == "compliant" and evidence_coverage == "covered":
        return _text(
            output_language,
            "Requirement is currently mapped as compliant with supporting evidence.",
            "Requirement saat ini dipetakan compliant dengan evidence pendukung.",
        )

    if status == "non_compliant":
        parts.append(_text(output_language, "Compliance gap remains unresolved.", "Gap compliance masih belum selesai."))
    elif status == "needs_clarification":
        parts.append(_text(output_language, "Client clarification is required before final compliance position.", "Clarification dari client dibutuhkan sebelum posisi compliance final."))
    elif status == "partially_compliant":
        parts.append(_text(output_language, "Response is partially compliant and needs strengthening.", "Response partially compliant dan perlu diperkuat."))
    elif status == "not_started":
        parts.append(_text(output_language, "Response is not mapped or not started yet.", "Response belum termapping atau belum dimulai."))
    else:
        parts.append(_text(output_language, "Owner review is required.", "Review owner dibutuhkan."))

    if evidence_coverage == "missing":
        parts.append(_text(output_language, "No linked evidence found.", "Belum ada evidence yang terhubung."))
    elif evidence_coverage == "partial":
        parts.append(_text(output_language, "Evidence coverage is partial.", "Coverage evidence masih parsial."))

    if clarification_open:
        parts.append(_text(output_language, "Open clarification may affect the final answer.", "Clarification terbuka dapat memengaruhi jawaban final."))

    return " ".join(parts)


def _action(output_language: str, status: str, evidence_coverage: str, owner: str) -> str:
    if status == "compliant" and evidence_coverage == "covered":
        return _text(
            output_language,
            "Keep evidence linked and validate response wording during final review.",
            "Pertahankan evidence terhubung dan validasi wording response saat final review.",
        )

    if status == "non_compliant":
        return _text(
            output_language,
            f"Escalate to {owner}, define exception or alternative response, and record approval rationale.",
            f"Escalate ke {owner}, tentukan exception atau response alternatif, dan catat rationale approval.",
        )

    if status == "needs_clarification":
        return _text(
            output_language,
            "Track clarification response, then update compliance status and response wording.",
            "Pantau jawaban clarification, lalu update status compliance dan wording response.",
        )

    if evidence_coverage == "missing":
        return _text(
            output_language,
            f"Assign {owner} to attach evidence and confirm compliance support.",
            f"Tugaskan {owner} untuk melampirkan evidence dan konfirmasi dukungan compliance.",
        )

    return _text(
        output_language,
        f"Assign {owner} to finalize response, evidence, and residual gap notes.",
        f"Tugaskan {owner} untuk finalisasi response, evidence, dan catatan gap residual.",
    )


def build_compliance_summary(items: list[dict]) -> dict:
    if not items:
        return {
            "total_items": 0,
            "weighted_score": 0.0,
            "score_percent": 0,
            "max_score": 0.0,
            "status_counts": {},
            "category_scores": [],
            "evidence_coverage_counts": {},
            "high_risk_gaps": 0,
            "recommendation": "Generate compliance matrix after extracting requirements.",
        }

    weighted_score = sum(item["score"] * item["weight"] for item in items)
    max_score = sum(item["max_score"] * item["weight"] for item in items) or 1.0
    score_percent = int(round((weighted_score / max_score) * 100))

    status_counts = {}
    evidence_counts = {}
    categories = {}
    high_risk_gaps = 0

    for item in items:
        status_counts[item["compliance_status"]] = status_counts.get(item["compliance_status"], 0) + 1
        evidence_counts[item["evidence_coverage"]] = evidence_counts.get(item["evidence_coverage"], 0) + 1

        category = item["category"] or "general"
        bucket = categories.setdefault(category, {"category": category, "items": 0, "weighted_score": 0.0, "max_score": 0.0})
        bucket["items"] += 1
        bucket["weighted_score"] += item["score"] * item["weight"]
        bucket["max_score"] += item["max_score"] * item["weight"]

        if item["risk_level"] == "high" and item["compliance_status"] != "compliant":
            high_risk_gaps += 1

    category_scores = []
    for bucket in categories.values():
        category_scores.append({
            "category": bucket["category"],
            "items": bucket["items"],
            "score_percent": int(round((bucket["weighted_score"] / (bucket["max_score"] or 1.0)) * 100)),
        })
    category_scores.sort(key=lambda row: row["score_percent"])

    if score_percent >= 85 and high_risk_gaps == 0:
        recommendation = "Compliance position is strong for final review."
    elif score_percent >= 65:
        recommendation = "Compliance position is workable but needs gap closure before approval."
    else:
        recommendation = "Compliance position requires focused remediation before submission."

    return {
        "total_items": len(items),
        "weighted_score": round(weighted_score, 2),
        "score_percent": score_percent,
        "max_score": round(max_score, 2),
        "status_counts": status_counts,
        "category_scores": category_scores,
        "evidence_coverage_counts": evidence_counts,
        "high_risk_gaps": high_risk_gaps,
        "recommendation": recommendation,
    }


def generate_compliance_item_payloads(
    *,
    requirements=None,
    response_items=None,
    evidence_items=None,
    clarifications=None,
    output_language: str = "en",
) -> list[dict]:
    requirements = requirements or []
    response_items = response_items or []
    evidence_items = evidence_items or []
    clarifications = clarifications or []

    response_by_req = {}
    for item in response_items:
        req_id = getattr(item, "requirement_id", None)
        if req_id and req_id not in response_by_req:
            response_by_req[req_id] = item

    evidence_by_req = {}
    evidence_by_response = {}

    for ev in evidence_items:
        for req_id in getattr(ev, "related_requirement_ids", None) or []:
            evidence_by_req.setdefault(req_id, []).append(ev)

        for response_id in getattr(ev, "related_response_item_ids", None) or []:
            evidence_by_response.setdefault(response_id, []).append(ev)

    open_clarification_req_ids = {
        getattr(q, "requirement_id", None)
        for q in clarifications
        if getattr(q, "requirement_id", None)
        and getattr(q, "status", None) in {"open", "draft", "pending", "blocked"}
    }

    payloads = []

    for req in requirements:
        req_id = getattr(req, "id", None)
        response_item = response_by_req.get(req_id)
        response_id = getattr(response_item, "id", None) if response_item else None

        linked_evidence = list(evidence_by_req.get(req_id, []))
        if response_id:
            linked_evidence.extend(evidence_by_response.get(response_id, []))

        evidence_ids = sorted({
            getattr(ev, "id", None)
            for ev in linked_evidence
            if getattr(ev, "id", None)
        })

        evidence_coverage = "missing"
        if evidence_ids:
            blocked = any(getattr(ev, "status", None) == "blocked" for ev in linked_evidence)
            evidence_coverage = "partial" if blocked or len(evidence_ids) == 1 else "covered"

        priority = _level(getattr(req, "priority", None))
        risk_level = _level(getattr(req, "risk_level", None))
        clarification_open = req_id in open_clarification_req_ids
        status = _status(req, response_item, clarification_open)
        owner = _owner(req, response_item)
        score = _score(status, evidence_coverage, priority, risk_level)

        payloads.append({
            "requirement_id": req_id,
            "response_item_id": response_id,
            "category": getattr(req, "category", None) or getattr(response_item, "category", None) if response_item else getattr(req, "category", None) or "general",
            "requirement_text": getattr(req, "requirement_text", None) or getattr(response_item, "requirement_text", None) if response_item else getattr(req, "requirement_text", None) or "",
            "compliance_status": status,
            "score": score,
            "max_score": 100,
            "weight": _weight(priority, risk_level),
            "owner": owner,
            "priority": priority,
            "risk_level": risk_level,
            "evidence_item_ids": evidence_ids,
            "evidence_coverage": evidence_coverage,
            "gap_summary": _gap(output_language, status, evidence_coverage, clarification_open),
            "recommended_action": _action(output_language, status, evidence_coverage, owner),
            "notes": _text(
                output_language,
                "Generated from requirement, response plan, evidence pack, and clarification status.",
                "Dihasilkan dari requirement, response plan, evidence pack, dan status clarification.",
            ),
            "source_page": getattr(req, "source_page", None),
            "confidence": getattr(req, "confidence", None) or getattr(response_item, "confidence", None) if response_item else getattr(req, "confidence", None) or 0.60,
            "generation_mode": "rules_only",
        })

    for item in response_items:
        if getattr(item, "requirement_id", None):
            continue

        item_id = getattr(item, "id", None)
        evidence_ids = sorted({
            getattr(ev, "id", None)
            for ev in evidence_by_response.get(item_id, [])
            if getattr(ev, "id", None)
        })

        evidence_coverage = "partial" if evidence_ids else "missing"
        status = _status(None, item, False)
        owner = getattr(item, "owner", None) or "bid_manager"
        score = _score(status, evidence_coverage, "medium", "medium")

        payloads.append({
            "requirement_id": None,
            "response_item_id": item_id,
            "category": getattr(item, "category", None) or "response",
            "requirement_text": getattr(item, "requirement_text", None) or f"Response item #{item_id}",
            "compliance_status": status,
            "score": score,
            "max_score": 100,
            "weight": 1.0,
            "owner": owner,
            "priority": "medium",
            "risk_level": "medium",
            "evidence_item_ids": evidence_ids,
            "evidence_coverage": evidence_coverage,
            "gap_summary": _gap(output_language, status, evidence_coverage, False),
            "recommended_action": _action(output_language, status, evidence_coverage, owner),
            "notes": _text(
                output_language,
                "Generated from response plan item without requirement mapping.",
                "Dihasilkan dari response plan item tanpa mapping requirement.",
            ),
            "source_page": getattr(item, "source_page", None),
            "confidence": getattr(item, "confidence", None) or 0.60,
            "generation_mode": "rules_only",
        })

    payloads.sort(key=lambda item: (item["score"], item["risk_level"] != "high", item["category"], item["requirement_id"] or 0))
    return payloads
