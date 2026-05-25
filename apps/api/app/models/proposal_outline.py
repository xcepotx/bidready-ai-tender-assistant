from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderProposalSection(Base):
    __tablename__ = "tender_proposal_sections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, index=True)

    section_key: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_outline: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    draft_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_response_item_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidence_needed: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    risks: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="draft", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    generation_mode: Mapped[str] = mapped_column(String(50), default="rules_only", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
