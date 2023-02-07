"""create posts table

Revision ID: 282a1e452ac6
Revises: 
Create Date: 2023-02-06 16:00:11.197359

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "282a1e452ac6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("posts")
