gen:
    @echo "Generating templates"
    uv run --exact hadalized

ed:
    source .venv/bin/activate && nvim src/hadalized/config.py

fmt:
    # uv format -- src/ tests/
    # uv run --exact ruff format src/ tests/
    ruff format src/ tests/
    ruff check --fix src/ tests/
    # uv run --exact ruff check --fix src/ tests/

check:
    ruff check src/ tests/
    # uv format --check -- src/ tests/
    ty check src/ tests/
    # uv run --exact ruff check src/ tests/
    # uv run --exact ty check src/ tests/

tag version:
    git tag -a "v{{version}}" -m "v{{version}}"

test:
    uv run --exact pytest

clear_cache:
    uv run --exact python bin/clear_cache.py
