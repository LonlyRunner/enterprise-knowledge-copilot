import json

import pytest

from app.evaluation.cache import CaseResultCache
from app.evaluation.dataset import EvaluationDataset
from app.evaluation.executors import ReplayExecutor
from app.evaluation.quality_gate import QualityGate
from app.evaluation.runner import UnifiedEvaluationRunner


@pytest.mark.asyncio
async def test_unified_runner_evaluates_all_dimensions_and_reuses_case_cache(tmp_path):
    dataset = EvaluationDataset().load("data/evaluation/c5_cases.json")
    executor = ReplayExecutor.from_file("data/evaluation/c5_results.json")
    runner = UnifiedEvaluationRunner(
        executor,
        cache=CaseResultCache(tmp_path),
        executor_version=executor.version,
    )
    first = await runner.run(dataset, quality_gate=QualityGate.from_file("data/evaluation/quality_gate.json"))
    second = await runner.run(dataset, quality_gate=QualityGate.from_file("data/evaluation/quality_gate.json"))
    assert first.quality_gate and first.quality_gate.passed
    assert first.passed_cases == 4
    assert {"agent.routing", "retrieval.recall_at_k", "generation.citation"} <= set(first.metrics)
    assert second.cache_hits == 4


def test_dataset_supports_legacy_and_extended_shapes(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([
        {"id": "legacy", "question": "q", "expected_answer": "a", "relevant_chunk_ids": ["c"]},
        {"id": "extended", "question": "q2", "expected_answer_keywords": ["a"], "expected_route": "agent", "owner": "c5"},
    ]), encoding="utf-8")
    cases = EvaluationDataset().load(path)
    assert cases[0].relevant_chunk_ids == ["c"]
    assert cases[1].expected_route == "agent"
    assert cases[1].metadata["owner"] == "c5"
