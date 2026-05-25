from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject, TenderRequirement
from app.models.clarification import TenderClarificationQuestion
from app.schemas.tender import ClarificationQuestionResponse, ClarificationQuestionUpdate, ClarificationBulkUpdate, BulkUpdateResponse
from app.services.clarification_generator import generate_clarification_questions
from app.services.audit_service import create_audit_log
from app.services.i18n_service import get_project_output_language, localize_payload


router = APIRouter(tags=["clarifications"])


ALLOWED_STATUS = {
    "open",
    "answered",
    "closed",
    "cancelled",
    "needs_internal_review",
}

ALLOWED_RISK = {
    "low",
    "medium",
    "high",
}

ALLOWED_PRIORITY = {
    "low",
    "medium",
    "high",
}


def snapshot_clarification(question: TenderClarificationQuestion) -> dict:
    return {
        "id": question.id,
        "project_id": question.project_id,
        "requirement_id": question.requirement_id,
        "category": question.category,
        "question_text": question.question_text,
        "reason": question.reason,
        "priority": question.priority,
        "risk_level": question.risk_level,
        "source_page": question.source_page,
        "owner": question.owner,
        "status": question.status,
        "notes": question.notes,
    }


@router.post(
    "/api/v1/projects/{project_id}/generate-clarifications",
    response_model=list[ClarificationQuestionResponse],
)
def generate_project_clarifications(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    requirements = (
        db.query(TenderRequirement)
        .filter(TenderRequirement.project_id == project_id)
        .order_by(TenderRequirement.category.asc(), TenderRequirement.id.asc())
        .all()
    )

    if not requirements:
        raise HTTPException(status_code=400, detail="No requirements found. Run RFP analysis first.")

    old_count = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .count()
    )

    db.query(TenderClarificationQuestion).filter(
        TenderClarificationQuestion.project_id == project_id
    ).delete(synchronize_session=False)

    generated = generate_clarification_questions(requirements)

    output_language = get_project_output_language(db, project_id)
    generated = localize_payload(generated, output_language)
    created = []

    for item in generated:
        question = TenderClarificationQuestion(
            project_id=project_id,
            requirement_id=item["requirement_id"],
            category=item["category"],
            question_text=item["question_text"],
            reason=item["reason"],
            priority=item["priority"],
            risk_level=item["risk_level"],
            source_page=item["source_page"],
            owner=item["owner"],
            status=item["status"],
            notes=item["notes"],
        )
        db.add(question)
        created.append(question)

    db.flush()

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="generate_clarifications",
        entity_type="clarification_batch",
        entity_id=None,
        before_json={"old_count": old_count},
        after_json={"new_count": len(created)},
        ip_address=request.client.host if request.client else None,
        notes="Clarification questions regenerated",
    )

    db.commit()

    for question in created:
        db.refresh(question)

    return created


@router.get(
    "/api/v1/projects/{project_id}/clarifications",
    response_model=list[ClarificationQuestionResponse],
)
def list_project_clarifications(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.project_id == project_id)
        .order_by(
            TenderClarificationQuestion.priority.desc(),
            TenderClarificationQuestion.id.asc(),
        )
        .all()
    )




@router.patch(
    "/api/v1/clarifications/bulk-update",
    response_model=BulkUpdateResponse,
)
def bulk_update_clarification_questions(
    payload: ClarificationBulkUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    if not payload.question_ids:
        raise HTTPException(status_code=400, detail="question_ids is required")

    data = payload.model_dump(exclude_unset=True)
    ids = data.pop("question_ids", [])

    if "status" in data and data["status"] is not None and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "risk_level" in data and data["risk_level"] is not None and data["risk_level"] not in ALLOWED_RISK:
        raise HTTPException(status_code=400, detail=f"Invalid risk_level. Allowed: {sorted(ALLOWED_RISK)}")

    if "priority" in data and data["priority"] is not None and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}")

    patch = {key: value for key, value in data.items() if value is not None}

    if not patch:
        raise HTTPException(status_code=400, detail="No update fields provided")

    questions = (
        db.query(TenderClarificationQuestion)
        .filter(TenderClarificationQuestion.id.in_(ids))
        .all()
    )

    if not questions:
        raise HTTPException(status_code=404, detail="No matching clarification questions found")

    project_ids = {item.project_id for item in questions}
    project_id = list(project_ids)[0] if len(project_ids) == 1 else None

    before = [snapshot_clarification(item) for item in questions]

    for question in questions:
        for field, value in patch.items():
            setattr(question, field, value)

    db.flush()

    after = [snapshot_clarification(item) for item in questions]

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="bulk_update_clarifications",
        entity_type="clarification_batch",
        entity_id=None,
        before_json={"items": before},
        after_json={"items": after, "patch": patch},
        ip_address=request.client.host if request.client else None,
        notes=f"Bulk updated {len(questions)} clarification question(s)",
    )

    db.commit()

    return {
        "updated_count": len(questions),
        "ids": [item.id for item in questions],
    }

@router.patch(
    "/api/v1/clarifications/{question_id}",
    response_model=ClarificationQuestionResponse,
)
def update_clarification_question(
    question_id: int,
    payload: ClarificationQuestionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    question = db.get(TenderClarificationQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Clarification question not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(ALLOWED_STATUS)}")

    if "risk_level" in data and data["risk_level"] not in ALLOWED_RISK:
        raise HTTPException(status_code=400, detail=f"Invalid risk_level. Allowed: {sorted(ALLOWED_RISK)}")

    if "priority" in data and data["priority"] not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Allowed: {sorted(ALLOWED_PRIORITY)}")

    before = snapshot_clarification(question)

    for field, value in data.items():
        setattr(question, field, value)

    db.flush()

    after = snapshot_clarification(question)

    create_audit_log(
        db,
        project_id=question.project_id,
        actor=x_actor,
        action="update_clarification",
        entity_type="clarification_question",
        entity_id=question.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Clarification question updated from API",
    )

    db.commit()
    db.refresh(question)

    return question
