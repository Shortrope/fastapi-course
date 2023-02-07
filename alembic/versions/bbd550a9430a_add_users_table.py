"""add users table

Revision ID: bbd550a9430a
Revises: 87cd2e65c30e
Create Date: 2023-02-06 20:02:42.507274

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "bbd550a9430a"
down_revision = "87cd2e65c30e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade() -> None:
    op.drop_table("users")
