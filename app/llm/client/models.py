from dataclasses import dataclass


@dataclass
class LLMResponse:

    content: str

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    model: str = ""