from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router
from app.catalog.importer import load_catalog_artifact, load_catalog_from_sql
from app.classifier.events import JsonlEventLogger
from app.classifier.service import RootCategoryClassifier
from app.core.config import get_settings
from app.search.semantic import (
    BaseSemanticRetriever,
    RemoteSemanticRetriever,
    SemanticUnavailable,
    SentenceTransformerRetriever,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.event_logger = JsonlEventLogger(settings.event_log_path)
    app.state.classifier = None

    catalog = None
    candidates = []
    if settings.catalog_artifact:
        candidates.append(Path(settings.catalog_artifact))
        candidates.append(Path(__file__).resolve().parent.parent / settings.catalog_artifact)
    candidates.append(Path(__file__).resolve().parent.parent / "storage" / "catalog" / "catalog.json")
    candidates.append(Path("storage") / "catalog" / "catalog.json")

    for candidate in candidates:
        if candidate.exists():
            try:
                catalog = load_catalog_artifact(str(candidate))
                logger.info("Successfully loaded catalog artifact from: %s", candidate)
                break
            except Exception as exc:
                logger.warning("Failed loading catalog candidate %s: %s", candidate, exc)

    if catalog is None and settings.catalog_source:
        source_path = Path(settings.catalog_source)
        if not source_path.is_absolute():
            source_path = Path(__file__).resolve().parent.parent / source_path
        if source_path.exists():
            catalog = load_catalog_from_sql(
                source_path,
                version=settings.catalog_version,
            )

    if catalog is not None:
        semantic = _build_semantic(settings, catalog)
        app.state.classifier = RootCategoryClassifier(
            catalog,
            semantic_retriever=semantic,
            input_validation_enabled=settings.input_validation_enabled,
        )
    yield
    app.state.classifier = None


def _build_semantic(settings, catalog):
    if settings.semantic_remote_url:
        logger.info("Using Remote Semantic AI Engine via Colab: %s", settings.semantic_remote_url)
        return RemoteSemanticRetriever(settings.semantic_remote_url)
    if not settings.enable_semantic:
        return BaseSemanticRetriever()
    try:
        return SentenceTransformerRetriever(
            catalog,
            model_name=settings.semantic_model_name,
        )
    except SemanticUnavailable as exc:
        logger.warning("Semantic search is unavailable: %s", exc)
        return BaseSemanticRetriever()
    except Exception:
        logger.exception("Semantic search failed to initialise; falling back to exact/fuzzy")
        return BaseSemanticRetriever()


app = FastAPI(
    title="Dandan Root Category Classifier",
    version="0.1.0",
    lifespan=lifespan,
)

# Only the local prototype and explicitly configured review URLs may call the
# unauthenticated demo endpoint from a browser. The production API remains
# protected by its API key.
_cors_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:52345",
        "http://127.0.0.1:52345",
        *_cors_settings.demo_allowed_origins,
    ],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(detail),
                "details": {},
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid classification request",
                "details": {"errors": exc.errors()},
            }
        },
    )


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    return response


app.include_router(router)
