from typing import TypedDict


class AgentState(
    TypedDict
):

    question: str

    intent: str | None

    answer: str | None


    tenant_id: str

    user_id: str

    trace_id: str


    need_human_review: bool

    human_action: str | None