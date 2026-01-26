"""Application commands."""

from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from hadalized.writer import ThemeWriter
from hadalized.config import Config

app = App()
cache_app = app.command(App(name="cache", help="Interact with the application cache."))


# def _get_config(config: Config | None = None) -> Config:
#     """allow this func to be monkeypatched for unit tests?"""
#     from hadalized.config import Config
#     return Config()
#


@app.command
def build(
    app: list[str] | None = None,
    # TODO: filter on palettes too?
    # palettes: Annotated[list[str] | None, Parameter(alias="-p")] = None,
    out: Path | None = None,
    exclude: Annotated[list[str] | None, Parameter(alias="-e")] = None,
    verbose: Annotated[bool, Parameter(alias="-v", negative="")] = False,
    prefix: Annotated[bool, Parameter(alias="-P", negative="")] = False,
    config: Annotated[Config, Parameter(parse=False)] = Config(),
):
    """Build themes for the specified applications.

    Args:
        app: Build themes for the specified list of application names.
            If none are provided, all theme files will be built.
        exclude: A list of application names to exclude when building.
        out: An output directory to copy generated theme files to.
        verbose: Run in verbose mode.
        prefix: If set, add each application name / theme category prefix to
            the output path. Ignored if `out` is not specified.
    """
    exclude = exclude or []
    config = config.replace(verbose=verbose)
    if not app:
        build_configs = list(v for k, v in config.builds.items() if k not in exclude)
    else:
        build_configs = [config.builds[x] for x in app if x not in exclude]
    with ThemeWriter(config) as writer:
        for build_config in build_configs:
            if prefix and out is not None:
                out /= build_config.name
            writer.build(build_config, output_dir=out)


# FIXME: development only
# @app.command
# def show(config: Config):
#     print(config.build_dir)
#     print(config.cache_dir is None, config.cache_dir)
#     print(config.template_dir)


@cache_app.command(name="clear")
def cache_clear(
    config: Annotated[Config, Parameter(parse=False)] = Config(),
):
    """Clear the application cache."""
    from hadalized.cache import Cache

    with Cache() as cache:
        cache.clear()


@cache_app.command(name="list", alias=["ls"])
def cache_list(config: Config = Config()):
    """List the contents of the application cache."""
    with ThemeWriter(config) as writer:
        cache = writer.cache
        print(f"Cache db file {cache._db_file.absolute()}")
        print(f"Cache is in memory: {cache.in_memory}.")
        print("Cache contents")
        results = cache._conn.execute("SELECT * from builds")
        for path, digest in results:
            print(f"{path}: {digest}")


# app()
