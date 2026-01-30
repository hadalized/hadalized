"""Module containing all underlying color definitions and gamut info."""

from enum import StrEnum, auto
from pathlib import Path
from typing import Self

from pydantic import Field, PrivateAttr

from hadalized import homedirs
from hadalized.color import ColorMap
from hadalized.palette import (
    BaseNode,
    Bases,
    ColorField,
    ColorFieldType,
    Hues,
    Palette,
)


class Ref(ColorMap):
    """Container for named color refs used in foregrounds and backgrounds."""

    black: ColorField = "oklch(0.10 0.01 220)"
    darkgray: ColorField = "oklch(0.30 0.01 220)"
    darkslategray: ColorField = "oklch(0.30 0.03 220)"
    gray: ColorField = "oklch(0.50 0.01 220)"
    slategray: ColorField = "oklch(0.600 0.03 220)"
    lightgray: ColorField = "oklch(0.70 0.01 220)"
    lightslategray: ColorField = "oklch(0.700 0.02 220)"
    white: ColorField = "oklch(0.995 0.01 220)"
    b12: ColorField = "oklch(0.125 0.025 220)"
    b13: ColorField = "oklch(0.135 0.025 220)"
    b16: ColorField = "oklch(0.1625 0.025 220)"
    b20: ColorField = "oklch(0.200 .030 220)"
    b25: ColorField = "oklch(0.250 .030 220)"
    b30: ColorField = "oklch(0.300 .035 220)"
    b35: ColorField = "oklch(0.350 .035 220)"
    g20: ColorField = "oklch(0.200 .010 220)"
    g30: ColorField = "oklch(0.300 .010 220)"
    g35: ColorField = "oklch(0.350 .010 220)"
    g45: ColorField = "oklch(0.450 .010 220)"
    g60: ColorField = "oklch(0.600 .010 220)"
    g65: ColorField = "oklch(0.650 .010 220)"
    g70: ColorField = "oklch(0.700 .010 220)"
    g75: ColorField = "oklch(0.750 .010 220)"
    g80: ColorField = "oklch(0.800 .010 220)"
    g90: ColorField = "oklch(0.900 .010 220)"
    s80: ColorField = "oklch(0.800 .020 100)"
    s85: ColorField = "oklch(0.850 .020 100)"
    s90: ColorField = "oklch(0.900 .020 100)"
    s91: ColorField = "oklch(0.910 .020 100)"
    s92: ColorField = "oklch(0.925 .020 100)"
    s95: ColorField = "oklch(0.950 .020 100)"
    s97: ColorField = "oklch(0.975 .015 100)"
    s99: ColorField = "oklch(0.990 .010 100)"
    s100: ColorField = "oklch(0.995 .010 100)"
    w80: ColorField = "oklch(0.800 .005 100)"
    w85: ColorField = "oklch(0.850 .005 100)"
    w90: ColorField = "oklch(0.900 .005 100)"
    w91: ColorField = "oklch(0.910 .005 100)"
    w92: ColorField = "oklch(0.925 .005 100)"
    w95: ColorField = "oklch(0.950 .005 100)"
    w97: ColorField = "oklch(0.975 .005 100)"
    w99: ColorField = "oklch(0.990 .005 100)"
    w100: ColorField = "oklch(0.995 .005 100)"


hues: dict[str, Hues] = {
    "neutral": Hues(
        red="oklch(0.575 0.185 25)",
        orange="oklch(0.650 0.150 60)",
        yellow="oklch(0.675 0.120 100)",
        lime="oklch(0.650 0.130 115)",
        green="oklch(0.575 0.165 130)",
        mint="oklch(0.675 0.130 155)",
        cyan="oklch(0.625 0.100 180)",
        azure="oklch(0.675 0.110 225)",
        blue="oklch(0.575 0.140 250)",
        violet="oklch(0.575 0.185 290)",
        magenta="oklch(0.575 0.185 330)",
        rose="oklch(0.675 0.100 360)",
    ),
    "dark": Hues(
        red="oklch(0.60 0.185 25)",
        orange="oklch(0.650 0.150 60)",
        yellow="oklch(0.700 0.120 100)",
        lime="oklch(0.675 0.120 115)",
        green="oklch(0.650 0.165 130)",
        mint="oklch(0.715 0.130 155)",
        cyan="oklch(0.650 0.100 180)",
        azure="oklch(0.725 0.110 225)",
        blue="oklch(0.625 0.150 250)",
        violet="oklch(0.625 0.185 290)",
        magenta="oklch(0.625 0.185 330)",
        rose="oklch(0.700 0.100 360)",
    ),
    "light": Hues(
        red="oklch(0.550 0.185 25)",
        orange="oklch(0.650 0.150 60)",
        yellow="oklch(0.650 0.120 100)",
        lime="oklch(0.650 0.130 115)",
        green="oklch(0.575 0.165 130)",
        mint="oklch(0.650 0.130 155)",
        cyan="oklch(0.550 0.100 180)",
        azure="oklch(0.650 0.110 225)",
        blue="oklch(0.575 0.140 250)",
        violet="oklch(0.550 0.185 290)",
        magenta="oklch(0.550 0.185 330)",
        rose="oklch(0.625 0.100 360)",
    ),
    "hl": Hues(
        red="oklch(0.800 0.100 25)",
        orange="oklch(0.850 0.100 60)",
        yellow="oklch(0.950 0.200 100)",
        lime="oklch(0.855 0.100 115)",
        green="oklch(0.85 0.100 130)",
        mint="oklch(0.875 0.100 155)",
        cyan="oklch(0.900 0.100 180)",
        azure="oklch(0.875 0.100 225)",
        blue="oklch(0.825 0.100 250)",
        violet="oklch(0.825 0.200 290)",
        magenta="oklch(0.825 0.200 330)",
        rose="oklch(0.825 0.200 360)",
    ),
    "bright": Hues(
        red="oklch(0.675 0.200 25)",
        orange="oklch(0.75 0.175 60)",
        yellow="oklch(0.80 0.165 100)",
        lime="oklch(0.800 0.185 120)",
        green="oklch(0.800 0.200 135)",
        mint="oklch(0.800 0.195 155)",
        cyan="oklch(0.800 0.145 180)",
        azure="oklch(0.800 0.135 225)",
        blue="oklch(0.800 0.100 250)",
        violet="oklch(0.800 0.100 290)",
        magenta="oklch(0.800 0.185 330)",
        rose="oklch(0.800 0.120 360)",
    ),
}


def default_palettes() -> dict[str, Palette]:
    """Lazily compute default palette colors.

    Returns:
        A map of palette.name -> palette.

    """
    ref = Ref()

    # Palette definitions
    dark: Palette = Palette(
        name="hadalized",
        desc="Main dark theme with blueish solarized inspired backgrounds.",
        mode="dark",
        gamut="srgb",
        aliases=["dark"],
        hue=hues["dark"],
        bright=hues["bright"],
        hl=hues["hl"],
        base=Bases(
            bg="oklch(0.13 0.025 220)",
            bg1="oklch(0.14 0.03 220)",
            bg2=ref.b16,
            bg3=ref.b20,
            bg4=ref.b25,
            bg5=ref.b30,
            bg6=ref.b35,
            hidden=ref.g45,
            subfg=ref.g70,
            fg=ref.w80,
            emph=ref.w85,
            op2=ref.s80,
            op1=ref.s85,
            op=ref.s90,
        ),
    )

    gray: Palette = Palette(
        name="hadalized-gray",
        desc="Dark theme variant with more grayish backgrounds.",
        mode="dark",
        gamut=dark.gamut,
        aliases=["gray"],
        hue=dark.hue,
        bright=dark.bright,
        hl=dark.hl,
        base=Bases(
            bg="oklch(0.13 0.005 220)",
            bg1="oklch(0.14 0.005 220)",
            bg2="oklch(0.16 0.005 220)",
            bg3="oklch(0.20 0.005 220)",
            bg4="oklch(0.25 0.005 220)",
            bg5="oklch(0.30 0.005 220)",
            bg6="oklch(0.35 0.005 220)",
            hidden=dark.base.hidden,
            subfg=dark.base.subfg,
            fg=dark.base.fg,
            emph=dark.base.emph,
            op2=ref.w80,
            op1=ref.w85,
            op=ref.w90,
        ),
    )

    day: Palette = Palette(
        name="hadalized-day",
        desc="Light theme variant with sunny backgrounds.",
        mode="light",
        gamut="srgb",
        aliases=["day"],
        hue=hues["light"],
        bright=hues["bright"],
        hl=hues["hl"],
        base=Bases(
            bg=ref.s100,
            bg1=ref.s99,
            bg2=ref.s95,
            bg3=ref.s92,
            bg4=ref.s99,
            bg5=ref.s85,
            bg6=ref.s80,
            hidden=ref.g75,
            subfg=ref.g60,
            fg=ref.g30,
            emph=ref.g20,
            op2=dark.base.bg3,
            op1=dark.base.bg2,
            op=dark.base.bg,
        ),
    )

    white: Palette = Palette(
        name="hadalized-white",
        desc="Light theme variant with whiter backgrounds.",
        mode="light",
        gamut=day.gamut,
        aliases=["white"],
        hue=day.hue,
        bright=day.bright,
        hl=day.hl,
        base=Bases(
            bg=ref.w100,
            bg1=ref.w99,
            bg2=ref.w95,
            bg3=ref.w92,
            bg4=ref.w99,
            bg5=ref.w85,
            bg6=ref.w80,
            hidden=day.base.hidden,
            subfg=day.base.subfg,
            fg=day.base.fg,
            emph=day.base.emph,
            op2=day.base.op2,
            op1=day.base.op1,
            op=day.base.op,
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
            "{palette.name}.{template.ext}",  # default
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
