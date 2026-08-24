from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.db import init_database
from app.db.session import engine


settings = get_settings()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    await init_database()

    yield

    await engine.dispose()


def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"code": "BAD_REQUEST", "message": str(exc)})

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        return JSONResponse(status_code=404, content={"code": "NOT_FOUND", "message": str(exc)})

    app.include_router(
        api_router,
        prefix="/api/v1",
    )

    return app


app = create_app()
