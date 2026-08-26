"""persist AI write approvals"""
from alembic import op
import sqlalchemy as sa

revision = "e0f1a2b3c4d5"
down_revision = "d9e0f1a2b3c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_approvals",
        sa.Column("approval_id", sa.String(80), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("idempotency_key", sa.String(128), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_by", sa.String(128), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_approvals_tenant_id", "ai_approvals", ["tenant_id"])
    op.create_index("ix_ai_approvals_user_id", "ai_approvals", ["user_id"])
    op.create_index("ix_ai_approvals_idempotency_key", "ai_approvals", ["idempotency_key"])
    op.create_index(
        "uq_ai_approval_idempotency",
        "ai_approvals",
        ["tenant_id", "user_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_ai_approvals_idempotency_key", table_name="ai_approvals")
    op.drop_index("uq_ai_approval_idempotency", table_name="ai_approvals")
    op.drop_index("ix_ai_approvals_user_id", table_name="ai_approvals")
    op.drop_index("ix_ai_approvals_tenant_id", table_name="ai_approvals")
    op.drop_table("ai_approvals")
