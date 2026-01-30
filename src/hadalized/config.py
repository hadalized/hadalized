"""Module containing all underlying color definitions and gamut info."""

from enum import StrEnum, auto
from pathlib import Path
from typing import Self

from pydantic import Field, PrivateAttr

from hadalized import homedirs
from hadalized.base import BaseNode
from hadalized.color import Bases, ColorFieldType, Hues, Ref
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
        base=Bases.dark() | Bases(
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
        base=day.base | Bases(
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

    def model_post_init(self, context, /) -> None:
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
    """Build subdir where theme files are placed. Defaults to `name`."""
    template: str
    """Template filename relative to the templates directory."""
    filename: str = Field(
        default="",
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
    """The underlying context type to pass to the template. """
    color_type: ColorFieldType = ColorFieldType.hex
    """How each Palette should be transformed when presented as context
    to the template."""
    _fname: str = PrivateAttr(default="")

    def model_post_init(self, context, /) -> None:
        """Construct filename template."""
        filename = self.filename
        if not self.filename:
            if self.context_type == ContextType.palette:
                filename = "{context.name}.{template_ext}"
            else:
                filename = self.template

        # Infer extension from template file extension.
        if filename.endswith("{template_ext}"):
            _, _, ext = self.template.rpartition(".")
            filename = filename.replace("{template_ext}", ext)
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
            template="neovim.lua",
        ),
        "wezterm": BuildConfig(
            name="wezterm",
            template="wezterm.toml",
        ),
        "starship": BuildConfig(
            name="starship",
            template="starship.toml",
            context_type=ContextType.full,
        ),
        # "info": BuildConfig(
        #     name="info",
        #     template="palette_info.json",
        #     color_type=ColorFieldType.identity,
        # ),
        "html-samples": BuildConfig(
            name="html-samples",
            template="palette.html",
            color_type=ColorFieldType.css,
        ),
    }


class Config(BaseNode):
    """App configuration.

    Contains information about which app theme files to generate and where
    to write the build artifacts.
    """

    verbose: bool = False
    build_dir: Path = Field(default_factory=homedirs.build)
    """Directory containing built theme files."""
    cache_dir: Path = Field(default_factory=homedirs.cache)
    cache_in_memory: bool = False
    disable_cache: bool = False
    """Application cache directory. Set to `None` to use an in-memory cache."""
    template_dir: Path = Field(default_factory=homedirs.template)
    """Directory where templates will be searched for. If a template is not
    found in this directory, it will be loaded from those defined in the
    package."""
    builds: dict[str, BuildConfig] = default_builds()
    """Build directives specifying how and which theme files are
    generated."""
    palettes: dict[str, Palette] = default_palettes()
    """Palette definitions."""
    terminal: TerminalConfig = TerminalConfig()
    _palette_lu: dict[str, Palette] = PrivateAttr(default={})

    def model_post_init(self, context, /) -> None:
        """Set lookups."""
        for key, palette in self.palettes.items():
            self._palette_lu[key] = palette
            for alias in palette.aliases:
                self._palette_lu[alias] = palette
        return super().model_post_init(context)

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
