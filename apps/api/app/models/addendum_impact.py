from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderAddendumImpactItem(Base):
    __tablename__ = "tender_addendum_impact_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    document_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    source_document_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    impact_type: Mapped[str] = mapped_column(String(80), default="document_change", nullable=False, index=True)
    impacted_artifact: Mapped[str] = mapped_column(String(80), default="requirements", nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), default="medium", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default="open", nullable=False, index=True)

    source_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    due_date: Mapped[str | None] = mapped_column(String(120), nullable=True)

    related_requirement_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_response_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_clarification_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_compliance_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_risk_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_approval_step_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
