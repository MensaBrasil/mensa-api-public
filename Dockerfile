FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim as base
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

FROM base as deps
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev

FROM base as runtime
COPY --from=deps /app/.venv .venv
COPY . /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "uvicorn", "people_api:app", "--host", "0.0.0.0", "--port", "5000"]
