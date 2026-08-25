from typing import TypedDict


class MultiAgentState(
    TypedDict
):

    question: str


    next_agent: str | None


    answer: str | None


    history: list