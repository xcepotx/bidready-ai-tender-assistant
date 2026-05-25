import re


def _clean(value: str | None) -> str | None:
    if not value:
        return None

    value = re.sub(r"\s+", " ", value).strip()
    value = value.strip(":-–— ")
    return value or None


def _first_match(patterns: list[str], lines: list[dict]) -> tuple[str | None, dict | None]:
    for item in lines:
        line = item["text"]
        for pattern in patterns:
            match = re.search(pattern, line, flags=re.IGNORECASE)
            if match:
                value = _clean(match.group(1) if match.groups() else line)
                return value, {
                    "page": item["page_number"],
                    "text": line,
                    "pattern": pattern,
                }

    return None, None


def _infer_service_domain(text: str, project_domain: str | None = None) -> str | None:
    if project_domain:
        return project_domain

    lower = text.lower()
    domains = []

    if any(k in lower for k in ["managed service", "sla", "support", "24x7", "24/7", "incident"]):
        domains.append("Managed Services")

    if any(k in lower for k in ["cloud", "infrastructure", "server", "data center", "backup", "disaster recovery"]):
        domains.append("Cloud / Infrastructure")

    if any(k in lower for k in ["application", "aplikasi", "software", "maintenance aplikasi", "development"]):
        domains.append("Application Services")

    if any(k in lower for k in ["security", "cybersecurity", "iso 27001", "compliance", "audit", "vulnerability"]):
        domains.append("Cybersecurity / Compliance")

    if any(k in lower for k in ["data", "analytics", "artificial intelligence", "machine learning", "dashboard"]):
        domains.append("Data / AI")

    if not domains:
        return None

    return " / ".join(dict.fromkeys(domains))


def _extract_submission_requirements(lines: list[dict]) -> tuple[list[str], list[dict]]:
    results = []
    evidence = []
    seen = set()

    explicit_keywords = [
        "nib",
        "npwp",
        "surat penawaran",
        "bermeterai",
        "meterai",
        "proposal",
        "executive summary",
        "commercial proposal",
        "technical proposal",
        "cv",
        "certification",
        "sertifikat",
    ]

    for item in lines:
        line = item["text"]
        lower = line.lower()

        is_submission_line = (
            "melampirkan" in lower
            or "proposal must include" in lower
            or "must include" in lower
            or "wajib melampirkan" in lower
            or "required document" in lower
            or any(keyword in lower for keyword in explicit_keywords)
        )

        if not is_submission_line:
            continue

        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        cleaned = re.sub(r"^peserta\s+wajib\s+melampirkan\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^vendor\s+must\s+provide\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^proposal\s+must\s+include\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip(" .")

        if len(cleaned) < 2:
            continue

        key = cleaned.lower()
        if key in seen:
            continue

        seen.add(key)
        results.append(cleaned)
        evidence.append({
            "page": item["page_number"],
            "text": line,
        })

    return results, evidence


def extract_project_metadata_from_pages(pages: list[dict], project=None) -> dict:
    lines = []

    for page in pages:
        page_number = page.get("page_number")
        text = page.get("text") or ""

        for raw_line in text.splitlines():
            line = _clean(raw_line)
            if not line:
                continue

            lines.append({
                "page_number": page_number,
                "text": line,
            })

    all_text = "\n".join(item["text"] for item in lines)

    package_name, package_evidence = _first_match(
        [
            r"(?:Nama Paket|Package Name|RFP Title|Judul Paket)\s*[:\-]\s*(.+)",
            r"(?:Paket)\s*[:\-]\s*(.+)",
        ],
        lines,
    )

    issuer, issuer_evidence = _first_match(
        [
            r"(?:Instansi|Client|Issuer|Pemilik Pekerjaan|Company)\s*[:\-]\s*(.+)",
            r"(?:Diterbitkan oleh|Issued by)\s*[:\-]\s*(.+)",
        ],
        lines,
    )

    submission_deadline, submission_deadline_evidence = _first_match(
        [
            r"(?:Batas Akhir Pemasukan Penawaran|Submission Deadline|Proposal Submission Deadline|Batas Akhir)\s*[:\-]\s*(.+)",
            r"(?:submit.*by|submitted by)\s*[:\-]?\s*(.+)",
        ],
        lines,
    )

    clarification_deadline, clarification_deadline_evidence = _first_match(
        [
            r"(?:Clarification Deadline|Batas Akhir Klarifikasi|Batas Klarifikasi|Aanwijzing)\s*[:\-]\s*(.+)",
        ],
        lines,
    )

    proposal_validity, proposal_validity_evidence = _first_match(
        [
            r"(?:Masa berlaku penawaran)\s*(?:minimal|:|\-)?\s*(.+)",
            r"(?:Proposal validity|Validity period)\s*[:\-]\s*(.+)",
        ],
        lines,
    )

    submission_requirements, submission_requirements_evidence = _extract_submission_requirements(lines)

    service_domain = _infer_service_domain(
        all_text,
        getattr(project, "tender_type", None) if project else None,
    )

    source_evidence = {
        "package_name": package_evidence,
        "issuer": issuer_evidence,
        "submission_deadline": submission_deadline_evidence,
        "clarification_deadline": clarification_deadline_evidence,
        "proposal_validity": proposal_validity_evidence,
        "submission_requirements": submission_requirements_evidence,
    }

    return {
        "package_name": package_name or getattr(project, "title", None),
        "issuer": issuer or getattr(project, "issuer", None),
        "submission_deadline": submission_deadline,
        "clarification_deadline": clarification_deadline,
        "proposal_validity": proposal_validity,
        "service_domain": service_domain,
        "submission_requirements": submission_requirements,
        "source_evidence": source_evidence,
        "extraction_mode": "rules_only",
        "notes": "Extracted by rule-based metadata extractor v1",
    }
