FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

FROM base AS deps
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev

FROM base AS runtime
COPY --from=deps /app/.venv .venv
COPY . /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "-m", "people_api", "api"]
