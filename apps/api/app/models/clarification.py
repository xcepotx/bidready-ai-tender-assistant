from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class TenderClarificationQuestion(Base):
    __tablename__ = "tender_clarification_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False)
    requirement_id: Mapped[int | None] = mapped_column(ForeignKey("tender_requirements.id"), nullable=True)

    category: Mapped[str] = mapped_column(String(80), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
