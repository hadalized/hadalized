from pathlib import Path

import pytest

from hadalized.config import (
    Config,
    Options,
    TerminalConfig,
    UserConfig,
    load_config,
)


def test_config_methods():
    conf = Config()
    assert hash(conf) == hash(conf)
    assert conf.builds
    assert conf.palettes
    assert conf.to("hex")
    assert conf.to("css")
    assert conf.parse_palettes().palettes["hadalized"]._is_parsed


# @pytest.mark.parametrize(
#         "idx",
#         list(range(1,17))
# )
def test_terminal_config_ansi():
    conf: TerminalConfig = TerminalConfig()
    for idx in range(1, 7):
        assert conf.ansi.get_name(idx)
        assert conf.ansi.get_name(idx + 8)
    assert len(conf.ansi.pairing) == 6


def test_model_dump_lua(config: Config):
    assert config.model_dump_lua()


def test_load_config_from_user_specified_file():
    opt = Options(
        config_file=Path(__file__).parent / "test_config.toml",
        cache_dir=Path("set_in_init"),
    )
    config = load_config(opt)
    assert not isinstance(config, UserConfig)
    assert config.cache_dir == opt.cache_dir
    assert config.template_dir == Path("set_in_test_config")


def test_load_config_no_config_set():
    opt = Options(
        no_config=True,
        cache_dir=Path("set_in_init"),
    )
    config = load_config(opt)
    assert not isinstance(config, UserConfig)
    assert config.cache_dir == opt.cache_dir


def test_load_config_is_user_config(monkeypatch: pytest.MonkeyPatch):
    cache_dir = "set_in_env"
    monkeypatch.setenv("HADALIZED_CACHE_DIR", cache_dir)
    config = load_config()
    assert isinstance(config, UserConfig)
    assert config.cache_dir == Path(cache_dir)

    opt = Options(cache_dir=Path("set_from_init"))
    config = load_config(opt)
    assert isinstance(config, UserConfig)
    assert config.cache_dir == opt.cache_dir


def test_opts_init():
    assert Options(no_config=True)
    assert Options(no_templates=True)
    assert Options(verbose=True)
    assert Options(quiet=True)


def test_opts_mutually_exclusive_fields():
    with pytest.raises(ValueError):
        Options(config_file=Path("blah"), no_config=True)
    with pytest.raises(ValueError):
        Options(cache_in_memory=True, no_cache=True)
    with pytest.raises(ValueError):
        Options(verbose=True, quiet=True)


def test_opts_properties():
    opts = Options(no_config=True)
    assert opts.use_cache is True
    assert opts.use_templates is False
