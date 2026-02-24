"""fix products updated_at default

Revision ID: 2826c2a22282
Revises: 780392d4a504
Create Date: 2026-02-21 17:44:45.545793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2826c2a22282'
down_revision: Union[str, None] = '780392d4a504'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("UPDATE products SET updated_at = now() WHERE updated_at IS NULL")
    op.alter_column(
        "products", "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False
    )

def downgrade():
    op.alter_column("products", "updated_at", server_default=None)