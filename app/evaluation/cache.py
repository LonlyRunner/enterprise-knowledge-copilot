from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from app.evaluation.models import EvaluationCase, EvaluationObservation


class CaseResultCache:
    """Small content-addressed cache for deterministic per-case observations."""

    VERSION = "c5-v1"

    def __init__(self, directory: str | Path = "storage/evaluation/cache"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def key(self, case: EvaluationCase, *, executor_version: str = "default") -> str:
        payload = {"version": self.VERSION, "executor": executor_version, "case": case.to_dict()}
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        return digest

    def get(self, key: str) -> EvaluationObservation | None:
        path = self.directory / f"{key}.json"
        try:
            return EvaluationObservation.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
            return None

    def set(self, key: str, observation: EvaluationObservation) -> None:
        path = self.directory / f"{key}.json"
        temporary = path.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(observation.to_dict(), ensure_ascii=False, default=str), encoding="utf-8")
        temporary.replace(path)

    def clear(self) -> int:
        count = 0
        for path in self.directory.glob("*.json"):
            try:
                path.unlink()
                count += 1
            except OSError:
                continue
        return count
