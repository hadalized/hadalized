"""Application commands."""

from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from hadalized import homedirs
from hadalized.writer import ThemeWriter
from hadalized.config import Config

app = App()
cache_app = app.command(App(name="cache", help="Interact with the application cache."))
config_app = app.command(
    App(name="config", help="Interact with the application config.")
)
# palette_app = app.command(
#     App(name="palette", help="Interact with palettes.")
#
# )


# def _get_config(config: Config | None = None) -> Config:
#     """allow this func to be monkeypatched for unit tests?"""
#     from hadalized.config import Config
#     return Config()
#


@app.command
def build(
    app: Annotated[list[str] | None, Parameter(negative="")] = None,
    exclude: Annotated[list[str] | None, Parameter(alias="-e", negative="")] = None,
    output: Annotated[Path | None, Parameter(alias=["-o", "--out"])] = None,
    palette: Annotated[list[str] | None, Parameter(alias="-p")] = None,
    verbose: Annotated[bool, Parameter(alias="-v", negative="")] = False,
    prefix: Annotated[bool, Parameter(alias="-P", negative="")] = False,
    cache: bool = True,
    config: Annotated[Config | None, Parameter(parse=False)] = None,
):
    """Build themes for the specified applications.

    Args:
        app: Build themes for the specified list of application names.
            If none are provided, all theme files will be built.
        exclude: A list of application names to exclude when building.
        output: An output directory to copy generated theme files to.
        palette: List of palettes to build. If excluded, all palettes are
            included.
        verbose: Run in verbose mode.
        prefix: If set, add each application name / theme category prefix to
            the output path. Ignored if `output` is not specified.
        cache: If set, use the cache.
    """
    exclude = exclude or []
    config = config or Config()
    if palette is None:
        palettes = config.palettes
    else:
        palettes = {p.name: p for p in (config.get_palette(x) for x in palette)}

    config = config.replace(
        verbose=verbose,
        palettes=palettes,
        disable_cache=not cache,
    )

    if not app:
        build_configs = [v for k, v in config.builds.items() if k not in exclude]
    else:
        build_configs = [
            v for k, v in config.builds.items() if k in app and k not in exclude
        ]
    with ThemeWriter(config) as writer:
        for build_config in build_configs:
            output_dir = output
            if prefix and output_dir is not None:
                output_dir /= build_config.name
            writer.build(build_config, output_dir=output_dir)


@config_app.command(name="info")
def config_info(parse: Annotated[bool, Parameter(negative="")] = False):
    from rich import print_json

    config = Config()
    if parse:
        config = config.parse_palettes()
    print_json(config.model_dump_json())


@config_app.command(name="schema")
def config_schema():
    from rich import print_json
    import json

    print_json(json.dumps(Config.model_json_schema()))


@config_app.command(name="init")
def config_init(
    force: Annotated[bool, Parameter(negative="")] = False,
):
    """Populate application configuration in $XDG_CONFIG_HOME/hadalized

    Args:
        force: If supplied, rewrite existing user configuration files.
    """
    # TODO: just tests for now
    import tomli_w as toml

    config_path = homedirs.config() / "config.toml"
    if not force and config_path.exists():
        print(f"{config_path} already exists.")
        return
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = Config()
    # print_json(config.model_dump_json())

    try:
        with config_path.open("wb") as fp:
            print(f"Creating {config_path}")
            data = config.model_dump(mode="json", exclude_none=True)
            toml.dump(data, fp)
    except TypeError as exc:
        print(f"Unable to write config file: {exc}")
        config_path.unlink()


@app.command(name="palette")
def palette_info(name: str = "hadalized", gamut: str | None = None, parse: bool = True):
    """Show information about a particular palette.

    Args:
        name: Palette name or alias, e.g., "hadalized".
        gamut: A specifed gamut to parse against. If not provided, the
            gamut defined by the palette is used.
        parse: Whether to fully parse the palette. If set to false, only
            raw color definitions are shown.

    """
    # TODO: Respect user config.
    from rich import print_json

    config = Config()
    palette = config.get_palette(name)
    if parse:
        if gamut is not None:
            palette = palette.replace(gamut=gamut)
        palette = palette.parse()
    print_json(palette.model_dump_json())


@cache_app.command(name="clear")
def cache_clear(
    config: Annotated[Config, Parameter(parse=False)] = Config(),
):
    """Clear the application cache."""
    from hadalized.cache import Cache

    with Cache() as cache:
        cache.clear()


@cache_app.command(name="list", alias=["ls"])
def cache_list():
    """List the contents of the application cache.

    Args:
        config: Configuration instance.

    """
    from hadalized.cache import Cache
    from rich import print_json
    import json

    with Cache() as cache:
        print_json(json.dumps(cache.get_digests()))


@cache_app.command(name="info")
def cache_info(config: Config = Config()):
    """List the contents of the application cache."""
    with ThemeWriter(config) as writer:
        cache = writer.cache
        print(f"Cache dir: {cache.cache_dir.absolute()}")
        print(f"Cache db file: {cache._db_file.absolute()}")
        print(f"Cache is in memory: {cache.in_memory}.")
