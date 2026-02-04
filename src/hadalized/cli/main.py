"""Application commands."""

from contextlib import suppress
from pathlib import Path  # noqa
from shutil import rmtree

from cyclopts import App

from hadalized import homedirs
from hadalized.cache import Cache
from hadalized.config import Config, Options, load_config
from hadalized.writer import ThemeWriter

app = App()
cache_app = app.command(App(name="cache", help="Interact with the application cache."))
config_app = app.command(
    App(name="config", help="Interact with the application config.")
)
palette_app = app.command(App(name="palette", help="Interact with palettes."))
state_app = app.command(
    App(name="state", help="Interact with the application state, e.g., built files.")
)


@app.command
def build(name: str | None = None, opt: Options | None = None):
    """Build application color themes files.

    When no applications or palette is specified, themes will be built for all
    application and palette pairs.

    Args:
        name: Target application to build. Use ``--app`` to include multiple.
        opt: Options.

    """
    opt = opt or Options()
    if name is not None:
        opt |= Options(include_builds=[*opt.include_builds, name])
    config = load_config(opt)
    if config.dry_run:
        print("DRY-RUN. No theme files will be generated or copied.")
    with ThemeWriter(config) as writer:
        writer.run()


# @config_app.command(name="info")
# def config_info(opt: Options | None = None):
#     """Dispaly configuration info."""
#     from rich import print_json
#
#     config = load_config(opt)
#     print_json(config.model_dump_json())


@config_app.command(name="schema")
def config_schema():
    """Display configuration schema."""
    import json

    from rich import print_json

    print_json(json.dumps(Config.model_json_schema()))


@config_app.command(name="init")
def config_init(opts: Options | None = None):
    """Populate application configuration toml file.

    When `--output=stdout` the toml contents will be printed.
    """
    import tomli_w as toml

    config = load_config(opts)
    if str(config.output_dir) == "stdout":
        print(toml.dumps(config.model_dump(mode="json", exclude_none=True)))
        return
    output = config.output_dir or homedirs.config()
    if output.suffix != ".toml":
        output /= "config.toml"

    output_exists = output.exists()
    if output_exists and not config.quiet:
        print(f"{output} already exists.")
    if output_exists and not config.force:
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as fp:
        if not config.quiet:
            print(f"Creating {output}")
        data = config.model_dump(mode="json", exclude_none=True)
        if not config.dry_run:
            toml.dump(data, fp)
    # except TypeError as exc:
    #     print(f"Unable to write config file: {exc}")
    #     output.unlink()


@palette_app.command(name="parse")
def palette_parse(
    name: str = "hadalized",
    *,
    gamut: str | None = None,
    opt: Options | None = None,
):
    """Show information about a particular palette.

    Args:
        name: Palette name or alias, e.g., "hadalized".
        gamut: A specifed gamut to parse against. If not provided, the
            gamut defined by the palette is used.
        opt: Options

    """
    # TODO: Respect user config.
    from rich import print_json

    opt = opt or Options()
    config = load_config(opt)
    for item in [name, *config.include_palettes]:
        palette = config.get_palette(item)
        if gamut is not None:
            palette = palette.replace(gamut=gamut)
        print_json(palette.parse().model_dump_json())


@cache_app.command(name="clean")
def cache_clean(opt: Options | None = None):
    """Clear the application cache."""
    config = load_config(opt)
    if config.dry_run and not config.quiet:
        print("DRY-RUN: Cache files will not be deleted.")
    if not config.quiet:
        print(f"Clearing {config.cache_dir}")
    if config.verbose:
        files = "\n".join(str(x) for x in config.cache_dir.glob("**/*") if x.is_file())
        print(files)
    if not config.dry_run:
        with suppress(FileNotFoundError):
            rmtree(config.cache_dir)


@cache_app.command(name="dir")
def cache_dir(opt: Options | None = None):
    """Show the cache directory."""
    config = load_config(opt)
    print(config.cache_dir)


@cache_app.command(name="list", alias=["ls"])
def cache_list(opt: Options | None = None):
    """List the contents of the application cache."""
    import json

    from rich import print_json

    config = load_config(opt)

    with Cache(config.opt) as cache:
        print_json(json.dumps(cache.get_digests()))


@state_app.command(name="dir")
def state_dir(opt: Options | None = None):
    """Show the applicate state directory."""
    config = load_config(opt)
    print(config.opt.state_dir)


@state_app.command(name="clean")
def state_clean(opt: Options | None = None):
    """Clear application state files such as built themes."""
    config = load_config(opt)
    if config.dry_run and not config.quiet:
        print("DRY-RUN. No state files will be deleted.")
    if not config.quiet:
        # import json
        #
        # from rich import print_json

        print(f"Clearing {config.state_dir}")
        files = "\n".join(str(x) for x in config.state_dir.glob("**/*") if x.is_file())
        if files:
            print(files)
        # print_json(json.dumps(files))
    if not config.dry_run:
        with suppress(FileNotFoundError):
            rmtree(config.state_dir)


@state_app.command(name="list", alias=["ls"])
def state_list(opt: Options | None = None):
    """List application state files."""
    config = load_config(opt)
    files = "\n".join(str(x) for x in config.state_dir.glob("**/*") if x.is_file())
    print(files)


@app.command
def clean(opt: Options | None = None):
    """Clean cache and state files."""
    cache_clean(opt)
    state_clean(opt)


# @app.command
# def debug(opt: Options | None = None):
#     """Debug things."""
#     from rich import print_json
#
#     config = load_config(opt)
#     print(f"{config.cache_dir=}")
#     print(f"{config.dry_run=}")
#     print(f"{opt=}")
#     if opt is not None:
#         print(f"{opt.model_fields_set=}")
#     print("config.opt")
#     print_json(config.opt.model_dump_json())
#     print(f"{config.model_fields_set=}")
#     print(f"{config.opt.model_fields_set=}")
