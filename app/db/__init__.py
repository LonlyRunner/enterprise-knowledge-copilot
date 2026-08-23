from sqlalchemy import text

from app.db.session import engine


async def init_database():

    async with engine.begin() as connection:

        await connection.execute(
            text(
                "CREATE EXTENSION IF NOT EXISTS vector"
            )
        )