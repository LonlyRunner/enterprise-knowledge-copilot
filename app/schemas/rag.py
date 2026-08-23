from pydantic import BaseModel, Field
import uuid
from pydantic import BaseModel, Field

class RagIndexResponse(BaseModel):
    document: str
    chunks: int
    vector_count: int


class RagQueryRequest(BaseModel):

    knowledge_base_id: uuid.UUID

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class RagSource(BaseModel):
    content: str
    score: float
    source: str
    chunk_index: int


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[RagSource]

class RetrievalDebugRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class RetrievalDebugItem(BaseModel):
    rank: int
    score: float
    content: str
    source: str
    chunk_index: int


class RetrievalDebugResponse(BaseModel):
    query: str
    top_k: int
    results: list[RetrievalDebugItem]


class EvaluationCaseResponse(BaseModel):
    question: str
    hit: bool
    matched_rank: int | None


class RetrievalEvaluationResponse(BaseModel):
    total: int
    hits: int
    recall: float
    cases: list[EvaluationCaseResponse]

class RagIndexRequest(BaseModel):

    knowledge_base_id: uuid.UUID

    file_path: str = Field(
        ...,
        min_length=1,
    )


class RagExperimentConfig(BaseModel):
    chunk_size: int = Field(
        ...,
        ge=50,
        le=5000,
    )

    chunk_overlap: int = Field(
        ...,
        ge=0,
        le=1000,
    )

    top_k: int = Field(
        ...,
        ge=1,
        le=20,
    )


class RagExperimentRequest(BaseModel):
    document_path: str

    configs: list[RagExperimentConfig]


class RagExperimentResultResponse(BaseModel):
    chunk_size: int
    chunk_overlap: int
    top_k: int
    chunks: int
    hits: int
    total: int
    recall: float

class HybridRetrievalDebugRequest(BaseModel):
    knowledge_base_id: uuid.UUID
    question: str = Field(
        ...,
        min_length=1,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    candidate_k: int = Field(
        default=10,
        ge=1,
        le=100,
    )

class RerankDebugRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    candidate_k: int = Field(
        default=10,
        ge=1,
        le=20,
    )


class RagChatMessage(BaseModel):
    role: str = Field(
        ...,
        pattern="^(user|assistant)$",
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class RagChatRequest(
    BaseModel
):

    knowledge_base_id: uuid.UUID

    conversation_id: uuid.UUID

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class RagChatResponse(
    BaseModel
):

    conversation_id: uuid.UUID

    original_question: str

    rewritten_question: str

    answer: str

    sources: list[RagSource]


class VectorRetrievalDebugRequest(
    BaseModel
):

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

class TokenEstimateRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="需要进行 Token 估算的文本",
    )


class TokenEstimateResponse(BaseModel):
    text: str
    token_count: int
    budget: dict[str, int]