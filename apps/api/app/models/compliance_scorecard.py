from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderComplianceItem(Base):
    __tablename__ = "tender_compliance_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    requirement_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    response_item_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    category: Mapped[str] = mapped_column(String(120), default="general", nullable=False, index=True)
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)

    compliance_status: Mapped[str] = mapped_column(String(80), default="needs_review", nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    owner: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(80), default="medium", nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(80), default="medium", nullable=False, index=True)

    evidence_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidence_coverage: Mapped[str] = mapped_column(String(80), default="missing", nullable=False, index=True)

    gap_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
