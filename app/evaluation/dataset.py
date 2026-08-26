from __future__ import annotations

import json
from pathlib import Path

from app.evaluation.models import EvaluationCase


class EvaluationDataset:
    def load(self, path: str | Path) -> list[EvaluationCase]:
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        items = data.get("cases", []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError("evaluation dataset must be a JSON array or an object containing 'cases'")
        cases = [EvaluationCase.from_dict(item) for item in items]
        self._validate(cases)
        return cases

    @staticmethod
    def _validate(cases: list[EvaluationCase]) -> None:
        seen: set[str] = set()
        for case in cases:
            if not case.id.strip() or not case.question.strip():
                raise ValueError("evaluation case id and question are required")
            if case.id in seen:
                raise ValueError(f"duplicate evaluation case id: {case.id}")
            seen.add(case.id)
