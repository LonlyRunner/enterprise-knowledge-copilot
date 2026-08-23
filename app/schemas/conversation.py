import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class ConversationCreateRequest(
    BaseModel
):
    title: str | None = Field(
        default=None,
        max_length=255,
    )


class ConversationResponse(
    BaseModel
):
    id: uuid.UUID

    knowledge_base_id: uuid.UUID

    title: str | None

    summary: str | None = None

    created_at: datetime

    updated_at: datetime


class ConversationListResponse(
    BaseModel
):
    items: list[
        ConversationResponse
    ]


class MessageResponse(
    BaseModel
):
    id: uuid.UUID

    role: str

    content: str

    created_at: datetime


class ConversationDetailResponse(
    BaseModel
):
    conversation: (
        ConversationResponse
    )

    messages: list[
        MessageResponse
    ]