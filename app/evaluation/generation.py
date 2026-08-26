from __future__ import annotations

import re

from app.evaluation.models import EvaluationCase, EvaluationObservation


def _terms(text: str) -> set[str]:
    words = {word.lower() for word in re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text or "")}
    # Character unigrams make the metric useful for Chinese answers without a
    # heavyweight tokenizer; Latin words remain whole tokens.
    compact = re.sub(r"\s+", "", text or "")
    words.update(compact[index:index + 2] for index in range(max(0, len(compact) - 1)))
    return {word for word in words if word not in {"的", "了", "是", "我", "有", "和"}}


class GenerationEvaluator:
    @staticmethod
    def keyword_match(answer: str, expected_answer: str = "", expected_keywords: list[str] | None = None) -> float:
        keywords = expected_keywords if expected_keywords is not None else (expected_answer.split() if expected_answer else [])
        if not keywords:
            return 1.0
        return sum(keyword.lower() in (answer or "").lower() for keyword in keywords) / len(keywords)

    @staticmethod
    def citation(case: EvaluationCase, observation: EvaluationObservation) -> float | None:
        if not case.answerable or not (case.relevant_chunk_ids or case.expected_chunk_keywords):
            return None
        if not observation.citations:
            return 0.0
        if not case.relevant_chunk_ids:
            return 1.0
        cited = {str(item.get("chunk_id")) for item in observation.citations if item.get("chunk_id") is not None}
        return float(bool(cited & set(case.relevant_chunk_ids)))

    @staticmethod
    def groundedness(case: EvaluationCase, observation: EvaluationObservation) -> float | None:
        if not case.answerable or not observation.context:
            return None
        answer_terms = _terms(observation.answer)
        context_terms = _terms(observation.context)
        return len(answer_terms & context_terms) / len(answer_terms) if answer_terms else 0.0

    @staticmethod
    def relevance(case: EvaluationCase, observation: EvaluationObservation) -> float:
        question_terms = _terms(case.question)
        answer_terms = _terms(observation.answer)
        if not question_terms:
            return 1.0
        return len(question_terms & answer_terms) / len(question_terms)
