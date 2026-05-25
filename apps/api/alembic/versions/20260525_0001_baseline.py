"""baseline schema from SQLAlchemy metadata

Revision ID: 20260525_0001
Revises:
Create Date: 2026-05-25

This baseline migration mirrors the current SQLAlchemy metadata. It is safe to
run against an existing database because SQLAlchemy create_all checks for
existing tables before creating them.
"""

from __future__ import annotations

from alembic import op

from app.db.session import Base

# Import all models so Base.metadata contains every mapped table.
from app.models import action_item  # noqa: F401
from app.models import addendum_impact  # noqa: F401
from app.models import approval_workflow  # noqa: F401
from app.models import audit  # noqa: F401
from app.models import clarification  # noqa: F401
from app.models import clarification_response_tracker  # noqa: F401
from app.models import compliance_scorecard  # noqa: F401
from app.models import decision_gate  # noqa: F401
from app.models import evidence_pack  # noqa: F401
from app.models import project_language  # noqa: F401
from app.models import project_metadata  # noqa: F401
from app.models import proposal_outline  # noqa: F401
from app.models import proposal_template  # noqa: F401
from app.models import response_plan  # noqa: F401
from app.models import risk_item  # noqa: F401
from app.models import tender  # noqa: F401


revision = "20260525_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
