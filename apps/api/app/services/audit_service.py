from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    *,
    project_id: int | None,
    actor: str | None,
    action: str,
    entity_type: str,
    entity_id: int | None,
    before_json: dict | None,
    after_json: dict | None,
    ip_address: str | None = None,
    notes: str | None = None,
) -> AuditLog:
    log = AuditLog(
        project_id=project_id,
        actor=actor or "dev_user",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_json=before_json,
        after_json=after_json,
        ip_address=ip_address,
        notes=notes,
    )
    db.add(log)
    return log
