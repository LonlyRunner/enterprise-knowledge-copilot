"""add tenant ownership to knowledge bases"""
from alembic import op
import sqlalchemy as sa

revision = "d9e0f1a2b3c4"
down_revision = "c7d8e9f0a1b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("knowledge_bases", sa.Column("tenant_id", sa.String(64), nullable=True, server_default="default"))
    op.execute("UPDATE knowledge_bases SET tenant_id = 'default' WHERE tenant_id IS NULL")
    op.alter_column("knowledge_bases", "tenant_id", nullable=False, server_default="default")
    op.create_index("ix_knowledge_bases_tenant_id", "knowledge_bases", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_bases_tenant_id", table_name="knowledge_bases")
    op.drop_column("knowledge_bases", "tenant_id")
