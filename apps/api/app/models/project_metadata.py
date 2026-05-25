from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderProjectMetadata(Base):
    __tablename__ = "tender_project_metadata"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    package_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    submission_deadline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clarification_deadline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    proposal_validity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    submission_requirements: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source_evidence: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    extraction_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
