import re


class SimpleTokenizer:

    def tokenize(
        self,
        text: str,
    ) -> list[str]:

        text = text.lower().strip()

        tokens = []

        # 英文单词、数字、编号
        english_and_numbers = re.findall(
            r"[a-z0-9_-]+",
            text,
        )

        tokens.extend(
            english_and_numbers
        )

        # 中文字符
        chinese_chars = re.findall(
            r"[\u4e00-\u9fff]",
            text,
        )

        tokens.extend(
            chinese_chars
        )

        return tokens