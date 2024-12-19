FROM python:3.12.6-slim-bullseye@sha256:6fe70237cff8ad7c0a91b992cb7cb454187dfd2e3f08ce2d023907d76db8c287 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12.6-slim-bullseye@sha256:6fe70237cff8ad7c0a91b992cb7cb454187dfd2e3f08ce2d023907d76db8c287 AS prod

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "/app/src/soundboard/__init__.py"]
