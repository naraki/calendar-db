FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#FROM ghcr.io/astral-sh/uv:python3.12

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync
COPY . .
#COPY ../calendar_secret.json ./credentials.json

CMD ["uv", "run", "test.py"]
#CMD ["uv", "run", "main.py"]
