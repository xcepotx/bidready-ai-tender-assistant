from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.session import Base

# Import all model modules so SQLAlchemy metadata is populated.
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


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return settings.database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
