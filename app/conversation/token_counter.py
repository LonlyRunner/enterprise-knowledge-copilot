from __future__ import annotations


class TokenCounter:
    """
    TokenCounter（Token 计数器）

    当前阶段使用近似 Token 计算。

    后续可以替换为：
    - DeepSeek Tokenizer
    - Qwen Tokenizer
    - tiktoken
    - Provider 官方 Tokenizer
    """

    DEFAULT_CHARS_PER_TOKEN = 3.0

    def __init__(
        self,
        chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
    ):
        if chars_per_token <= 0:
            raise ValueError(
                "chars_per_token must be greater than 0"
            )

        self.chars_per_token = chars_per_token

    def count_text(
        self,
        text: str | None,
    ) -> int:
        if not text:
            return 0

        estimated_tokens = int(
            len(text) / self.chars_per_token
        )

        return max(
            1,
            estimated_tokens,
        )

    def count_message(
        self,
        role: str,
        content: str,
    ) -> int:
        """
        单条 Chat Message 的近似 Token 数。
        """

        message_overhead = 4

        return (
            self.count_text(role)
            + self.count_text(content)
            + message_overhead
        )

    def count_messages(
        self,
        messages: list[dict[str, str]],
    ) -> int:
        total = 0

        for message in messages:
            total += self.count_message(
                role=message.get(
                    "role",
                    "user",
                ),
                content=message.get(
                    "content",
                    "",
                ),
            )

        return total