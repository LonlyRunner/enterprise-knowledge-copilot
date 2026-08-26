from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.evaluation.models import UnifiedEvaluationReport


def report_to_json(report: UnifiedEvaluationReport, path: str | Path | None = None) -> str:
    content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2, default=str)
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content + "\n", encoding="utf-8")
    return content


def report_to_markdown(report: UnifiedEvaluationReport) -> str:
    gate = report.quality_gate
    lines = [
        "# C5 Evaluation Report", "", f"- Dataset: `{report.dataset}`",
        f"- Cases: {report.passed_cases}/{report.total_cases} passed",
        f"- Duration: {report.duration_ms:.1f} ms; cache hits: {report.cache_hits}",
        f"- Quality gate: {'PASS' if gate is None or gate.passed else 'FAIL'}", "",
        "## Unified Metrics", "", "| Metric | Score |", "| --- | ---: |",
    ]
    lines.extend(f"| `{name}` | {value:.3f} |" for name, value in sorted(report.metrics.items()))
    lines.extend(["", "## Case Results", "", "| Case | Category | Result | Cached |", "| --- | --- | --- | --- |"])
    lines.extend(f"| `{case.case_id}` | {case.category} | {'PASS' if case.passed else 'FAIL'} | {'yes' if case.cached else 'no'} |" for case in report.cases)
    if gate and gate.failures:
        lines.extend(["", "## Gate Failures", ""] + [f"- {failure}" for failure in gate.failures])
    return "\n".join(lines) + "\n"


@dataclass
class EvaluationReport:
    """Legacy five-field report retained for Project A callers."""

    recall_at_k: float
    precision_at_k: float
    mrr: float
    faithfulness: float
    relevance: float
