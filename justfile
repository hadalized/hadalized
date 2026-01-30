gen:
    @echo "Generating templates"
    uv run --exact hadalized

ed:
    source .venv/bin/activate && nvim src/hadalized/config.py

fmt:
    uv run --exact ruff format src/ tests/
    uv run --exact ruff check --fix src/ tests/

check:
    uv run --exact ruff check src/ tests/
    uv run --exact ty check src/ tests/

test:
    uv run --exact pytest

clear_cache:
    uv run --exact python bin/clear_cache.py
