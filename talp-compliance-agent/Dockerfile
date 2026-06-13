FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -e . \
    && mkdir -p /app/storage/db /app/storage/audit /app/storage/logs \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -m appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]