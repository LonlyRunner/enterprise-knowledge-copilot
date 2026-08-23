from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from app.conversation.token_budget import (
    DEFAULT_TOKEN_BUDGET,
)
from app.conversation.token_counter import (
    TokenCounter,
)

from app.conversation.recent_message_window import (
    RecentMessageWindow,
)


router = APIRouter()


class TokenCountRequest(BaseModel):
    text: str


class TokenMessage(BaseModel):
    role: str
    content: str


class TokenMessagesRequest(BaseModel):
    messages: list[TokenMessage]

class RecentMessageWindowRequest(BaseModel):
    messages: list[TokenMessage]

    token_budget: int | None = None

@router.get(
    "/token-budget",
)
async def get_token_budget():
    """
    查看当前默认 Token Budget。
    """

    budget = DEFAULT_TOKEN_BUDGET

    return {
        "context_window": budget.context_window,
        "output_reserve": budget.output_reserve,
        "safety_buffer": budget.safety_buffer,

        "input_budget": budget.input_budget,

        "allocation": {
            "system_prompt": (
                budget.system_prompt_budget
            ),
            "conversation_summary": (
                budget.summary_budget
            ),
            "recent_messages": (
                budget.recent_messages_budget
            ),
            "retrieved_context": (
                budget.retrieved_context_budget
            ),
            "current_question": (
                budget.current_question_budget
            ),
        },

        "allocated_input_budget": (
            budget.allocated_input_budget
        ),

        "unallocated_input_budget": (
            budget.unallocated_input_budget
        ),

        "total_reserved": (
            budget.total_reserved
        ),
    }


@router.post(
    "/token-count",
)
async def count_text_tokens(
    request: TokenCountRequest,
):
    """
    测试单段文本的 Token 数。
    """

    counter = TokenCounter()

    token_count = counter.count_text(
        request.text
    )

    return {
        "text": request.text,
        "characters": len(request.text),
        "estimated_tokens": token_count,
    }


@router.post(
    "/messages/token-count",
)
async def count_message_tokens(
    request: TokenMessagesRequest,
):
    """
    测试多条 Message 的 Token 使用量。
    """

    counter = TokenCounter()

    messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in request.messages
    ]

    token_count = counter.count_messages(
        messages
    )

    budget = DEFAULT_TOKEN_BUDGET

    return {
        "message_count": len(messages),

        "estimated_tokens": token_count,

        "recent_messages_budget": (
            budget.recent_messages_budget
        ),

        "within_recent_messages_budget": (
            token_count
            <= budget.recent_messages_budget
        ),

        "remaining_recent_messages_budget": (
            budget.recent_messages_budget
            - token_count
        ),
    }


@router.post(
    "/recent-messages",
)
async def select_recent_messages(
    request: RecentMessageWindowRequest,
):
    """
    根据 Token Budget 选择最近历史消息。
    """

    counter = TokenCounter()

    window = RecentMessageWindow(
        token_counter=counter,
    )

    token_budget = (
        request.token_budget
        if request.token_budget is not None
        else DEFAULT_TOKEN_BUDGET.recent_messages_budget
    )

    messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in request.messages
    ]

    result = window.select(
        messages=messages,
        token_budget=token_budget,
    )

    return {
        "total_messages": len(messages),

        "selected_message_count": len(
            result.selected_messages
        ),

        "dropped_message_count": (
            result.dropped_messages
        ),

        "token_budget": (
            result.budget
        ),

        "used_tokens": (
            result.used_tokens
        ),

        "remaining_tokens": (
            result.remaining_tokens
        ),

        "selected_messages": (
            result.selected_messages
        ),
    }