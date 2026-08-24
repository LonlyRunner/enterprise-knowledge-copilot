from dataclasses import dataclass


@dataclass
class ContextMetrics:
    """
    Context Pipeline Runtime Metrics
    """

    summary_tokens: int

    history_tokens: int

    rag_context_tokens: int

    question_tokens: int

    prompt_tokens: int = 0

    degradation_attempts: int = 0

    selected_history_count: int = 0

    selected_chunk_count: int = 0