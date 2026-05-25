from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderProjectLanguageSetting(Base):
    __tablename__ = "tender_project_language_settings"
    __table_args__ = (
        UniqueConstraint("project_id", name="uq_tender_project_language_settings_project_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    # auto = let extractor detect/source language
    input_language: Mapped[str] = mapped_column(String(20), default="auto", nullable=False)

    # en / id = language used for generated analysis, questions, plans, reports
    output_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
