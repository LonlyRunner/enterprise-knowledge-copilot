"""add users for JWT authentication"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c7d8e9f0a1b2"
down_revision = "f1c2d3e4a5b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"),
        sa.Column("role", sa.String(32), nullable=False, server_default="employee"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
