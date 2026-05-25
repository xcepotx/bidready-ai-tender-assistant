import re


SECTION_CATEGORY_PATTERNS = [
    ("submission", [
        "submission", "submit", "proposal submission", "pemasukan penawaran",
        "dokumen penawaran", "format penawaran", "instruksi kepada peserta",
        "surat penawaran", "bermeterai", "unggah dokumen", "upload dokumen",
    ]),
    ("timeline", [
        "deadline", "batas akhir", "jadwal", "schedule", "timeline",
        "pukul", "tanggal", "clarification deadline", "aanwijzing",
    ]),
    ("scope", [
        "scope of work", "scope", "ruang lingkup", "kak", "tor",
        "term of reference", "statement of work", "sow", "syarat teknis", "teknis",
    ]),
    ("application_services", [
        "application", "aplikasi", "software", "development", "maintenance aplikasi",
        "application services", "modernization", "migration aplikasi",
    ]),
    ("cloud_infrastructure", [
        "cloud", "infrastructure", "server", "hosting", "data center",
        "availability zone", "backup", "disaster recovery", "dr", "environment",
    ]),
    ("data_ai", [
        "data", "analytics", "artificial intelligence", "machine learning",
        "genai", "generative ai", "model", "dashboard", "reporting", "etl",
    ]),
    ("cybersecurity_compliance", [
        "security", "cybersecurity", "iso 27001", "compliance", "privacy",
        "data protection", "encryption", "vulnerability", "penetration test",
        "pentest", "audit", "risk management", "data residency",
    ]),
    ("managed_services_sla", [
        "managed service", "sla", "service level", "support", "24x7", "24/7",
        "incident", "problem management", "change management", "l1", "l2", "l3",
    ]),
    ("integration", [
        "integration", "integrasi", "api", "interface", "middleware",
        "sap", "oracle", "erp", "crm", "sso", "identity",
    ]),
    ("delivery_transition", [
        "transition", "transisi", "implementation", "implementasi",
        "deployment", "rollout", "handover", "knowledge transfer", "training",
        "migration plan", "project plan", "metode pelaksanaan",
        "pelaksanaan pekerjaan", "rencana pelaksanaan", "delivery plan",
    ]),
    ("staffing_certification", [
        "cv", "personnel", "resource", "staff", "team member",
        "certified", "certification", "sertifikat", "bersertifikat",
        "tenaga ahli", "engineer", "architect",
    ]),
    ("commercial_pricing", [
        "price", "pricing", "commercial", "komersial", "harga", "harga penawaran",
        "biaya", "payment", "invoice", "milestone", "fixed price",
        "time and material", "t&m", "tax", "pajak", "hps", "rab", "boq",
        "masa berlaku penawaran", "penawaran harga",
    ]),
    ("legal_contractual", [
        "contract", "legal", "liability", "penalty", "denda", "termination",
        "warranty", "intellectual property", "ip rights", "confidentiality",
        "nda", "terms and conditions", "jaminan",
    ]),
]


REQUIREMENT_SIGNALS = [
    "must",
    "shall",
    "required",
    "mandatory",
    "should",
    "need to",
    "expected to",
    "wajib",
    "harus",
    "minimal",
    "melampirkan",
    "menyampaikan",
    "menyediakan",
    "memiliki",
    "termasuk",
    "masa berlaku",
    "batas akhir",
    "pukul",
    "submit",
    "proposal must",
    "vendor must",
    "bidder must",
    "penyedia wajib",
    "peserta wajib",
]


HIGH_RISK_KEYWORDS = [
    "mandatory",
    "wajib",
    "harus",
    "shall",
    "must",
    "penalty",
    "denda",
    "liability",
    "security",
    "cybersecurity",
    "iso 27001",
    "data residency",
    "personal data",
    "privacy",
    "24x7",
    "24/7",
    "sla",
    "jaminan",
    "bermeterai",
    "certified",
    "bersertifikat",
    "deadline",
    "batas akhir",
    "legal",
    "compliance",
]


MEDIUM_RISK_KEYWORDS = [
    "should",
    "expected",
    "melampirkan",
    "menyampaikan",
    "menyediakan",
    "memiliki",
    "minimal",
    "masa berlaku",
    "termasuk pajak",
    "integration",
    "support",
    "migration",
    "training",
    "handover",
]


OWNER_BY_CATEGORY = {
    "submission": "bid_manager",
    "timeline": "bid_manager",
    "scope": "solution_architect",
    "application_services": "application_services_team",
    "cloud_infrastructure": "cloud_infrastructure_team",
    "data_ai": "data_ai_team",
    "cybersecurity_compliance": "security_compliance_team",
    "managed_services_sla": "managed_services_team",
    "integration": "solution_architect",
    "delivery_transition": "delivery_manager",
    "staffing_certification": "resource_manager",
    "commercial_pricing": "commercial_team",
    "legal_contractual": "legal_team",
    "clarification_needed": "bid_manager",
    "general": "bid_manager",
}


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def clean_requirement_line(line: str) -> str:
    line = normalize_line(line)
    line = re.sub(r"^\d+[\.\)]\s*", "", line)
    line = re.sub(r"^[a-zA-Z][\.\)]\s*", "", line)
    line = re.sub(r"^[\-•]\s*", "", line)
    return line.strip()


def _pattern_matches(lower_text: str, pattern: str) -> bool:
    pattern = pattern.lower().strip()

    # Avoid false positives for short terms such as "ai" inside Indonesian words
    # like "menyampaikan" or "bermeterai".
    if len(pattern) <= 3:
        return re.search(rf"\\b{re.escape(pattern)}\\b", lower_text) is not None

    return pattern in lower_text


def detect_category(text: str, current_category: str | None = None) -> str:
    lower = text.lower()

    for category, patterns in SECTION_CATEGORY_PATTERNS:
        if any(_pattern_matches(lower, pattern) for pattern in patterns):
            return category

    if "clarify" in lower or "unclear" in lower or "not specified" in lower:
        return "clarification_needed"

    return current_category or "general"


def detect_section_header(line: str) -> bool:
    lower = line.lower().strip()

    if lower.endswith(":"):
        return True

    section_words = [
        "syarat",
        "scope",
        "ruang lingkup",
        "timeline",
        "jadwal",
        "commercial",
        "pricing",
        "security",
        "sla",
        "submission",
        "legal",
        "technical",
        "teknis",
    ]

    return len(line) <= 80 and any(word in lower for word in section_words)


def detect_risk(text: str) -> str:
    lower = text.lower()

    if any(keyword in lower for keyword in HIGH_RISK_KEYWORDS):
        return "high"

    if any(keyword in lower for keyword in MEDIUM_RISK_KEYWORDS):
        return "medium"

    return "low"


def detect_priority(text: str) -> str:
    lower = text.lower()

    mandatory_markers = [
        "must",
        "shall",
        "mandatory",
        "required",
        "wajib",
        "harus",
        "peserta wajib",
        "penyedia wajib",
        "bidder must",
        "vendor must",
    ]

    optional_markers = [
        "should",
        "may",
        "optional",
        "prefer",
        "diutamakan",
        "sebaiknya",
    ]

    if any(marker in lower for marker in mandatory_markers):
        return "mandatory"

    if any(marker in lower for marker in optional_markers):
        return "optional"

    return "needs_review"


def detect_owner(category: str) -> str:
    return OWNER_BY_CATEGORY.get(category, "bid_manager")


def is_requirement_line(line: str) -> bool:
    raw = normalize_line(line)
    clean = clean_requirement_line(raw)
    lower = clean.lower()

    if len(clean) < 12:
        return False

    if detect_section_header(clean):
        return False

    numbered = re.match(r"^\d+[\.\)]\s+", raw) is not None
    bullet = re.match(r"^[\-•]\s+", raw) is not None
    has_signal = any(signal in lower for signal in REQUIREMENT_SIGNALS)

    return numbered or bullet or has_signal


def requirement_notes(category: str, text: str) -> str:
    lower = text.lower()
    notes = ["Extracted by enterprise rule-based RFP extractor"]

    if category == "cybersecurity_compliance":
        notes.append("Security/compliance review recommended")

    if category == "legal_contractual":
        notes.append("Legal review recommended")

    if category == "commercial_pricing":
        notes.append("Commercial/pricing review recommended")

    if category == "managed_services_sla":
        notes.append("Validate SLA, support hours, and delivery capability")

    if "clarify" in lower or "unclear" in lower:
        notes.append("Potential clarification question")

    return " | ".join(notes)


def extract_requirements_from_pages(pages: list[dict]) -> list[dict]:
    results: list[dict] = []
    current_category: str | None = None
    seen: set[str] = set()

    for page in pages:
        page_number = page["page_number"]
        text = page.get("text") or ""

        for raw_line in text.splitlines():
            line = normalize_line(raw_line)
            if not line:
                continue

            if detect_section_header(line):
                current_category = detect_category(line, current_category)
                continue

            if not is_requirement_line(line):
                continue

            requirement_text = clean_requirement_line(line)
            if not requirement_text:
                continue

            dedupe_key = requirement_text.lower()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            category = detect_category(requirement_text, current_category)

            results.append(
                {
                    "category": category,
                    "requirement_text": requirement_text,
                    "priority": detect_priority(requirement_text),
                    "risk_level": detect_risk(requirement_text),
                    "source_page": page_number,
                    "evidence_quote": line[:500],
                    "confidence": 0.72,
                    "suggested_owner": detect_owner(category),
                    "status": "needs_review",
                    "notes": requirement_notes(category, requirement_text),
                }
            )

    return results
