from contextlib import asynccontextmanager
import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.db import init_database
from app.db.session import engine
from app.observability import setup_opentelemetry
from app.cache.semantic import close_cache_redis
from app.api.v1.endpoints.chat import close_llm_client


settings = get_settings()
logger = logging.getLogger(__name__)

HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
HTTP_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "path"])


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    await init_database()

    yield

    await close_cache_redis()
    await close_llm_client()
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

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled API error: %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误，请查看后端日志",
            },
        )

    app.include_router(
        api_router,
        prefix="/api/v1",
    )

    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        path = request.url.path if request.url.path != "/metrics" else "/metrics"
        HTTP_REQUESTS.labels(request.method, path, str(response.status_code)).inc()
        HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - started)
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        from starlette.responses import Response
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    setup_opentelemetry(app)

    frontend_directory = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_directory.is_dir():
        app.mount(
            "/ui",
            StaticFiles(directory=frontend_directory, html=True),
            name="frontend",
        )

    return app


app = create_app()
