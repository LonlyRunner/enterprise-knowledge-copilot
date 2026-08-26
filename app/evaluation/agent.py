from __future__ import annotations

from typing import Any

from app.evaluation.models import EvaluationCase, EvaluationObservation


class AgentEvaluator:
    """Deterministic checks for routing, tool selection and tool arguments."""

    @staticmethod
    def routing(case: EvaluationCase, observation: EvaluationObservation) -> float | None:
        if not case.expected_route:
            return None
        return float(observation.route == case.expected_route)

    @staticmethod
    def tool_selection(case: EvaluationCase, observation: EvaluationObservation) -> float | None:
        if not case.expected_tools:
            return None
        expected = set(case.expected_tools)
        actual = {call.tool for call in observation.tool_calls}
        if not expected and not actual:
            return 1.0
        return 2 * len(expected & actual) / max(1, len(expected) + len(actual))

    @staticmethod
    def tool_arguments(case: EvaluationCase, observation: EvaluationObservation) -> float | None:
        if not case.expected_tool_arguments:
            return None
        checks: list[bool] = []
        for tool_name, expected in case.expected_tool_arguments.items():
            calls = [call for call in observation.tool_calls if call.tool == tool_name]
            checks.append(any(AgentEvaluator._contains(call.arguments, expected) for call in calls))
        return sum(checks) / len(checks) if checks else 1.0

    @staticmethod
    def success(expected: str, actual: str) -> bool:
        return expected in actual

    @staticmethod
    def _contains(actual: Any, expected: Any) -> bool:
        if isinstance(expected, dict):
            return isinstance(actual, dict) and all(
                key in actual and AgentEvaluator._contains(actual[key], value)
                for key, value in expected.items()
            )
        if isinstance(expected, list):
            return isinstance(actual, list) and all(any(AgentEvaluator._contains(item, wanted) for item in actual) for wanted in expected)
        return actual == expected
