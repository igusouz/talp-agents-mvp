"""
TALP Compliance Agent - Aplicação principal FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import catalog, compliance, compliance_runs, health
from app.db.init_db import init_db

app = FastAPI(
    title="TALP Compliance Agent API",
    description="Agente intermediário para análise de regras de negócio e compliance.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(health.api_v1_router, tags=["health"])
app.include_router(compliance.router)
app.include_router(compliance_runs.router)
app.include_router(catalog.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Inicializa recursos mínimos da aplicação."""
    init_db()
    print("TALP Compliance Agent iniciado")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Finaliza a aplicação."""
    print("TALP Compliance Agent desligado")