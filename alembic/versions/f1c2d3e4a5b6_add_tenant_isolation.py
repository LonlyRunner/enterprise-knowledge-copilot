"""add tenant isolation columns"""
from alembic import op
import sqlalchemy as sa

revision = "f1c2d3e4a5b6"
down_revision = "e78a72b98e23"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("documents", sa.Column("tenant_id", sa.String(64), nullable=True, server_default="default"))
    op.add_column("document_chunks", sa.Column("tenant_id", sa.String(64), nullable=True, server_default="default"))
    op.create_index("ix_documents_tenant_id", "documents", ["tenant_id"])
    op.create_index("ix_document_chunks_tenant_id", "document_chunks", ["tenant_id"])
    op.execute("UPDATE documents SET tenant_id = 'default' WHERE tenant_id IS NULL")
    op.execute("UPDATE document_chunks SET tenant_id = 'default' WHERE tenant_id IS NULL")
    op.alter_column("documents", "tenant_id", nullable=False, server_default="default")
    op.alter_column("document_chunks", "tenant_id", nullable=False, server_default="default")

def downgrade() -> None:
    op.drop_index("ix_document_chunks_tenant_id", table_name="document_chunks")
    op.drop_index("ix_documents_tenant_id", table_name="documents")
    op.drop_column("document_chunks", "tenant_id")
    op.drop_column("documents", "tenant_id")
