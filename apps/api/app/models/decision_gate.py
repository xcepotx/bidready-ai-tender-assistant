from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderDecisionGate(Base):
    __tablename__ = "tender_decision_gates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    decision_status: Mapped[str] = mapped_column(String(80), default="needs_executive_review", nullable=False)
    recommendation: Mapped[str] = mapped_column(String(255), nullable=False)
    readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.70, nullable=False)

    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_reasons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    blockers: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    required_approvals: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    next_actions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    owner: Mapped[str | None] = mapped_column(String(120), default="bid_manager", nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
