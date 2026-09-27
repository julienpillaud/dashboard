FROM oven/bun:1.3-slim AS frontend-builder

WORKDIR /workspace
RUN --mount=type=cache,target=/root/.cache/bun \
    --mount=type=bind,source=frontend/bun.lock,target=bun.lock \
    --mount=type=bind,source=frontend/package.json,target=package.json \
    bun install --frozen-lockfile

# Copy frontend folder content inside workspace
COPY frontend .

RUN bun x vite build

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS backend-builder
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends git

# Disable Python downloads, because we want to use the system interpreter
# across both images.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /workspace
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked
# Copy backend folder content inside workspace
COPY backend .

# Use a final image without uv
FROM python:3.14-slim-bookworm

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from the backend-builder
COPY --from=backend-builder --chown=nonroot:nonroot /workspace /workspace
COPY --from=frontend-builder --chown=nonroot:nonroot /workspace/dist /workspace/dist

# Place executables in the environment at the front of the path
ENV PATH="/workspace/.venv/bin:$PATH"

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Use the non-root user to run our application
USER nonroot

# Use `/workspace` as the working directory
WORKDIR /workspace

# Run the FastAPI application
CMD [ \
  "uvicorn", \
  "app.core.app:app", \
  "--host", "0.0.0.0", \
  "--proxy-headers", \
  "--forwarded-allow-ips", "*", \
  "--log-config", "app/core/logging/config.json" \
]
