"""defaults import_runs rows

Revision ID: 4d59ffa574a2
Revises: 2826c2a22282
Create Date: 2026-02-22 22:26:50.060459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d59ffa574a2'
down_revision: Union[str, None] = '2826c2a22282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("UPDATE import_runs SET rows_total = 0 WHERE rows_total IS NULL")
    op.execute("UPDATE import_runs SET rows_success = 0 WHERE rows_success IS NULL")
    op.execute("UPDATE import_runs SET rows_failed = 0 WHERE rows_failed IS NULL")

    op.alter_column("import_runs", "rows_total",
        existing_type=sa.Integer(),
        server_default=sa.text("0"),
        existing_nullable=False
    )
    op.alter_column("import_runs", "rows_success",
        existing_type=sa.Integer(),
        server_default=sa.text("0"),
        existing_nullable=False
    )
    op.alter_column("import_runs", "rows_failed",
        existing_type=sa.Integer(),
        server_default=sa.text("0"),
        existing_nullable=False
    )

def downgrade():
    op.alter_column("import_runs", "rows_total", server_default=None)
    op.alter_column("import_runs", "rows_success", server_default=None)
    op.alter_column("import_runs", "rows_failed", server_default=None)
