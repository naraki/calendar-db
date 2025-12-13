
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run"]
