"""create document chunks

Revision ID: 538f439727f3
Revises: 36336eb2ab52
Create Date: 2026-05-20 10:56:08.810339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '538f439727f3'
down_revision: Union[str, Sequence[str], None] = '36336eb2ab52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
