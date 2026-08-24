from dataclasses import dataclass
import uuid

from app.rag.evaluator import RagEvaluator
from app.rag.service import RagService
from app.rag.splitters.recursive import (
    RecursiveTextSplitter,
)


@dataclass
class ExperimentConfig:
    chunk_size: int
    chunk_overlap: int
    top_k: int


@dataclass
class ExperimentResult:
    chunk_size: int
    chunk_overlap: int
    top_k: int
    chunks: int
    hits: int
    total: int
    recall: float


class RagExperimentRunner:

    def __init__(
        self,
        rag_service: RagService,
    ):
        self.rag_service = rag_service

        self.evaluator = RagEvaluator(
            rag_service
        )

    async def run(
        self,
        document_path: str,
        dataset_path: str,
        knowledge_base_id: uuid.UUID,
        configs: list[ExperimentConfig],
    ) -> list[ExperimentResult]:

        results: list[
            ExperimentResult
        ] = []

        for config in configs:

            self.rag_service.splitter = (
                RecursiveTextSplitter(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                )
            )

            index_result = (
                await self.rag_service.index_document(
                    knowledge_base_id=knowledge_base_id,
                    file_path=document_path,
                )
            )

            evaluation = (
                await self.evaluator.evaluate_retrieval(
                    dataset_path=dataset_path,
                    knowledge_base_id=knowledge_base_id,
                    top_k=config.top_k,
                )
            )

            results.append(
                ExperimentResult(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    top_k=config.top_k,
                    chunks=index_result.chunks,
                    hits=evaluation.hits,
                    total=(
                        evaluation.answerable_total
                    ),
                    recall=round(
                        evaluation.recall,
                        4,
                    ),
                )
            )

        return results
