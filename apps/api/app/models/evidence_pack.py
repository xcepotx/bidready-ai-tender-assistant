from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderEvidenceItem(Base):
    __tablename__ = "tender_evidence_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    evidence_name: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_category: Mapped[str] = mapped_column(String(120), default="general", nullable=False)

    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="open", nullable=False)
    priority: Mapped[str] = mapped_column(String(80), default="medium", nullable=False)

    source_type: Mapped[str] = mapped_column(String(80), default="generated", nullable=False)
    source_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_requirement_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_response_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_proposal_section_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
