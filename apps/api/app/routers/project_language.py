from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.project_language import TenderProjectLanguageSetting
from app.schemas.tender import ProjectLanguageSettingResponse, ProjectLanguageSettingUpdate
from app.services.audit_service import create_audit_log


router = APIRouter(tags=["project_language"])


ALLOWED_INPUT_LANGUAGES = {"auto", "en", "id"}
ALLOWED_OUTPUT_LANGUAGES = {"en", "id"}


def snapshot_language_setting(setting: TenderProjectLanguageSetting) -> dict:
    return {
        "id": setting.id,
        "project_id": setting.project_id,
        "input_language": setting.input_language,
        "output_language": setting.output_language,
    }


def get_or_create_language_setting(db: Session, project_id: int) -> TenderProjectLanguageSetting:
    setting = (
        db.query(TenderProjectLanguageSetting)
        .filter(TenderProjectLanguageSetting.project_id == project_id)
        .first()
    )

    if setting:
        return setting

    setting = TenderProjectLanguageSetting(
        project_id=project_id,
        input_language="auto",
        output_language="en",
    )

    db.add(setting)
    db.commit()
    db.refresh(setting)

    return setting


@router.get(
    "/api/v1/projects/{project_id}/language",
    response_model=ProjectLanguageSettingResponse,
)
def get_project_language_setting(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return get_or_create_language_setting(db, project_id)


@router.patch(
    "/api/v1/projects/{project_id}/language",
    response_model=ProjectLanguageSettingResponse,
)
def update_project_language_setting(
    project_id: int,
    payload: ProjectLanguageSettingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    x_actor: str | None = Header(default="dev_user", alias="X-Actor"),
):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    setting = get_or_create_language_setting(db, project_id)
    data = payload.model_dump(exclude_unset=True)

    if "input_language" in data and data["input_language"] not in ALLOWED_INPUT_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input_language. Allowed: {sorted(ALLOWED_INPUT_LANGUAGES)}",
        )

    if "output_language" in data and data["output_language"] not in ALLOWED_OUTPUT_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_language. Allowed: {sorted(ALLOWED_OUTPUT_LANGUAGES)}",
        )

    before = snapshot_language_setting(setting)

    for field, value in data.items():
        setattr(setting, field, value)

    setting.updated_at = datetime.utcnow()

    db.flush()

    after = snapshot_language_setting(setting)

    create_audit_log(
        db,
        project_id=project_id,
        actor=x_actor,
        action="update_language_setting",
        entity_type="project_language_setting",
        entity_id=setting.id,
        before_json=before,
        after_json=after,
        ip_address=request.client.host if request.client else None,
        notes="Project language setting updated",
    )

    db.commit()
    db.refresh(setting)

    return setting
