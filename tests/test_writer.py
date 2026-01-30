import pytest

from hadalized.config import Config, BuildConfig, ContextType
from hadalized.writer import ThemeWriter


def test_writer_full_context(config: Config):
    build = BuildConfig(
        name="test",
        template="template.txt",
        context_type=ContextType.full,
    )
    with ThemeWriter(config) as writer:
        writer.build(build)


def test_theme_writer_run_uses_cache(config: Config, build_config):
    config = config.replace(builds={build_config.name: build_config})
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


def test_writer_get_package_template(config: Config):
    assert ThemeWriter(config).get_template("neovim.lua")


def test_writer_get_fs_template(config: Config):
    assert ThemeWriter(config).get_template("template.txt")
