from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.workflows import router as workflows_router
from app.clients.factory import create_agent_registry, create_http_client
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.workflow_service import WorkflowService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    http_client = create_http_client(settings)
    registry = create_agent_registry(http_client=http_client, settings=settings)
    app.state.workflow_service = WorkflowService(registry)
    app.state.http_client = http_client

    yield

    await http_client.aclose()


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(workflows_router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
