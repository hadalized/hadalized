from hadalized.cli import main as m


def test_build_single_app(tmp_path, config):
    m.build(app=["neovim"], out=tmp_path, prefix=True, config=config)
    assert (config.build_dir / "neovim" / "hadalized.lua").exists()
    assert (tmp_path / "neovim" / "hadalized.lua").exists()


def test_cache_list():
    m.cache_list()
