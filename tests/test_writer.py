import pytest

from hadalized.config import Config
from hadalized.writer import ThemeWriter


def test_theme_writer_run_uses_cache(config: Config, build_config):
    config = config.replace(builds={"neovim": build_config})
    with ThemeWriter(config) as writer:
        written = writer.run()
        assert written
        written = writer.run()
        assert written == []


def test_build_with_copy(config: Config, build_config):
    with ThemeWriter(config) as writer:
        output_dir = config.build_dir / "copies"
        writer.build(build_config, output_dir=output_dir)
        assert (output_dir / "hadalized.lua").exists()


def test_writer_exits_with_exception(config: Config):
    with pytest.raises(ValueError):
        with ThemeWriter(config):
            raise ValueError("bomb")
