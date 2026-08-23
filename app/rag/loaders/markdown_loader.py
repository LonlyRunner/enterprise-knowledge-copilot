from pathlib import Path

from app.rag.loaders.base import BaseDocumentLoader
from app.rag.models import Document


class MarkdownDocumentLoader(
    BaseDocumentLoader
):

    def load(
        self,
        file_path: str,
    ) -> Document:

        path = Path(file_path)

        text = path.read_text(
            encoding="utf-8"
        )

        return Document(
            content=text,
            metadata={
                "source": path.name,
                "file_type": "markdown",
                "path": str(path),
            },
        )