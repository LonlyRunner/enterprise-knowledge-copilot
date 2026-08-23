
from app.rag.service import RagService
from app.rag.evaluator import RagEvaluator
from app.schemas.rag import (
    RagIndexRequest,
    RagIndexResponse,
    RagQueryRequest,
    RagQueryResponse,
    RetrievalDebugRequest,
    RetrievalDebugResponse,
)

from app.rag.experiment import (
    ExperimentConfig,
    RagExperimentRunner,
)

from app.schemas.rag import (
    RagExperimentRequest,
)

from app.schemas.rag import (
    RagIndexRequest,
)

from app.schemas.rag import (
    HybridRetrievalDebugRequest,
)

from app.schemas.rag import (
    RerankDebugRequest,
)

from app.schemas.rag import (
    RagChatRequest,
    RagChatResponse,
)

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.dependencies import (
    get_db,
)

from app.schemas.rag import (
    VectorRetrievalDebugRequest,
)

router = APIRouter()

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

    return await rag_service.index_document(
        knowledge_base_id=(
            request.knowledge_base_id
        ),
        file_path=request.file_path,
    )


@router.post(
    "/rag/query",
    response_model=RagQueryResponse,
)
async def query_rag(
    request: RagQueryRequest,

    db: AsyncSession = Depends(
        get_db
    ),
):

    rag_service = RagService(
        session=db
    )

    return await rag_service.query(
        knowledge_base_id=(
            request.knowledge_base_id
        ),
        question=request.question,
        top_k=request.top_k,
    )

@router.post(
    "/rag/evaluation/retrieval",
)
async def evaluate_retrieval(
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
):

    rag_service = (
        RagService(
            session=db
        )
    )

    return await rag_service.chat(
        knowledge_base_id=(
            request.knowledge_base_id
        ),
        conversation_id=(
            request.conversation_id
        ),
        question=(
            request.question
        ),
        top_k=request.top_k,
    )


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
    )