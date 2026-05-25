import os


class AiGatewayConfig:
    def __init__(self):
        self.mode = os.getenv("AI_MODE", "rules_only")
        self.provider = os.getenv("AI_PROVIDER", "none")
        self.model = os.getenv("AI_MODEL", "none")

    @property
    def external_call_enabled(self) -> bool:
        return self.mode in {"approved_enterprise_llm", "local_llm"} and self.provider != "none"


def get_ai_gateway_config() -> AiGatewayConfig:
    return AiGatewayConfig()


def build_rule_based_bid_brief(
    *,
    project,
    readiness_summary: dict,
    requirements,
    clarifications,
) -> dict:
    high_risk_requirements = [r for r in requirements if r.risk_level == "high"]
    blocked_requirements = [r for r in requirements if r.status == "blocked"]
    needs_review_requirements = [r for r in requirements if r.status == "needs_review"]
    open_clarifications = [q for q in clarifications if q.status == "open"]
    high_priority_clarifications = [q for q in clarifications if q.priority == "high"]

    service_domain = project.tender_type or "the requested service scope"
    issuer = project.issuer or "the client"

    executive_summary = (
        f"This bid workspace reviews the RFP for {project.title} from {issuer}. "
        f"The current service domain is {service_domain}. "
        f"The system identified {len(requirements)} requirement item(s), "
        f"{len(high_risk_requirements)} high-risk requirement(s), and "
        f"{len(open_clarifications)} open clarification question(s). "
        f"Current readiness recommendation: {readiness_summary.get('recommendation', 'Not available')}."
    )

    key_risks = []

    if high_risk_requirements:
        for req in high_risk_requirements[:6]:
            key_risks.append(
                f"[{req.category}] {req.requirement_text}"
            )

    if blocked_requirements:
        key_risks.append(
            f"{len(blocked_requirements)} requirement(s) are currently blocked and may affect bid readiness."
        )

    if not key_risks:
        key_risks.append("No major high-risk requirement has been detected from current review data.")

    clarification_focus = []

    for question in high_priority_clarifications[:5]:
        clarification_focus.append(
            f"[{question.category}] {question.question_text}"
        )

    if not clarification_focus:
        for question in open_clarifications[:5]:
            clarification_focus.append(
                f"[{question.category}] {question.question_text}"
            )

    if not clarification_focus:
        clarification_focus.append("No open clarification question is currently available.")

    next_actions = []

    if needs_review_requirements:
        next_actions.append(
            f"Review and classify {len(needs_review_requirements)} requirement item(s) currently marked as needs_review."
        )

    if high_risk_requirements:
        next_actions.append(
            "Assign owners for high-risk requirements and validate delivery, legal, commercial, or security impact."
        )

    if open_clarifications:
        next_actions.append(
            f"Resolve or send {len(open_clarifications)} open clarification question(s) before final bid response."
        )

    if readiness_summary.get("readiness_score", 0) < 65:
        next_actions.append(
            "Run a focused bid review session before committing to final proposal response."
        )

    if not next_actions:
        next_actions.append("Proceed to final human review and export the readiness matrix.")

    assumptions = [
        "This brief is generated from extracted document text, requirement matrix, clarification questions, and review status.",
        "This v1 brief uses rules_only mode and does not send confidential RFP content to any external LLM.",
        "Human review remains mandatory before client-facing submission or internal bid approval.",
    ]

    return {
        "project_id": project.id,
        "project_title": project.title,
        "ai_mode": "rules_only",
        "generated_by": "rule_based_bid_brief_v1",
        "executive_summary": executive_summary,
        "readiness_recommendation": readiness_summary.get("recommendation", "Not available"),
        "key_risks": key_risks,
        "clarification_focus": clarification_focus,
        "next_actions": next_actions,
        "assumptions": assumptions,
    }
