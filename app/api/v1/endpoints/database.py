from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import AsyncSessionLocal


router = APIRouter()


@router.get("/database/health")
async def database_health():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "postgresql",
            "result": result.scalar_one(),
        }
