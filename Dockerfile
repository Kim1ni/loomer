FROM python:3.12-slim

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (excluding dev dependencies)
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

# Cloud Run injects the PORT environment variable
ENV PORT=8080

# Install dependencies and sync into a virtual environment
RUN uv sync --frozen --no-dev

# Run uvicorn directly
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]