"""Application schema bootstrap for PostgreSQL warehouse metadata.

PostgreSQL 15+ revokes CREATE on schema ``public`` from non-owners. Local and
managed databases often connect as a non-owner role (e.g. ``dataforge_user``),
so ``Base.metadata.create_all()`` fails with ``permission denied for schema
public`` and metadata tables are never created.

DataForge therefore ensures a dedicated schema owned by the connecting role and
places warehouse objects on that schema via ``search_path``.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.logging import get_logger

logger = get_logger("db.schema")

# Dedicated schema owned by the application database role.
APPLICATION_SCHEMA = "dataforge"


def uses_application_schema(db_engine: Engine) -> bool:
    return db_engine.dialect.name == "postgresql"


def ensure_application_schema(db_engine: Engine) -> str | None:
    """Create the application schema when running on PostgreSQL.

    Returns the schema name, or ``None`` for dialects that do not need it
    (e.g. SQLite test databases).
    """
    if not uses_application_schema(db_engine):
        return None

    with db_engine.begin() as connection:
        connection.execute(
            text(
                f'CREATE SCHEMA IF NOT EXISTS "{APPLICATION_SCHEMA}" '
                "AUTHORIZATION CURRENT_USER"
            )
        )
        connection.execute(
            text(f'SET search_path TO "{APPLICATION_SCHEMA}", public')
        )

    logger.info(
        "Application schema ready | schema={} | search_path={},public",
        APPLICATION_SCHEMA,
        APPLICATION_SCHEMA,
    )
    return APPLICATION_SCHEMA


def configure_search_path(dbapi_connection) -> None:
    """Apply search_path on each pooled PostgreSQL connection."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute(f'SET search_path TO "{APPLICATION_SCHEMA}", public')
    finally:
        cursor.close()
