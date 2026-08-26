from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from app.evaluation.models import EvaluationCase, EvaluationObservation


class ReplayExecutor:
    """Executor for checked-in JSON observations used by CI and offline runs."""

    version = "replay-v1"

    def __init__(self, results: dict[str, Any]):
        self.results = results

    @classmethod
    def from_file(cls, path: str) -> "ReplayExecutor":
        import json
        from pathlib import Path

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and "results" in data:
            items = data["results"]
        elif isinstance(data, dict) and "cases" in data:
            items = data["cases"]
        else:
            items = data
        if isinstance(items, list):
            results = {
                str(item["case_id"]): (item.get("observation", item))
                for item in items
                if "case_id" in item
            }
        elif isinstance(data, dict) and isinstance(data.get("cases"), list):
            results = {
                str(item["case_id"]): item.get("observation", item)
                for item in data["cases"]
                if "case_id" in item
            }
        else:
            results = dict(items)
        return cls(results)

    async def __call__(self, case: EvaluationCase) -> EvaluationObservation:
        item = self.results.get(case.id)
        if item is None:
            return EvaluationObservation(error=f"missing replay result for case {case.id}")
        return EvaluationObservation.from_dict(item)


class HttpGatewayExecutor:
    """Live adapter for a running Project C Gateway."""

    version = "http-gateway-v1"

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def __call__(self, case: EvaluationCase) -> EvaluationObservation:
        payload = {"question": case.question, **case.request}
        mode = payload.get("mode") or case.expected_route or "auto"
        endpoint = "/ai/agent" if mode == "agent" else "/ai/chat"
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}{endpoint}", json=payload)
                response.raise_for_status()
                data = response.json()
            observation = EvaluationObservation.from_dict(data)
            observation.latency_ms = (time.perf_counter() - started) * 1000
            return observation
        except Exception as exc:
            return EvaluationObservation(error=f"{type(exc).__name__}: {exc}", latency_ms=(time.perf_counter() - started) * 1000)


Executor = Callable[[EvaluationCase], Awaitable[EvaluationObservation | dict[str, Any]]]
