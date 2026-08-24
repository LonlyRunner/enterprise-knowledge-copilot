from dataclasses import dataclass


@dataclass
class RequestMetrics:
    """
    AI Request Runtime Metrics
    """

    # Context
    summary_tokens: int = 0

    history_tokens: int = 0

    rag_context_tokens: int = 0

    question_tokens: int = 0


    # Prompt
    prompt_tokens: int = 0


    # Generation
    output_tokens: int = 0


    # Total
    total_tokens: int = 0


    # Latency ms

    retrieval_latency_ms: float = 0

    llm_latency_ms: float = 0

    total_latency_ms: float = 0


    # Cost

    input_cost: float = 0

    output_cost: float = 0

    total_cost: float = 0