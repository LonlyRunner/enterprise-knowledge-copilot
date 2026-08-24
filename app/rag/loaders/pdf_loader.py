from pathlib import Path

from pypdf import PdfReader

from app.rag.loaders.base import BaseDocumentLoader
from app.rag.models import Document


class PdfDocumentLoader(
    BaseDocumentLoader
):

    def load(
        self,
        file_path: str,
        *,
        document_id: str | None = None,
        tenant_id: str = "default",
    ) -> Document:

        path = Path(file_path)

        reader = PdfReader(
            file_path
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):

            text = (
                page.extract_text()
                or ""
            )

            text = text.strip()

            if not text:
                continue

            pages.append(
                (
                    f"[PAGE {page_number}]\n"
                    f"{text}"
                )
            )

        content = "\n\n".join(
            pages
        )

        return Document(
            id=document_id or path.stem,
            tenant_id=tenant_id,
            content=content,
            metadata={
                "source": path.name,
                "file_type": "pdf",
                "path": str(path),
                "page_count": len(
                    reader.pages
                ),
            },
        )
