from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderDocument, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.schemas.tender import AiGatewayConfigResponse, BidBriefResponse
from app.services.ai_gateway import get_ai_gateway_config, build_rule_based_bid_brief


router = APIRouter(tags=["ai"])


def compute_readiness_summary_dict(project, documents, requirements, clarifications) -> dict:
    requirement_count = len(requirements)
    document_count = len(documents)

    high_risk_requirement_count = len([r for r in requirements if r.risk_level == "high"])
    blocked_requirement_count = len([r for r in requirements if r.status == "blocked"])
    needs_review_requirement_count = len([r for r in requirements if r.status == "needs_review"])
    accepted_requirement_count = len([r for r in requirements if r.status == "accepted"])

    open_clarification_count = len([q for q in clarifications if q.status == "open"])
    high_priority_clarification_count = len([q for q in clarifications if q.priority == "high"])

    score = 100

    if document_count == 0:
        score -= 40

    if requirement_count == 0:
        score -= 35

    score -= min(high_risk_requirement_count * 6, 30)
    score -= min(blocked_requirement_count * 12, 30)
    score -= min(needs_review_requirement_count * 3, 25)
    score -= min(open_clarification_count * 4, 28)
    score -= min(high_priority_clarification_count * 5, 25)

    readiness_score = max(0, min(100, score))

    if readiness_score >= 85:
        recommendation = "Ready for final review"
    elif readiness_score >= 65:
        recommendation = "Proceed with clarification"
    elif readiness_score >= 40:
        recommendation = "Needs focused bid review"
    else:
        recommendation = "Not ready"

    return {
        "readiness_score": readiness_score,
        "recommendation": recommendation,
        "requirement_count": requirement_count,
        "document_count": document_count,
        "high_risk_requirement_count": high_risk_requirement_count,
        "blocked_requirement_count": blocked_requirement_count,
        "needs_review_requirement_count": needs_review_requirement_count,
        "accepted_requirement_count": accepted_requirement_count,
        "open_clarification_count": open_clarification_count,
        "high_priority_clarification_count": high_priority_clarification_count,
    }


@router.get("/api/v1/ai/config", response_model=AiGatewayConfigResponse)
def get_ai_config():
    config = get_ai_gateway_config()

    return {
        "mode": config.mode,
        "provider": config.provider,
        "model": config.model,
        "external_call_enabled": config.external_call_enabled,
    }


@router.get("/api/v1/projects/{project_id}/bid-brief", response_model=BidBriefResponse)
def get_project_bid_brief(project_id: int, db: Session = Depends(get_db)):
    config = get_ai_gateway_config()

    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    documents = (
        db.query(TenderDocument)
        .filter(TenderDocument.project_id == project_id)
        .all()
    )

    requirements = (
        db.query(TenderRequirement)
        .filter(TenderRequirement.project_id == project_id)
        .order_by(TenderRequirement.category.asc(), TenderRequirement.id.asc())
        .all()
    )

    clarifications = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .order_by(TenderClarificationQuestion.priority.desc(), TenderClarificationQuestion.id.asc())
        .all()
    )

    readiness_summary = compute_readiness_summary_dict(
        project=project,
        documents=documents,
        requirements=requirements,
        clarifications=clarifications,
    )

    # Current enterprise-safe MVP mode:
    # Do not call any external LLM even if config exists.
    if config.mode == "rules_only":
        return build_rule_based_bid_brief(
            project=project,
            readiness_summary=readiness_summary,
            requirements=requirements,
            clarifications=clarifications,
        )

    # Placeholder for later approved provider integration.
    # We still return rule-based output until an approved provider is configured and reviewed.
    brief = build_rule_based_bid_brief(
        project=project,
        readiness_summary=readiness_summary,
        requirements=requirements,
        clarifications=clarifications,
    )
    brief["ai_mode"] = config.mode
    brief["generated_by"] = "gateway_placeholder_rule_based_fallback"
    return brief
