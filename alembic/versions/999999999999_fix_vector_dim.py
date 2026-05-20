"""fix vector dimensions

Revision ID: 999999999999
Revises: 712071959596
Create Date: 2026-05-20 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


# revision identifiers, used by Alembic.
revision: str = '999999999999'
down_revision: Union[str, Sequence[str], None] = '712071959596'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL to alter the vector column dimension from 1536 to 384
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(384);")


def downgrade() -> None:
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536);")
