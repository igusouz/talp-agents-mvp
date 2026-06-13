from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.config.settings import load_settings
from app.graph import build_agent
from app.schemas.models import FinalOutput

router = APIRouter(prefix="/api/v1/invest", tags=["invest"])


class InvestAnalyzeRequest(BaseModel):
    user_story_text: str = Field(min_length=1, max_length=10000)

    @field_validator("user_story_text")
    @classmethod
    def story_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("user_story_text must not be blank")
        return cleaned


@lru_cache(maxsize=1)
def get_agent():
    settings = load_settings()
    return build_agent(backend=settings.backend)


@router.post("/analyze", response_model=FinalOutput)
def analyze_story(payload: InvestAnalyzeRequest) -> FinalOutput:
    try:
        agent = get_agent()
        return agent.run(payload.user_story_text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
