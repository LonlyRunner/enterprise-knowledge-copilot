import pytest

from app.rag.service import RagService
from app.db.session import AsyncSessionLocal


@pytest.fixture
async def rag_service():

    async with AsyncSessionLocal() as session:

        service = RagService(
            session=session,
        )

        yield service