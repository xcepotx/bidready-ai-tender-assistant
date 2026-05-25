from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TenderProposalTemplate(Base):
    __tablename__ = "tender_proposal_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("tender_projects.id"), nullable=False, unique=True, index=True)

    template_name: Mapped[str] = mapped_column(String(255), default="Standard Executive Proposal", nullable=False)
    executive_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_profile: Mapped[str | None] = mapped_column(Text, nullable=True)
    win_theme: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposal_tone: Mapped[str] = mapped_column(String(80), default="formal", nullable=False)

    section_order: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    excluded_section_keys: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    custom_sections: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    footer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
