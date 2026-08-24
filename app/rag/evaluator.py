import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from app.rag.service import RagService


@dataclass
class EvaluationCaseResult:
    case_id: str
    question: str
    category: str
    hit: bool
    matched_rank: int | None
    answerable: bool


@dataclass
class RetrievalEvaluationResult:
    total: int
    answerable_total: int
    hits: int
    recall: float
    cases: list[EvaluationCaseResult]


class RagEvaluator:

    def __init__(
        self,
        rag_service: RagService,
    ):
        self.rag_service = rag_service

    async def evaluate_retrieval(
        self,
        dataset_path: str,
        knowledge_base_id: uuid.UUID,
        top_k: int = 3,
    ) -> RetrievalEvaluationResult:

        path = Path(dataset_path)

        dataset = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        cases: list[EvaluationCaseResult] = []

        hits = 0
        answerable_total = 0

        for item in dataset:

            answerable = item.get(
                "answerable",
                True,
            )

            if not answerable:
                cases.append(
                    EvaluationCaseResult(
                        case_id=item["id"],
                        question=item["question"],
                        category=item.get(
                            "category",
                            "unknown",
                        ),
                        hit=True,
                        matched_rank=None,
                        answerable=False,
                    )
                )
                continue

            answerable_total += 1

            result = await self.rag_service.retrieve(
                knowledge_base_id=knowledge_base_id,
                question=item["question"],
                top_k=top_k,
            )

            expected_keywords = item[
                "expected_chunk_keywords"
            ]

            matched_rank = None

            for retrieved in result.results:

                content = retrieved.content

                if all(
                    keyword in content
                    for keyword
                    in expected_keywords
                ):
                    matched_rank = (
                        retrieved.rank
                    )
                    break

            hit = matched_rank is not None

            if hit:
                hits += 1

            cases.append(
                EvaluationCaseResult(
                    case_id=item["id"],
                    question=item["question"],
                    category=item.get(
                        "category",
                        "unknown",
                    ),
                    hit=hit,
                    matched_rank=matched_rank,
                    answerable=True,
                )
            )

        recall = (
            hits / answerable_total
            if answerable_total
            else 0.0
        )

        return RetrievalEvaluationResult(
            total=len(dataset),
            answerable_total=answerable_total,
            hits=hits,
            recall=recall,
            cases=cases,
        )

    async def evaluate_hybrid_retrieval(
            self,
            dataset_path: str,
            knowledge_base_id: uuid.UUID,
            top_k: int = 3,
            candidate_k: int = 10,
    ):

        path = Path(
            dataset_path
        )

        dataset = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        total = 0
        hits = 0
        cases = []

        for item in dataset:

            if not item.get(
                    "answerable",
                    True,
            ):
                continue

            total += 1

            results = (
                await self.rag_service.retrieve_hybrid(
                    knowledge_base_id=knowledge_base_id,
                    question=item["question"],
                    top_k=top_k,
                    candidate_k=candidate_k,
                )
            )

            expected_keywords = item[
                "expected_chunk_keywords"
            ]

            matched_rank = None

            for result in results:

                content = result[
                    "content"
                ]

                if all(
                        keyword in content
                        for keyword
                        in expected_keywords
                ):
                    matched_rank = result[
                        "rank"
                    ]
                    break

            hit = (
                    matched_rank
                    is not None
            )

            if hit:
                hits += 1

            cases.append(
                {
                    "id": item["id"],
                    "question": item[
                        "question"
                    ],
                    "hit": hit,
                    "matched_rank": (
                        matched_rank
                    ),
                }
            )

        recall = (
            hits / total
            if total
            else 0
        )

        return {
            "total": total,
            "hits": hits,
            "recall": round(
                recall,
                4,
            ),
            "cases": cases,
        }

