from pydantic import BaseModel


class AgentRoute(
    BaseModel
):

    agent: str

    reason: str