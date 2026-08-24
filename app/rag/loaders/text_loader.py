from pathlib import Path

from app.rag.loaders.base import BaseDocumentLoader
from app.rag.models import Document


class TextDocumentLoader(BaseDocumentLoader):

    def load(
        self,
        file_path: str,
        *,
        document_id: str | None = None,
        tenant_id: str = "default",
    ) -> Document:

        path = Path(file_path)

        text = path.read_text(
            encoding="utf-8"
        )

        return Document(
            id=document_id or path.stem,
            tenant_id=tenant_id,
            content=text,
            metadata={
                "source": path.name,
                "file_type": "txt",
                "path": str(path),
            },
        )
