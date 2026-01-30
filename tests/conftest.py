from pathlib import Path
from typing import TYPE_CHECKING
import pytest

from hadalized.config import default_palettes, Config

if TYPE_CHECKING:
    from hadalized.palette import Palette
    from hadalized.config import BuildConfig

_config = Config()


@pytest.fixture
def config(tmp_path) -> Config:
    return Config(
        build_dir=tmp_path / "build",
        cache_dir=tmp_path / "cache",
        template_dir=Path(__file__).parent,
        verbose=True,
    )


@pytest.fixture
def palette() -> Palette:
    return _config.get_palette("dark").parse()


@pytest.fixture
def raw_palette() -> Palette:
    return default_palettes()["hadalized"]


@pytest.fixture
def build_config() -> BuildConfig:
    return _config.builds["neovim"]
