from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.evaluation.models import QualityGateResult, UnifiedEvaluationReport


DEFAULT_THRESHOLDS: dict[str, float] = {
    "agent.routing": 0.95,
    "agent.tool_selection": 0.95,
    "agent.tool_arguments": 0.95,
    "retrieval.hit_rate": 0.80,
    "retrieval.recall_at_k": 0.70,
    "retrieval.mrr": 0.60,
    "generation.keyword": 0.80,
    "generation.citation": 0.80,
    "generation.groundedness": 0.70,
    "generation.relevance": 0.60,
}


class QualityGate:
    def __init__(self, thresholds: dict[str, float] | None = None):
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    @classmethod
    def from_file(cls, path: str | Path | None) -> "QualityGate":
        if not path:
            return cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        thresholds = data.get("thresholds", data) if isinstance(data, dict) else {}
        return cls({str(key): float(value) for key, value in thresholds.items()})

    def evaluate(self, report: UnifiedEvaluationReport) -> QualityGateResult:
        failures = []
        for metric, threshold in self.thresholds.items():
            if metric not in report.metrics:
                continue  # metric is not applicable to this dataset
            actual = report.metrics[metric]
            if actual < threshold:
                failures.append(f"{metric}={actual:.3f} < {threshold:.3f}")
        return QualityGateResult(passed=not failures, failures=failures, thresholds=self.thresholds)
