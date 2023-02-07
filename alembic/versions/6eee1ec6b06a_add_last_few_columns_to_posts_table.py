"""add last few columns to posts table

Revision ID: 6eee1ec6b06a
Revises: 5db9081bbc3c
Create Date: 2023-02-06 20:22:57.313601

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "6eee1ec6b06a"
down_revision = "5db9081bbc3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("published", sa.Boolean(), nullable=False, server_default="TRUE"),
    )
    op.add_column(
        "posts",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
