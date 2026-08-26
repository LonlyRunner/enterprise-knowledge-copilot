from __future__ import annotations

import asyncio
import inspect
import time
from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import datetime, timezone

from app.evaluation.agent import AgentEvaluator
from app.evaluation.cache import CaseResultCache
from app.evaluation.generation import GenerationEvaluator
from app.evaluation.models import CaseEvaluationResult, EvaluationCase, EvaluationObservation, UnifiedEvaluationReport
from app.evaluation.quality_gate import QualityGate
from app.evaluation.retrieval import RetrievalEvaluator


class UnifiedEvaluationRunner:
    """Run all C5 dimensions against one normalized executor."""

    def __init__(self, executor: Callable, *, cache: CaseResultCache | None = None, use_cache: bool = True, max_concurrency: int = 4, retrieval_k: int = 5, executor_version: str = "default"):
        self.executor = executor
        self.cache = cache
        self.use_cache = use_cache
        self.max_concurrency = max(1, max_concurrency)
        self.retrieval_k = retrieval_k
        self.executor_version = executor_version

    async def run(self, cases: Iterable[EvaluationCase], *, dataset: str = "inline", quality_gate: QualityGate | None = None) -> UnifiedEvaluationReport:
        cases = list(cases)
        started_at = datetime.now(timezone.utc)
        started = time.perf_counter()
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def one(case: EvaluationCase) -> CaseEvaluationResult:
            cached = False
            observation = None
            key = self.cache.key(case, executor_version=self.executor_version) if self.cache else None
            if self.use_cache and self.cache and key:
                observation = self.cache.get(key)
                cached = observation is not None
            if observation is None:
                try:
                    async with semaphore:
                        value = self.executor(case)
                        value = await value if inspect.isawaitable(value) else value
                    observation = value if isinstance(value, EvaluationObservation) else EvaluationObservation.from_dict(value or {})
                except Exception as exc:
                    observation = EvaluationObservation(error=f"{type(exc).__name__}: {exc}")
                if self.cache and key and observation.error is None:
                    self.cache.set(key, observation)
            return self.evaluate_case(case, observation, cached=cached)

        results = await asyncio.gather(*(one(case) for case in cases))
        samples: dict[str, list[float]] = defaultdict(list)
        for result in results:
            for metric, value in result.metrics.items():
                samples[metric].append(value)
        metrics = {metric: sum(values) / len(values) for metric, values in samples.items()}
        report = UnifiedEvaluationReport(
            dataset=str(dataset), started_at=started_at.isoformat(), finished_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=(time.perf_counter() - started) * 1000, total_cases=len(results),
            passed_cases=sum(result.passed for result in results), failed_cases=sum(not result.passed for result in results),
            cache_hits=sum(result.cached for result in results), metrics=metrics, cases=results,
        )
        if quality_gate:
            report.quality_gate = quality_gate.evaluate(report)
        return report

    def evaluate_case(self, case: EvaluationCase, observation: EvaluationObservation, *, cached: bool = False) -> CaseEvaluationResult:
        metrics: dict[str, float] = {}
        checks: dict[str, bool] = {}
        if observation.error:
            return CaseEvaluationResult(case.id, case.category, False, metrics, checks, observation, cached, observation.error)

        for name, value in (("agent.routing", AgentEvaluator.routing(case, observation)), ("agent.tool_selection", AgentEvaluator.tool_selection(case, observation)), ("agent.tool_arguments", AgentEvaluator.tool_arguments(case, observation))):
            if value is not None:
                metrics[name] = value
                checks[name] = value >= 0.999

        retrieval = RetrievalEvaluator.evaluate(observation.retrieved_chunk_ids, case.relevant_chunk_ids, k=self.retrieval_k, retrieved_contents=observation.retrieved_contents, expected_keywords=case.expected_chunk_keywords)
        metrics.update(retrieval)
        checks.update({name: value >= 0.999 for name, value in retrieval.items() if name.endswith("hit_rate")})

        keywords = case.expected_answer_keywords or ([case.expected_answer] if case.expected_answer else [])
        if keywords:
            metrics["generation.keyword"] = GenerationEvaluator.keyword_match(observation.answer, case.expected_answer, keywords)
            checks["generation.keyword"] = metrics["generation.keyword"] >= 0.8
        for name, value, threshold in (("generation.citation", GenerationEvaluator.citation(case, observation), 0.999), ("generation.groundedness", GenerationEvaluator.groundedness(case, observation), 0.5)):
            if value is not None:
                metrics[name] = value
                checks[name] = value >= threshold
        if case.answerable:
            metrics["generation.relevance"] = GenerationEvaluator.relevance(case, observation)
            checks["generation.relevance"] = metrics["generation.relevance"] > 0.0
        return CaseEvaluationResult(case.id, case.category, all(checks.values()) if checks else True, metrics, checks, observation, cached)


class EvaluationRunner:
    """Backward-compatible facade for the original minimal runner."""

    def __init__(self, rag_service, retrieval_evaluator=None, generation_evaluator=None):
        self.rag_service = rag_service

    async def run(self, cases):
        results = []
        for case in cases:
            result = await self.rag_service.chat(question=case.question)
            answer = result.get("answer", "") if isinstance(result, dict) else str(result)
            results.append({"case_id": case.id, "answer": answer})
        return results
