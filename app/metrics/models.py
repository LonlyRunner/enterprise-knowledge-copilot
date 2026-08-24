from dataclasses import dataclass


@dataclass
class RequestMetrics:

    trace_id: str


    # Context Token
    summary_tokens: int

    history_tokens: int

    rag_context_tokens: int

    question_tokens: int


    # LLM Token
    input_tokens: int

    output_tokens: int

    total_tokens: int


    # Model
    model: str


    # Performance
    llm_latency_ms: float

    retrieval_latency_ms: float = 0


    # RAG
    selected_chunk_count: int = 0

    degradation_attempts: int = 0


    # Cost
    total_cost: float = 0