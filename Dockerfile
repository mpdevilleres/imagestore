FROM python:3.11-slim AS base

WORKDIR /opt

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

COPY ./pyproject.toml ./uv.lock ./README.md ./
COPY ./src ./src
COPY ./templates ./templates

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

FROM base AS runtime

ARG VERSION
ENV VERSION=${VERSION}

COPY --from=builder /opt/.venv /opt/.venv
COPY ./src ./src
COPY ./templates ./templates

COPY ./entrypoint.sh /entrypoint.sh
COPY ./cmd.sh /cmd.sh

RUN chmod +x /entrypoint.sh
RUN chmod +x /cmd.sh

ENV PATH=/opt:/opt/.venv/bin:${PATH}

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/cmd.sh"]
