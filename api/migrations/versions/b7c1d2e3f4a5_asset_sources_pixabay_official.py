"""asset sources: pixabay, official_rockstar (V7.4, D20)

Revision ID: b7c1d2e3f4a5
Revises: d63e36a38321
Create Date: 2026-11-06 13:30:00
"""
from alembic import op

revision = "b7c1d2e3f4a5"
down_revision = "d63e36a38321"
branch_labels = None
depends_on = None

OLD = ("own", "trend_radar", "pexels", "ai_generated", "tts", "royalty_free")
NEW = ("own", "trend_radar", "pexels", "pixabay", "official_rockstar", "ai_generated", "tts", "royalty_free")


def _set(values):
    op.drop_constraint("source_allowed", "assets", type_="check")
    op.create_check_constraint("source_allowed", "assets", "source in (" + ", ".join(repr(v) for v in values) + ")")


def upgrade() -> None:
    _set(NEW)


def downgrade() -> None:
    _set(OLD)
