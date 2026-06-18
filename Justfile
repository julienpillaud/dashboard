default:
    just --list

lint:
    uv run ruff check --fix || true
    uv run ruff format
    uv run ty check

tests *options="":
    uv run pytest {{ options }}
