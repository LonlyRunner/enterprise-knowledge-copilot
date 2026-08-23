from collections.abc import Iterable

import tiktoken


class TokenCounter:
    """
    Token Counter

    当前使用 cl100k_base 进行近似 Token 统计。

    注意：
    DeepSeek 实际 Tokenizer 与 cl100k_base 并不完全一致，
    因此这里得到的是工程估算值，而不是模型供应商返回的精确值。
    """

    def __init__(self, encoding_name: str = "cl100k_base") -> None:
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_text(self, text: str | None) -> int:
        """
        统计单段文本 Token 数量。
        """
        if not text:
            return 0

        return len(
            self.encoding.encode(
                text,
                disallowed_special=(),
            )
        )

    def count_messages(
        self,
        messages: Iterable[dict[str, str]],
    ) -> int:
        """
        粗略统计 Chat Messages Token 数量。

        除正文 Token 外，为 role / message structure
        预留少量协议开销。
        """
        total = 0

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")

            # 每条消息预留结构性开销
            total += 4
            total += self.count_text(role)
            total += self.count_text(content)

        # Assistant reply 起始结构预留
        total += 2

        return total