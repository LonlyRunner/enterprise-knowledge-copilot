from dataclasses import dataclass, field


@dataclass
class Document:
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class DocumentChunk:
    id: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class VectorDocument:
    chunk: DocumentChunk
    embedding: list[float]


@dataclass
class SearchResult:
    chunk: DocumentChunk
    score: float


@dataclass
class ContextDebugInfo:
    summary_tokens: int

    history_tokens: int

    rag_context_tokens: int

    question_tokens: int

    prompt_tokens: int

    degradation_attempts: int

    selected_history_count: int

    selected_chunk_count: int