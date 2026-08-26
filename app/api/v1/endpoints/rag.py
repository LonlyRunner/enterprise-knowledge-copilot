
import uuid

from fastapi import APIRouter, Depends

from app.rag.evaluator import RagEvaluator
from app.rag.experiment import ExperimentConfig, RagExperimentRunner
from app.rag.service import RagService
from app.schemas.rag import (
    HybridRetrievalDebugRequest,
    RagChatRequest,
    RagChatResponse,
    RagExperimentRequest,
    RagIndexRequest,
    RagIndexResponse,
    RagQueryRequest,
    RagQueryResponse,
    RerankDebugRequest,
    TokenEstimateRequest,
    TokenEstimateResponse,
    VectorRetrievalDebugRequest,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.dependencies import (
    get_db,
)
from app.auth.rbac import require_permission
from app.auth.models import User
from app.cache.semantic import SemanticCache

from app.rag.context import TokenBudget, TokenCounter
router = APIRouter(dependencies=[Depends(require_permission("chat:use"))])

@router.post(
    "/rag/index",
    response_model=RagIndexResponse,
)
async def index_document(
    request: RagIndexRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    cache = SemanticCache()
    try:
        response = await rag_service.index_document(
            knowledge_base_id=request.knowledge_base_id,
            file_path=request.file_path,
        )
        await cache.invalidate_knowledge_base(str(request.knowledge_base_id))
        return response
    finally:
        await cache.close()
        await rag_service.close()


@router.post(
    "/rag/query",
    response_model=RagQueryResponse,
)
async def query_rag(
    request: RagQueryRequest,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("chat:use")),
):

    rag_service = RagService(
        session=db
    )

    cache = SemanticCache()
    try:
        cached = await cache.get(str(request.knowledge_base_id), request.question, request.top_k)
        if cached is not None:
            return cached
        response = await rag_service.query(
            knowledge_base_id=request.knowledge_base_id,
            question=request.question,
            top_k=request.top_k,
            tenant_id=user.tenant_id,
        )
        payload = response.model_dump(mode="json")
        await cache.set(str(request.knowledge_base_id), request.question, request.top_k, payload)
        return payload
    finally:
        await cache.close()
        await rag_service.close()

@router.post(
    "/rag/evaluation/retrieval",
)
async def evaluate_retrieval(
    knowledge_base_id: uuid.UUID,
    top_k: int = 3,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    evaluator = RagEvaluator(
        rag_service
    )

    result = (
        await evaluator.evaluate_retrieval(
            dataset_path=(
                "data/evaluation.json"
            ),
            knowledge_base_id=knowledge_base_id,
            top_k=top_k,
        )
    )

    return {
        "total": result.total,
        "hits": result.hits,
        "recall": round(
            result.recall,
            4,
        ),
        "cases": [
            {
                "question": (
                    case.question
                ),
                "hit": case.hit,
                "matched_rank": (
                    case.matched_rank
                ),
            }
            for case
            in result.cases
        ],
    }




@router.post(
    "/rag/evaluation/experiments",
)
async def run_rag_experiments(
    request: RagExperimentRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    experiment_runner = (
        RagExperimentRunner(
            rag_service
        )
    )

    configs = [
        ExperimentConfig(
            chunk_size=item.chunk_size,
            chunk_overlap=item.chunk_overlap,
            top_k=item.top_k,
        )
        for item in request.configs
    ]

    results = (
        await experiment_runner.run(
            document_path=request.document_path,
            dataset_path=(
                "data/evaluation.json"
            ),
            knowledge_base_id=request.knowledge_base_id,
            configs=configs,
        )
    )

    return [
        {
            "chunk_size": item.chunk_size,
            "chunk_overlap": (
                item.chunk_overlap
            ),
            "top_k": item.top_k,
            "chunks": item.chunks,
            "hits": item.hits,
            "total": item.total,
            "recall": item.recall,
        }
        for item in results
    ]

@router.post(
    "/rag/retrieval/hybrid/debug",
)
async def hybrid_retrieval_debug(
    request: HybridRetrievalDebugRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    return await rag_service.retrieve_hybrid(
        knowledge_base_id=(
            request.knowledge_base_id
        ),
        question=request.question,
        top_k=request.top_k,
        candidate_k=request.candidate_k,
    )

@router.post(
    "/rag/evaluation/hybrid",
)
async def evaluate_hybrid(
    knowledge_base_id: uuid.UUID,
    top_k: int = 3,
    candidate_k: int = 10,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    evaluator = RagEvaluator(
        rag_service
    )

    return await evaluator.evaluate_hybrid_retrieval(
        dataset_path=(
            "data/evaluation.json"
        ),
        knowledge_base_id=knowledge_base_id,
        top_k=top_k,
        candidate_k=candidate_k,
    )

@router.post(
    "/rag/retrieval/rerank/debug",
)
async def rerank_debug(
    request: RerankDebugRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    return await rag_service.retrieve_with_rerank(
        knowledge_base_id=request.knowledge_base_id,
        question=request.question,
        top_k=request.top_k,
        candidate_k=request.candidate_k,
    )


@router.post(
    "/rag/chat",
    response_model=RagChatResponse,
)
async def rag_chat(
    request: RagChatRequest,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("chat:use")),
):

    rag_service = (
        RagService(
            session=db
        )
    )

    try:
        return await rag_service.chat(
            knowledge_base_id=request.knowledge_base_id,
            conversation_id=request.conversation_id,
            question=request.question,
            top_k=request.top_k,
        )
    finally:
        await rag_service.close()


@router.post(
    "/rag/retrieval/vector/debug",
)
async def vector_retrieval_debug(
    request: VectorRetrievalDebugRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    return await rag_service.retrieve_vector(
        question=request.question,
        top_k=request.top_k,
        knowledge_base_id=request.knowledge_base_id,
    )

@router.post(
    "/token-estimate",
    response_model=TokenEstimateResponse,
)
async def estimate_tokens(
    request: TokenEstimateRequest,
) -> TokenEstimateResponse:
    counter = TokenCounter()
    budget = TokenBudget()

    token_count = counter.count_text(request.text)

    return TokenEstimateResponse(
        text=request.text,
        token_count=token_count,
        budget=budget.as_dict(),
    )
