from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import AsyncSessionLocal

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.dependencies import get_db
from app.repositories.document import (
    DocumentRepository,
)
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)

from app.models.document_chunk import (
    EMBEDDING_DIMENSION,
)

router = APIRouter()


@router.get("/database/health")
async def database_health():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            text("SELECT 1")
        )

        value = result.scalar_one()

    return {
        "status": "ok",
        "database": "postgresql",
        "result": value,
    }

@router.post(
    "/database/test-document"
)
async def test_document(
    db: AsyncSession = Depends(
        get_db
    ),
):

    document_repository = (
        DocumentRepository(
            db
        )
    )

    chunk_repository = (
        DocumentChunkRepository(
            db
        )
    )

    try:

        document = (
            await document_repository.create(
                name="test.txt",
                file_type="txt",
                source_path=(
                    "data/test.txt"
                ),
                status="processing",
            )
        )

        test_embedding = [
            0.01
            for _ in range(
                EMBEDDING_DIMENSION
            )
        ]

        chunks = (
            await chunk_repository.create_many(
                document_id=document.id,
                chunks=[
                    {
                        "chunk_index": 0,
                        "content": (
                            "这是第一段测试文本"
                        ),
                        "embedding": (
                            test_embedding
                        ),
                    },
                    {
                        "chunk_index": 1,
                        "content": (
                            "这是第二段测试文本"
                        ),
                        "embedding": (
                            test_embedding
                        ),
                    },
                ],
            )
        )

        await document_repository.update_status(
            document,
            "completed",
        )

        await db.commit()

        return {
            "document_id": str(
                document.id
            ),
            "status": (
                document.status
            ),
            "chunks": len(
                chunks
            ),
        }

    except Exception:

        await db.rollback()

        raise