import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.knowledge_base import (
        KnowledgeBaseModel,
    )
    from app.models.message import (
        MessageModel,
    )


class ConversationModel(Base):

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    knowledge_base_id: Mapped[
        uuid.UUID
    ] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "knowledge_bases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary_message_id: Mapped[
        uuid.UUID | None
    ] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "messages.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    knowledge_base: Mapped[
        "KnowledgeBaseModel"
    ] = relationship(
        back_populates="conversations",
    )

    messages: Mapped[
        list["MessageModel"]
    ] = relationship(
        "MessageModel",
        back_populates="conversation",
        foreign_keys=(
            "MessageModel.conversation_id"
        ),
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    summary_message: Mapped[
        "MessageModel | None"
    ] = relationship(
        "MessageModel",
        foreign_keys=[
            summary_message_id
        ],
        post_update=True,
    )