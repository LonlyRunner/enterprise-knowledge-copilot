from app.rag.models import DocumentChunk


class TextSplitter:

    def __init__(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 50,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(
        self,
        text: str,
        source: str = "unknown",
        *,
        tenant_id: str = "default",
        document_id: str = "",
    ) -> list[DocumentChunk]:

        text = text.strip()

        if not text:
            return []

        chunks: list[DocumentChunk] = []

        start = 0
        index = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        id=f"{source}-{index}",
                        tenant_id=tenant_id,
                        document_id=document_id,
                        chunk_index=index,
                        content=chunk_text,
                        metadata={
                            "source": source,
                            "chunk_index": index,
                            "start": start,
                            "end": min(end, len(text)),
                        },
                    )
                )

            if end >= len(text):
                break

            start += self.chunk_size - self.chunk_overlap
            index += 1

        return chunks
