"""FastAPI application entry point for HCX-Patent."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    datasets_router,
    experiments_router,
    exports_router,
    figures_router,
    health_router,
    patents_router,
    taxonomy_router,
    explainability_router,
    uncertainty_router,
)
from app.config import get_settings
from app.core.database import init_db
from app.core.logging_config import setup_logging

logger = logging.getLogger("hcx_patent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for startup initialization and graceful shutdown."""
    settings = get_settings()
    setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
    logger.info("Starting %s v%s...", settings.APP_NAME, settings.VERSION)

    # Ensure required artifact directories exist
    for sub in ["checkpoints", "predictions", "metrics", "figures", "reports"]:
        (Path(settings.ARTIFACTS_DIR) / sub).mkdir(parents=True, exist_ok=True)

    # Initialize SQLite schema
    init_db()
    logger.info("Database initialized successfully.")

    yield

    logger.info("Shutting down %s...", settings.APP_NAME)


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Research-Grade Patent Classification, Explainability, Uncertainty, and Taxonomy Drift Platform",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api/v1
API_PREFIX = "/api/v1"
app.include_router(health_router, prefix=API_PREFIX)
app.include_router(datasets_router, prefix=API_PREFIX)
app.include_router(experiments_router, prefix=API_PREFIX)
app.include_router(patents_router, prefix=API_PREFIX)
app.include_router(taxonomy_router, prefix=API_PREFIX)
app.include_router(explainability_router, prefix=API_PREFIX)
app.include_router(uncertainty_router, prefix=API_PREFIX)
app.include_router(figures_router, prefix=API_PREFIX)
app.include_router(exports_router, prefix=API_PREFIX)


@app.get("/")
def root_redirect():
    """Root redirect to docs."""
    return {"message": "HCX-Patent API is running. Visit /docs for OpenAPI documentation."}
