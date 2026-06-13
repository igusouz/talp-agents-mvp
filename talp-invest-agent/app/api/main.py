from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.invest import router as invest_router

app = FastAPI(
    title="TALP Invest Agent API",
    version="0.1.0",
    description="REST API wrapper for the INVEST analysis workflow.",
)
app.include_router(invest_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "talp-invest-agent",
        "version": "0.1.0",
    }
