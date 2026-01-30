from hadalized.cli import main as m


def test_build_single_app(tmp_path, config):
    m.build(app=["neovim"], output=tmp_path, prefix=True, config=config)
    assert (config.build_dir / "neovim" / "hadalized.lua").exists()
    assert (tmp_path / "neovim" / "hadalized.lua").exists()


def test_cache_list():
    m.cache_list()


def test_palette_info():
    m.palette_info(name="dark", gamut="display-p3")
    m.palette_info(name="dark", parse=False)
