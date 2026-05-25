from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderApprovalRequest(Base):
    __tablename__ = "tender_approval_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(40), default="draft", nullable=False, index=True)
    current_step_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    submitted_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    final_decision: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class TenderApprovalStep(Base):
    __tablename__ = "tender_approval_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)
    approval_request_id: Mapped[int] = mapped_column(ForeignKey("tender_approval_requests.id"), nullable=False, index=True)

    step_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    approver_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    approver_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(40), default="not_started", nullable=False, index=True)
    due_date: Mapped[str | None] = mapped_column(String(120), nullable=True)

    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
