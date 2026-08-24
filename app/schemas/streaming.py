from typing import Literal

from pydantic import BaseModel


class StreamEvent(BaseModel):
    event: Literal[
        "start",
        "delta",
        "done",
        "error",
    ]
    data: str | None = None