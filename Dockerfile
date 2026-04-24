# BUILD STAGE
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# optimization configs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# copy dependency files first (cache layer)
COPY pyproject.toml uv.lock ./

# install depedencies including dev group
RUN uv sync --frozen --group dev

COPY . .

# ensure project is installed in venv too
RUN uv sync --frozen --group dev


# PRODUCTION STAGE
FROM python:3.12-slim

WORKDIR /app

# optimization configs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p /app/static /app/media

# copy application code
COPY --from=builder /app /app

EXPOSE 8000

COPY entrypoint.prod.sh /app/entrypoint.prod.sh

RUN chmod +x /app/entrypoint.prod.sh

CMD ["/app/entrypoint.prod.sh"]
