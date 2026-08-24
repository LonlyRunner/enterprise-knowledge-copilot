from dataclasses import dataclass, field


@dataclass
class Document:

    content: str

    metadata: dict = field(
        default_factory=dict
    )

@dataclass
class DocumentChunk:

    id: str

    document_id: str

    chunk_index: int

    content: str

    metadata: dict = field(
        default_factory=dict
    )


@dataclass
class VectorDocument:

    chunk: DocumentChunk

    embedding: list[float]


@dataclass
class SearchResult:

    chunk: DocumentChunk

    score: float