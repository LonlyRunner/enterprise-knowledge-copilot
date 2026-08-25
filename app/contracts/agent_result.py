from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentCitation(BaseModel):
    source: str
    content: str = ""
    chunk_id: str | None = None
    score: float | None = None


class ToolInvocation(BaseModel):
    server: str = "enterprise-business"
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    success: bool
    result: dict[str, Any] = Field(default_factory=dict)


class AgentArtifact(BaseModel):
    type: str
    name: str
    content: Any


class ApprovalRequest(BaseModel):
    approval_id: str
    action: str
    reason: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: Literal["pending", "approved", "rejected"] = "pending"


class TokenUsageSummary(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class AgentStep(BaseModel):
    task_id: str
    agent: Literal["supervisor", "chat", "rag", "action"]
    action: str
    status: Literal["planned", "completed", "skipped", "failed"]
    summary: str = ""
    depends_on: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    request_id: str
    task_id: str
    trace_id: str
    status: Literal["completed", "partial", "pending_approval", "failed"]
    answer: str
    route: str
    model: str
    citations: list[AgentCitation] = Field(default_factory=list)
    agent_steps: list[AgentStep] = Field(default_factory=list)
    tool_calls: list[ToolInvocation] = Field(default_factory=list)
    artifacts: list[AgentArtifact] = Field(default_factory=list)
    approvals: list[ApprovalRequest] = Field(default_factory=list)
    usage: TokenUsageSummary = Field(default_factory=TokenUsageSummary)
