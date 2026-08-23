from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.rag import router as rag_router
from app.api.v1.endpoints.database import (
    router as database_router,
)

from app.api.v1.endpoints.knowledge_base import (
    router as knowledge_base_router,
)
from app.api.v1.endpoints.document import (
    router as document_router,
)
from app.api.v1.endpoints.conversation import (
    router as conversation_router,
)

from app.api.v1.endpoints import context

api_router = APIRouter()


api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    chat_router,
    tags=["Chat"],
)

api_router.include_router(
    rag_router,
    tags=["RAG"],
)

api_router.include_router(
    database_router,
    tags=["Database"],
)

api_router.include_router(
    knowledge_base_router,
    tags=["Knowledge Base"],
)

api_router.include_router(
    document_router,
    tags=["Documents"],
)

api_router.include_router(
    conversation_router,
    tags=["Conversations"],
)

api_router.include_router(
    context.router,
    prefix="/context",
    tags=["context"],
)