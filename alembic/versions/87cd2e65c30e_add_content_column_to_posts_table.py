"""add content column to posts table

Revision ID: 87cd2e65c30e
Revises: 282a1e452ac6
Create Date: 2023-02-06 16:33:56.426077

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "87cd2e65c30e"
down_revision = "282a1e452ac6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "content")
