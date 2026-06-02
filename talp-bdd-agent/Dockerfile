# Minimal, production-friendly Dockerfile for the BDD QA Agent

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal build dependencies for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata first to leverage Docker layer caching
COPY pyproject.toml pytest.ini README.md .env.example ./

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

# Upgrade pip and install package (including dev extras for convenience)
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir .[dev]

# Create a non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -m appuser
USER appuser

EXPOSE 8000

# Default command to run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
