"""
Rota de health check
"""

from fastapi import APIRouter
from app.schemas.models import HealthResponse

router = APIRouter()


@router.get("/health", name="health_check")
async def health_check():
    """Verifica se o agente está ativo e saudável."""
    return {
        "status": "healthy",
        "service": "talp-compliance-agent",
        "version": "0.1.0",
    }


@router.get("/", name="root")
async def root():
    """Rota raiz da aplicação."""
    return {
        "message": "TALP Compliance Agent",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


# Router para a API v1
api_v1_router = APIRouter(prefix="/api/v1", tags=["health"])


@api_v1_router.get("/health")
async def health_check_v1():
    """Verifica se o agente está ativo e saudável (API v1)."""
    return HealthResponse(
        status="healthy",
        service="talp-compliance-agent",
        version="0.1.0",
    )
