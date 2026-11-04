FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.18 /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY alembic.ini ./
COPY migrations ./migrations
COPY studio ./studio
ENV PATH=/app/.venv/bin:$PATH PYTHONUNBUFFERED=1
CMD ["sh", "-c", "alembic upgrade head && uvicorn studio.main:app --host 0.0.0.0 --port 8000"]
