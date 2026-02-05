from pathlib import Path

import pytest

from hadalized.cli import main as m
from hadalized.config import Options


@pytest.fixture
def realopts(tmp_path: Path) -> Options:
    return Options(
        # include_build=["neovim"],
        include_palettes=["hadalized"],
        prefix=True,
        state_dir=tmp_path / "state",
        output_dir=tmp_path / "output",
        no_config=True,
        verbose=True,
    )


@pytest.fixture
def dryopts(tmp_path: Path) -> Options:
    return Options(
        # include_build=["neovim"],
        include_palettes=["hadalized"],
        prefix=True,
        state_dir=tmp_path / "state",
        output_dir=tmp_path / "output",
        no_config=True,
        verbose=True,
        dry_run=True,
    )


def test_build_single_app(realopts: Options):
    opt = realopts
    m.build(name="neovim", opt=opt)
    assert (opt.build_dir / "neovim" / "hadalized.lua").exists()
    assert opt.output_dir is not None
    assert (opt.output_dir / "neovim" / "hadalized.lua").exists()


def test_build_single_app_no_copy(realopts: Options):
    opt = realopts | Options(output_dir=None)
    m.build(name="starship", opt=opt)
    assert (opt.build_dir / "starship" / "starship.toml").exists()


def test_build_single_app_dry(dryopts: Options):
    opt = dryopts
    m.build(name="neovim", opt=opt)


def test_cache_list():
    m.cache_list()


def test_cache_dir():
    m.cache_dir()


def test_state_list():
    m.state_list()


def test_state_dir():
    m.state_dir()


def test_clean(realopts: Options, dryopts: Options):
    realopts.state_dir.mkdir(parents=True, exist_ok=True)
    realopts.cache_dir.mkdir(parents=True, exist_ok=True)
    db_file = realopts.state_dir / "test.db"
    log_file = realopts.cache_dir / "test.log"
    db_file.touch()
    log_file.touch()
    m.clean(realopts)
    assert not db_file.exists()
    assert not log_file.exists()
    m.clean(dryopts)


def test_config_init_output_file_given(tmp_path):
    output = tmp_path / "hadalized.toml"
    # Initial generation.
    m.config_init(Options(output_dir=output, no_config=True))
    assert output.exists()
    # Force re-generation
    m.config_init(Options(output_dir=output, no_config=True, force=True))
    assert output.exists()
    # Exit early since file exists.
    m.config_init(Options(output_dir=output, no_config=True))
    assert output.exists()


def test_config_init_output_dir_given(tmp_path):
    # No name given to file
    opt = Options(output_dir=tmp_path, no_config=True)
    m.config_init(opt)
    assert (tmp_path / "config.toml").exists()
    m.config_init(Options(output_dir=tmp_path, no_config=True, dry_run=True))


def test_config_options():
    m.config_options()


def test_config_init_output_stdout(tmp_path):
    m.config_init(Options(output_dir=Path("stdout"), no_config=True))


def test_config_schema():
    m.config_schema()


def test_palette_parse():
    m.palette_parse(name="dark", gamut="display-p3")
    m.palette_parse(name="hadalized")
