from pathlib import Path

from app.rag.loaders.base import (
    BaseDocumentLoader,
)
from app.rag.loaders.docx_loader import (
    DocxDocumentLoader,
)
from app.rag.loaders.markdown_loader import (
    MarkdownDocumentLoader,
)
from app.rag.loaders.pdf_loader import (
    PdfDocumentLoader,
)
from app.rag.loaders.text_loader import (
    TextDocumentLoader,
)


def create_document_loader(
    file_path: str,
) -> BaseDocumentLoader:

    suffix = (
        Path(file_path)
        .suffix
        .lower()
    )

    loaders = {
        ".txt": TextDocumentLoader,
        ".md": MarkdownDocumentLoader,
        ".markdown": MarkdownDocumentLoader,
        ".docx": DocxDocumentLoader,
        ".pdf": PdfDocumentLoader,
    }

    loader_class = loaders.get(
        suffix
    )

    if loader_class is None:
        raise ValueError(
            f"Unsupported document type: {suffix}"
        )

    return loader_class()