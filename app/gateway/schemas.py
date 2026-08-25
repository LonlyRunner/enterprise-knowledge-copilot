from typing import Any, Dict, Optional, List
from uuid import UUID
from pydantic import BaseModel


class GatewayRequest(BaseModel):

    user_id: Optional[str] = None

    tenant_id: Optional[str] = None


    knowledge_base_id: Optional[UUID] = None


    message: str


    mode: str = "chat"


    metadata: Dict[str, Any] = {}


class GatewayResponse(BaseModel):

    request_id: str

    task_id: Optional[str] = None

    trace_id: str

    status: str

    answer: Optional[str] = None

    citations: List[dict] = []

    agent_steps: List[dict] = []

    usage: Dict[str, int] = {}