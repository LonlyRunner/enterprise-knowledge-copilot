from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.contracts import AgentResult


class GatewayRequest(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=10_000)
    # Legacy project-B callers used ``message``. Keep it as a compatibility
    # input while the project-C public contract uses ``question``.
    message: str | None = Field(default=None, min_length=1, max_length=10_000)
    mode: Literal["auto", "chat", "rag", "agent"] = "auto"
    knowledge_base_id: uuid.UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    model: str | None = None
    approve_actions: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_rag_mode(self):
        if self.question is None and self.message is not None:
            self.question = self.message
        if not self.question:
            raise ValueError("question is required")
        if self.mode == "rag" and self.knowledge_base_id is None:
            raise ValueError("knowledge_base_id is required when mode=rag")
        return self


class GatewayResponse(AgentResult):
    pass
