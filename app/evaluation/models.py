from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvaluationCase:
    """One golden case shared by Agent, Retrieval and Generation evaluation."""

    id: str
    question: str
    expected_answer: str = ""
    relevant_chunk_ids: list[str] = field(default_factory=list)
    expected_answer_keywords: list[str] = field(default_factory=list)
    expected_chunk_keywords: list[str] = field(default_factory=list)
    expected_route: str | None = None
    expected_tools: list[str] = field(default_factory=list)
    expected_tool_arguments: dict[str, dict[str, Any]] = field(default_factory=dict)
    category: str = "general"
    answerable: bool = True
    request: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> "EvaluationCase":
        known = set(cls.__dataclass_fields__)
        values = {key: value for key, value in item.items() if key in known}
        extra = {key: value for key, value in item.items() if key not in known}
        values["metadata"] = {**extra, **values.get("metadata", {})}
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ObservedToolCall:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    success: bool = True

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> "ObservedToolCall":
        return cls(
            tool=str(item.get("tool") or item.get("name") or ""),
            arguments=dict(item.get("arguments") or item.get("args") or {}),
            success=bool(item.get("success", True)),
        )


@dataclass
class EvaluationObservation:
    """Normalized output produced by a live system or a replay fixture."""

    answer: str = ""
    route: str | None = None
    tool_calls: list[ObservedToolCall] = field(default_factory=list)
    retrieved_chunk_ids: list[str] = field(default_factory=list)
    retrieved_contents: list[str] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)
    context: str = ""
    latency_ms: float = 0.0
    error: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> "EvaluationObservation":
        sources = item.get("citations") or item.get("sources") or []
        chunk_ids = item.get("retrieved_chunk_ids") or [
            str(source.get("chunk_id"))
            for source in sources
            if source.get("chunk_id") is not None
        ]
        contents = item.get("retrieved_contents") or [
            str(source.get("content") or "") for source in sources
        ]
        return cls(
            answer=str(item.get("answer") or ""),
            route=item.get("route"),
            tool_calls=[ObservedToolCall.from_dict(call) for call in item.get("tool_calls", [])],
            retrieved_chunk_ids=list(chunk_ids),
            retrieved_contents=list(contents),
            citations=list(sources),
            context=str(item.get("context") or "\n".join(contents)),
            latency_ms=float(item.get("latency_ms") or 0.0),
            error=item.get("error"),
            raw=dict(item),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaseEvaluationResult:
    case_id: str
    category: str
    passed: bool
    metrics: dict[str, float]
    checks: dict[str, bool]
    observation: EvaluationObservation
    cached: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QualityGateResult:
    passed: bool
    failures: list[str] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UnifiedEvaluationReport:
    dataset: str
    started_at: str
    finished_at: str
    duration_ms: float
    total_cases: int
    passed_cases: int
    failed_cases: int
    cache_hits: int
    metrics: dict[str, float]
    cases: list[CaseEvaluationResult]
    quality_gate: QualityGateResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
