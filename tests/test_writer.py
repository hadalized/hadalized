from pathlib import Path

import pytest
from jinja2.exceptions import TemplateNotFound

from hadalized.config import BuildConfig, Config, ContextType, Options
from hadalized.writer import ThemeWriter


def test_writer_full_context(config: Config):
    build = BuildConfig(
        name="test",
        template=Path("template.txt"),
        context_type=ContextType.full,
    )
    with ThemeWriter(config) as writer:
        writer.build(build)


def test_theme_writer_run_uses_cache(config: Config):
    with ThemeWriter(config) as writer:
        written = writer.run()
        assert written
        written = writer.run()
        assert not written


def test_build_with_copy(config: Config, build_config):
    with ThemeWriter(config) as writer:
        writer.build(build_config)
        assert config.output_dir is not None
        assert (config.output_dir / "hadalized.lua").exists()


def test_writer_exits_with_exception(config: Config):
    with pytest.raises(ValueError), ThemeWriter(config):
        raise ValueError("bomb")


def test_writer_get_package_template(config: Config):
    assert ThemeWriter(config).get_template("neovim.lua")


def test_writer_get_fs_template(config: Config):
    assert ThemeWriter(config).get_template("template.txt")


def test_writer_get_template_fail(config: Config):
    config |= Options(no_templates=True)
    with pytest.raises(TemplateNotFound):
        ThemeWriter(config).get_template("bomb")
