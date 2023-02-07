"""add foreign key to posts table

Revision ID: 5db9081bbc3c
Revises: bbd550a9430a
Create Date: 2023-02-06 20:13:41.999380

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5db9081bbc3c"
down_revision = "bbd550a9430a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "posts_users_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("posts_users_fk", table_name="posts")
    op.drop_column("posts", "owner_id")
