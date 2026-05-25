from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderResponseItem(Base):
    __tablename__ = "tender_response_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)
    requirement_id: Mapped[int | None] = mapped_column(ForeignKey("tender_requirements.id"), nullable=True, index=True)

    category: Mapped[str] = mapped_column(String(120), default="general", nullable=False)
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)

    compliance_status: Mapped[str] = mapped_column(String(80), default="needs_review", nullable=False)
    response_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    evidence_needed: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    risks: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="draft", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.60, nullable=False)

    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_quote: Mapped[str | None] = mapped_column(Text, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
