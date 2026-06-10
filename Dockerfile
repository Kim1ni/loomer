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

# Run the FastAPI app using uvicorn
CMD uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
