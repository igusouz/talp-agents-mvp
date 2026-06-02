"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.qa import router as qa_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Structured BDD QA analysis agent built with LangChain and FastAPI.",
)
app.include_router(qa_router, prefix=settings.api_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a minimal health response."""

    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
