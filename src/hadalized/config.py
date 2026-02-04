"""Module containing all underlying color definitions and gamut info."""

from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Self

from pydantic import Field, PrivateAttr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from hadalized import homedirs
from hadalized.base import BaseNode
from hadalized.color import Bases, ColorFieldType, Hues, Ref
from hadalized.options import Options
from hadalized.palette import Palette


def default_palettes() -> dict[str, Palette]:
    """Lazily compute default palette colors.

    Returns:
        A map of palette.name -> palette.

    """
    # Palette definitions
    dark: Palette = Palette(
        name="hadalized",
        desc="Main dark theme with blueish solarized inspired backgrounds.",
        mode="dark",
        gamut="srgb",
        aliases=["dark"],
        hue=Hues.dark(),
        base=Bases.dark(),
    )

    gray: Palette = Palette(
        name="hadalized-gray",
        desc="Dark theme variant with more grayish backgrounds.",
        mode="dark",
        gamut=dark.gamut,
        aliases=["gray"],
        hue=Hues.dark(),
        base=Bases.dark()
        | Bases(
            bg=Ref.w13,
            bg1=Ref.w14,
            bg2=Ref.w16,
            bg3=Ref.w20,
            bg4=Ref.w25,
            bg5=Ref.w30,
            bg6=Ref.w35,
        ),
    )

    day: Palette = Palette(
        name="hadalized-day",
        desc="Light theme variant with sunny backgrounds.",
        mode="light",
        gamut="srgb",
        aliases=["day"],
        hue=Hues.light(),
        base=Bases.light(),
    )

    white: Palette = Palette(
        name="hadalized-white",
        desc="Light theme variant with whiter backgrounds.",
        mode="light",
        gamut=day.gamut,
        aliases=["white"],
        hue=Hues.light(),
        base=day.base
        | Bases(
            bg=Ref.w100,
            bg1=Ref.w99,
            bg2=Ref.w95,
            bg3=Ref.w92,
            bg4=Ref.w99,
            bg5=Ref.w85,
            bg6=Ref.w80,
        ),
    )

    return {
        dark.name: dark,
        gray.name: gray,
        day.name: day,
        white.name: white,
    }


class ANSIMap(BaseNode):
    """A mapping from color hue name to ANSI color index."""

    red: int = 1
    """Typically represents red."""
    rose: int = 9
    """Typically represents bright red."""
    green: int = 2
    """Typically represents green."""
    lime: int = 10
    """Typically represents bright green."""
    yellow: int = 3
    """Typically represents yellow."""
    orange: int = 11
    """Typically represents bright yellow."""
    blue: int = 4
    """Typically represents blue."""
    azure: int = 12
    """Typically represents bright blue."""
    magenta: int = 5
    """Typically represents magenta or purple."""
    violet: int = 13
    """Typically represents bright magenta or bright purple."""
    cyan: int = 6
    """Typically represents cyan."""
    mint: int = 14
    """Typically represents bright cyan."""
    _idx_to_name: dict[int, str] = PrivateAttr({})

    def model_post_init(self, context: Any, /) -> None:
        """Model post init."""
        super().model_post_init(context)
        self._idx_to_name = {idx: name for name, idx in self}

    def get_name(self, idx: int) -> str:
        """Lookup the color name.

        Returns:
            The field name whose value is in the input.

        """
        return self._idx_to_name[idx]

    @property
    def pairing(self) -> list[tuple[str, str]]:
        """A map of a color and it's 'bright' variant."""
        return [(self.get_name(i), self.get_name(i + 8)) for i in range(1, 7)]


class TerminalConfig(BaseNode):
    """Configurations related to terminal emulators."""

    ansi: ANSIMap = ANSIMap()


class ContextType(StrEnum):
    """Values determine which context expose to template when building a theme."""

    palette = auto()
    """A single palette will be passed to the `context` variable of a template."""
    full = auto()
    """A full `Config` instance will be passed to the `context` variable."""


class BuiltinThemes(StrEnum):
    """Enumerates the list of themes that are handled by the builder."""

    neovim = auto()
    wezterm = auto()
    starship = auto()


class BuildConfig(BaseNode):
    """Information about which files should be generatted specific app."""

    name: str = Field(
        examples=["neovim", "myapp", "html-examples"],
    )
    """Application name or theme category."""
    subdir: Path | None = None
    """Build sub-directory where theme files are placed. Defaults to `name`."""
    template: Path
    """Template filename relative to the templates directory."""
    filename: str | None = Field(
        default=None,
        examples=[
            "{context.name}.{template_ext}",  # default
            "starship-alt.toml",
        ],
    )
    """Output file name, including extension. For builds
    that generate palette specific theme files, the default filename is of the
    form `{palette.name}.{template.extension}`. For those that take in
    all palettes into the context, the filename defaults to the underlying
    template name.
    """
    context_type: ContextType = ContextType.palette
    """The underlying context type to pass to the template."""
    color_type: ColorFieldType = ColorFieldType.hex
    """How each Palette should be transformed when presented as context
    to the template."""
    _fname: str = PrivateAttr(default="")

    def model_post_init(self, context: Any, /) -> None:
        """Construct filename template."""
        filename = self.filename or ""
        if not self.filename:
            if self.context_type == ContextType.palette:
                filename = "{context.name}.{ext}"
            else:
                filename = str(self.template)

        # Infer extension from template file extension.
        if filename.endswith(".{ext}"):
            filename = filename.replace(".{ext}", self.template.suffix)
        self._fname = filename.rstrip(".")
        return super().model_post_init(context)

    def format_path(self, context: BaseNode) -> Path:
        """File output path relative to build directory.

        Returns:
            The absolute path where a file should be written.

        """
        fname = self._fname.format(context=context).rstrip(".")
        return (self.subdir or Path(self.name)) / fname


def default_builds() -> dict[str, BuildConfig]:
    """Builtin build configs.

    Returns:
        The default build instructions used to generate theme files.

    """
    return {
        "neovim": BuildConfig(
            name="neovim",
            template=Path("neovim.lua"),
        ),
        "wezterm": BuildConfig(
            name="wezterm",
            template=Path("wezterm.toml"),
        ),
        "starship": BuildConfig(
            name="starship",
            template=Path("starship.toml"),
            context_type=ContextType.full,
        ),
        "info": BuildConfig(
            name="info",
            template=Path("palette_info.json"),
            color_type=ColorFieldType.info,
        ),
        "html-samples": BuildConfig(
            name="html-samples",
            template=Path("palette.html"),
            color_type=ColorFieldType.css,
        ),
    }


class Config(Options):
    """App configuration.

    Contains information about which app theme files to generate and where
    to write the build artifacts.

    This particular Config will not load settings from anything except
    init arguments, and as such serves as a default Config base.
    """

    builds: dict[str, BuildConfig] = Field(default_factory=default_builds)
    """Build directives specifying how and which theme files are
    generated."""
    palettes: dict[str, Palette] = Field(default_factory=default_palettes)
    """Palette color definitions."""
    terminal: TerminalConfig = TerminalConfig()
    _palette_lu: dict[str, Palette] = PrivateAttr(default={})
    """Lookup for a palette by name or alias."""
    _opts: Options | None = PrivateAttr(default=None)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set source loading priority.

        Returns:
            Priority order in which config settings are loaded.

        """
        return (init_settings,)

    def model_post_init(self, context, /) -> None:
        """Set lookups."""
        for key, palette in self.palettes.items():
            self._palette_lu[key] = palette
            for alias in palette.aliases:
                self._palette_lu[alias] = palette

        return super().model_post_init(context)

    @property
    def opt(self) -> Options:
        """Access just the runtime options from the configuration."""
        if self._opts is None:
            fields = set(Options.model_fields)
            opts = {k: v for k, v in self if k in fields and k in self.model_fields_set}
            self._opts = Options.model_construct(**opts)
        return self._opts

    def get_palette(self, name: str) -> Palette:
        """Get Palette by name or alias.

        Returns:
            Palette instance.

        """
        return self._palette_lu[name]

    def to(self, color_type: str | ColorFieldType) -> Self:
        """Transform the ColorFields to the specified type.

        Use to render themes that require the entire context (e.g., all palettes),
        but where specific color representations (e.g., hex)
        are required.

        Returns:
            A new Config instance whose ColorFields match the input type.

        """
        return self.replace(
            palettes={k: v.parse().to(color_type) for k, v in self.palettes.items()}
        )

    def parse_palettes(self) -> Self:
        """Parse each Palette to contain full ColorInfo.

        Returns:
            A new instance with each Palette a ParsedPalette instance.

        """
        return self.replace(palettes={k: v.parse() for k, v in self.palettes.items()})

    def __hash__(self) -> int:
        """Hash of the main config contents, excluding runtime options.

        Returns:
            The hash of the json dump of the instance.

        """
        if self._hash is None:
            include = {"palettes", "build", "terminal"}
            self._hash = hash(self.model_dump_json(include=include))
        return self._hash


class UserConfig(Config):
    """User configuration settings.

    While schematically identical to the base ``Config`` parent class, when
    a UserConfig is instantiated a selection of settings locations are
    additionally scanned. The priority of settings is

    - init params, e.g., those passed from the CLI
    - environment variables prefixed with `HADALIZED_`
    - environment variables in `./hadalized.env` prefixxed with `HADALIZED_`
    - environment variables in `./.env` prefixxed with `HADALIZED_`
    - settings in `./hadalized.toml`
    - settings in `$XDG_CONFIG_DIR/hadalized/config.toml`
    """

    model_config = SettingsConfigDict(
        frozen=True,
        env_file=[".env", "hadalized.env"],
        env_file_encoding="utf-8",
        # The env_nested_delimiter=_ and max_split=1 means
        # HADALIZED_OPTS_CACHE_DIR == Config.opts.cache_dir
        # otherwise with delimiter=__ we would need to pass
        # HADALIZED_OPTS__CACHE_DIR
        env_nested_delimiter="_",
        env_nested_max_split=1,
        env_prefix="hadalized_",
        env_parse_none_str="null",
        env_parse_enums=True,
        # env_ignore_empty=True,
        extra="forbid",
        nested_model_default_partial_update=True,
        toml_file=[homedirs.config() / "config.toml", "hadalized.toml"],
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Set source loading priority.

        Returns:
            Priority order in which config settings are loaded.

        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def load_config(opt: Options | None = None) -> Config:
    """Load a configuration instance with the cli options merged in.

    Handles the cases when a user specifies a specific user config file
    or when only the default configuration should be used.

    Args:
        opt: Options that determine which configuration sources are utilized.

    Returns:
        A Config or UserConfig instance.

    """
    if opt is None:
        config = UserConfig()
    elif opt.config_file is not None:
        import tomllib

        data = opt.config_file.read_text()
        config = Config.model_validate(tomllib.loads(data)) | opt
    elif opt.no_config:
        config = Config() | opt
    else:
        config = UserConfig() | opt
    return config.parse_palettes() if config.parse else config
