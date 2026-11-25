"""Add description_en column to cameras for CLIP/SigLIP native search

Revision ID: b2d9e41c7a10
Revises: a8c4e91f2b30
Create Date: 2026-11-25 06:45:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2d9e41c7a10"
down_revision: Union[str, None] = "a8c4e91f2b30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cameras",
        sa.Column("description_en", sa.String(length=100), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("cameras", "description_en")
