from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "119554b1686e"
down_revision: Union[str, None] = "3d256f2efd5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("cameras", "is_outdoor")


def downgrade() -> None:
    op.add_column(
        "cameras",
        sa.Column("is_outdoor", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
