from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderClarificationResponseItem(Base):
    __tablename__ = "tender_clarification_response_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    # Snapshot IDs only. Clarification questions can be regenerated, so do not create FK lock.
    clarification_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    requirement_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    category: Mapped[str] = mapped_column(String(120), default="general", nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    client_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_status: Mapped[str] = mapped_column(String(50), default="open", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(50), default="medium", nullable=False, index=True)

    owner: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    due_date: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sent_at: Mapped[str | None] = mapped_column(String(120), nullable=True)
    response_received_at: Mapped[str | None] = mapped_column(String(120), nullable=True)
    incorporated_at: Mapped[str | None] = mapped_column(String(120), nullable=True)

    impacted_artifacts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_response_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_compliance_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_risk_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_addendum_impact_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    recommended_follow_up: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
