from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderActionItem(Base):
    __tablename__ = "tender_action_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    related_requirement_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_response_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_clarification_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_evidence_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_proposal_section_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    owner: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False, index=True)
    due_date: Mapped[str | None] = mapped_column(String(120), nullable=True)

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
