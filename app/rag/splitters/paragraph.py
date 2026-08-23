import re


class ParagraphSplitter:

    def split(
        self,
        text: str,
    ) -> list[str]:

        text = text.replace(
            "\r\n",
            "\n",
        )

        paragraphs = re.split(
            r"\n\s*\n",
            text,
        )

        return [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]