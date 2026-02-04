from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from hadalized.config import Config

if TYPE_CHECKING:
    from hadalized.config import BuildConfig
    from hadalized.palette import Palette

_config = Config()


@pytest.fixture
def config(tmp_path) -> Config:
    return Config(
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        template_dir=Path(__file__).parent,
        output_dir=tmp_path / "output",
        verbose=True,
    )


@pytest.fixture
def palette() -> Palette:
    return _config.get_palette("dark").parse()


@pytest.fixture
def raw_palette() -> Palette:
    return _config.get_palette("dark")


@pytest.fixture
def build_config() -> BuildConfig:
    return _config.builds["neovim"]
