from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender import TenderProject
from app.models.audit import AuditLog
from app.schemas.tender import AuditLogResponse


router = APIRouter(tags=["audit_logs"])


@router.get("/api/v1/projects/{project_id}/audit-logs", response_model=list[AuditLogResponse])
def list_project_audit_logs(project_id: int, db: Session = Depends(get_db)):
    project = db.get(TenderProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return (
        db.query(AuditLog)
        .filter(AuditLog.project_id == project_id)
        .order_by(AuditLog.id.desc())
        .limit(300)
        .all()
    )


@router.get("/api/v1/audit-logs", response_model=list[AuditLogResponse])
def list_recent_audit_logs(db: Session = Depends(get_db)):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .limit(300)
        .all()
    )
