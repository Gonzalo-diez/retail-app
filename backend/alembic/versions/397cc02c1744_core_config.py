"""core/config

Revision ID: 397cc02c1744
Revises: 4d59ffa574a2
Create Date: 2026-02-24 18:22:46.564691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '397cc02c1744'
down_revision: Union[str, None] = '4d59ffa574a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
