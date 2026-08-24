from dataclasses import dataclass


@dataclass
class RequestMetrics:

    trace_id: str


    # Context

    summary_tokens: int = 0

    history_tokens: int = 0

    rag_context_tokens: int = 0

    question_tokens: int = 0


    # Prompt

    prompt_tokens: int = 0


    # LLM

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0


    model: str = ""


    # Latency

    retrieval_latency_ms: float = 0

    llm_latency_ms: float = 0

    total_latency_ms: float = 0


    # Retrieval Quality

    selected_chunk_count: int = 0

    average_rerank_score: float = 0


    # Degradation

    degradation_attempts: int = 0


    # Cost

    input_cost: float = 0

    output_cost: float = 0

    total_cost: float = 0