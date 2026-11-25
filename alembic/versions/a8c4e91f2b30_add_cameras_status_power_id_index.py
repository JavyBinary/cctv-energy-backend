from typing import Sequence, Union

from alembic import op

revision: str = "a8c4e91f2b30"
down_revision: Union[str, None] = "119554b1686e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_cameras_status_power_id",
        "cameras",
        ["status", "power", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_cameras_status_power_id", table_name="cameras")
