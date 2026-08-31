default:
    just --list

dev:
    docker compose -f compose-dev.yaml up -d

dev-down:
    docker compose -f compose-dev.yaml down

[working-directory('backend')]
lint:
    uv run ruff check --fix || true
    uv run ruff format
    uv run ty check

[working-directory('backend')]
tests *options="":
    uv run pytest {{ options }}
