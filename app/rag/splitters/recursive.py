from app.rag.models import (
    Document,
    DocumentChunk,
)
from app.rag.splitters.paragraph import (
    ParagraphSplitter,
)


class RecursiveTextSplitter:

    def __init__(
        self,
        chunk_size: int = 400,
        chunk_overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be positive"
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.paragraph_splitter = (
            ParagraphSplitter()
        )

    def split_document(
        self,
        document: Document,
    ) -> list[DocumentChunk]:

        paragraphs = (
            self.paragraph_splitter.split(
                document.content
            )
        )

        raw_chunks = (
            self._merge_paragraphs(
                paragraphs
            )
        )

        chunks = []

        for index, content in enumerate(
            raw_chunks
        ):

            metadata = {
                **document.metadata,
                "chunk_index": index,
            }

            chunks.append(
                DocumentChunk(
                    id=(
                        f"{document.metadata.get('source', 'document')}"
                        f"-{index}"
                    ),
                    tenant_id=document.tenant_id,
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    metadata=metadata,
                )
            )

        return chunks

    def _merge_paragraphs(
        self,
        paragraphs: list[str],
    ) -> list[str]:

        chunks = []

        current_parts = []
        current_length = 0

        for paragraph in paragraphs:

            paragraph_length = len(
                paragraph
            )

            if (
                current_parts
                and current_length
                + paragraph_length
                + 2
                > self.chunk_size
            ):

                current_chunk = (
                    "\n\n".join(
                        current_parts
                    )
                )

                chunks.append(
                    current_chunk
                )

                overlap_text = (
                    self._create_overlap(
                        current_chunk
                    )
                )

                current_parts = (
                    [overlap_text]
                    if overlap_text
                    else []
                )

                current_length = len(
                    overlap_text
                )

            current_parts.append(
                paragraph
            )

            current_length += (
                paragraph_length
                + 2
            )

        if current_parts:

            chunks.append(
                "\n\n".join(
                    current_parts
                )
            )

        return chunks

    def _create_overlap(
        self,
        text: str,
    ) -> str:

        if not text:
            return ""

        if (
            len(text)
            <= self.chunk_overlap
        ):
            return text

        return text[
            -self.chunk_overlap:
        ].strip()
