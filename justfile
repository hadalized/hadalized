gen:
    @echo "Generating templates"
    uv run --exact hadalized build --prefix --output_dir=build

ed:
    source .venv/bin/activate && nvim src/hadalized/config.py

# uv format is a preview feature. Can specify which version of ruff to use.
fmt:
    # uv format -- src/ tests/
    # uv run --exact ruff format src/ tests/
    # uv run --exact ruff check --fix src/ tests/
    ruff format src/ tests/
    ruff check --fix src/ tests/

check:
    ruff check src/ tests/
    # uv format --check -- src/ tests/
    ty check src/ tests/
    # uv run --exact ruff check src/ tests/
    # uv run --exact ty check src/ tests/

# Update the project version using the given semantics
# possible `part` values {major, minor, patch, stable, alpha, beta, rc, post, dev}
bump part:
    uv version --bump {{part}}

# Pushing a tag of the form v* kicks off the publish github workflow.
publish:
    @echo "Publishing $(uv version)"
    VERSION=$(uv version --short) && git tag -a "v${VERSION}" -m "v${VERSION}"
    git push --tags

test:
    uv run --exact pytest
