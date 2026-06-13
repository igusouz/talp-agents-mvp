# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    TALP_AUDIT_LOG_DIR=/app/logs/audit

WORKDIR /app

COPY pyproject.toml README.md ./
RUN uv sync --no-dev --no-install-project

COPY app ./app
COPY prompts ./prompts

RUN uv sync --no-dev \
    && mkdir -p /app/logs/audit \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app \
    && chown -R app:app /app

USER app

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
