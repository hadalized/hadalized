"""Common configuration options. Passed to many objects and CLI functions."""

from pathlib import Path
from typing import Annotated, Any

from cyclopts.parameter import Parameter
from pydantic import AfterValidator, Field

from hadalized import homedirs
from hadalized.base import BaseNode


def validate_nullable_path(val: str | Path | None) -> Path | None:
    """Convert special values of `null` or `none` to None.

    Returns:
        A ``Path`` instance or None.

    """
    match str(val).lower():
        case "null" | "none":
            out = None
        case _:
            out = Path(val) if isinstance(val, str) else val
    return out


@Parameter(name="*")
class Options(BaseNode):
    """Common options available to all CLI commands and configuration."""

    # fixme: Annotated[
    #     Path | None,
    #     Parameter(alias=["--fix"]),
    #     AfterValidator(validate_nullable_path),
    # ] = None
    include_builds: Annotated[
        list[str],
        Parameter(name="app", alias=["-a"], negative=""),
    ] = Field(default=[])
    """Application themes to build. The elements must correspond to a
    ``Config.builds`` key, which is typically an application name.
    If not specified, all applications in ``Config.builds`` will be
    generated.
    """
    cache_dir: Annotated[Path, Parameter(parse=True)] = homedirs.cache()
    """Location of cache directory."""
    config_file: Path | None = None
    """Specify a toml file to load configuration from. When specified,
    the standard configurations specified in ``UserConfig`` are ignored.
    """
    cache_in_memory: Annotated[bool, Parameter(negative="")] = False
    """Whether to use in-memory application cache."""
    dry_run: Annotated[bool, Parameter(alias="-n", negative="")] = False
    """Do not output any files or write to cache."""
    force: Annotated[bool, Parameter(alias="-f", negative="")] = False
    """Force rewriting of files. If set during theme building, files will
    be regenerated and cache populated."""
    no_cache: Annotated[bool, Parameter(negative="")] = False
    """Ignore cache completely. If set during theme building, hash digests
    of generated files will not be cached."""
    no_config: Annotated[bool, Parameter(negative="")] = False
    """Do not read settings from user config files. Implies `--no-templates`."""
    no_templates: Annotated[bool, Parameter(negative="")] = False
    """Ignore user defined templates. Implied by `--no-config`."""
    output_dir: Annotated[
        Path | None,
        Parameter(alias=["--output", "--out", "-o"]),
        AfterValidator(validate_nullable_path),
    ] = Field(
        default=None,
        examples=[Path("./build"), Path("./colors")],
    )
    """Directory to copy built theme files to or output files."""
    parse: Annotated[bool, Parameter(negative="")] = False
    """Whether palette colors should be parsed and expanded upon loading."""
    include_palettes: Annotated[
        list[str],
        Parameter(name="palette", alias=["-p"], negative=""),
    ] = Field(default=[])
    """Palettes to include when building application theme files. The
    items must include a key or alias in the ``Config.palettes`` definitions.
    If not specified, all defined palettes will be utilized.
    """
    prefix: Annotated[bool, Parameter()] = False
    """When set in conjunction with an output directory, built themes will
    be placed in a subdirectory determined by built theme file's parent
    directory. Typically this is just the applicate name, e.g., 'neovim'."""
    quiet: Annotated[bool, Parameter(alias="-q", negative="")] = False
    """Suppress logging to stdout."""
    state_dir: Annotated[Path, Parameter(parse=True)] = homedirs.state()
    """Directory containing application state such as built theme files."""
    template_dir: Annotated[Path, Parameter(parse=True)] = homedirs.template()
    """Directory where templates will be searched for initially. If a template
    is not found in this directory, it will be loaded from those defined in the
    package."""
    verbose: Annotated[bool, Parameter(alias="-v", negative="")] = False
    """Log more details."""

    def model_post_init(self, context: Any, /) -> None:
        """Check if settings do not conflict.

        Raises:
            ValueError: When mutually exclusive options are set.


        """
        if self.verbose and self.quiet:
            raise ValueError("Cannot set both verbose and quiet.")
        if self.no_cache and self.cache_in_memory:
            raise ValueError("Cannot set both no_cache and cache_in_memory.")
        if self.no_config and self.config_file:
            raise ValueError("Cannot set both no_config and config_file.")

        return super().model_post_init(context)

    @property
    def build_dir(self) -> Path:
        """Location of built theme files."""
        return self.state_dir / "build"

    @property
    def use_cache(self) -> bool:
        """Opposite of `no_cache`."""
        return not self.no_cache

    @property
    def use_templates(self) -> bool:
        """Whether to use user-defined templates.

        False if ``no_config`` is set.

        """
        return not self.no_config and not self.no_templates
