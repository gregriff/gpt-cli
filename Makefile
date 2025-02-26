# these are for development only. refer to readme for installation instructions

# use this after adding new packages to pyproject.toml
lock:
	uv lock

install:
	uv sync

run:
	uv run src/main.py

# run the cheapest model available for debugging
run-test:
	uv run src/main.py "claude-3-5-haiku"

lint:
	ruff check --fix

format: lint
	ruff format


.PHONY: install format lock run lint format
