"""Color string parsing and information extraction."""

from collections.abc import Callable
from enum import StrEnum, auto
from typing import Self

from coloraide import Color as ColorBase
from pydantic import Field, PrivateAttr

from hadalized.base import BaseNode

type ColorField = ColorInfo | str
"""A field value containing either full ColorInfo for a specific space / gamut
parseable string representation of a color."""

type ColorFieldStr = str

type ColorFieldHandler = Callable[[ColorField], ColorField]
"""A function that can be mapped across"""


class Ref:
    """Color definitions references."""

    black: ColorField = "oklch(0.10 0.01 220)"
    darkgray: ColorField = "oklch(0.30 0.01 220)"
    darkslategray: ColorField = "oklch(0.30 0.03 220)"
    gray: ColorField = "oklch(0.50 0.01 220)"
    slategray: ColorField = "oklch(0.600 0.03 220)"
    lightgray: ColorField = "oklch(0.70 0.01 220)"
    lightslategray: ColorField = "oklch(0.700 0.02 220)"
    white: ColorField = "oklch(0.995 0.01 220)"
    # blues, high chroma
    b12: ColorField = "oklch(0.125 0.030 220)"
    b13: ColorField = "oklch(0.130 0.030 220)"
    b14: ColorField = "oklch(0.140 0.030 220)"
    b16: ColorField = "oklch(0.1625 0.030 220)"
    b20: ColorField = "oklch(0.200 .030 220)"
    b25: ColorField = "oklch(0.250 .030 220)"
    b30: ColorField = "oklch(0.300 .035 220)"
    b35: ColorField = "oklch(0.350 .035 220)"
    # grays, mid chroma
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
    # Sun / Day high chroma
    s80: ColorField = "oklch(0.800 .020 100)"
    s85: ColorField = "oklch(0.850 .020 100)"
    s90: ColorField = "oklch(0.900 .020 100)"
    s91: ColorField = "oklch(0.910 .020 100)"
    s92: ColorField = "oklch(0.925 .020 100)"
    s95: ColorField = "oklch(0.950 .020 100)"
    s97: ColorField = "oklch(0.975 .015 100)"
    s99: ColorField = "oklch(0.990 .010 100)"
    s100: ColorField = "oklch(0.995 .010 100)"
    # whites, low chroma
    w13: ColorField = "oklch(0.13 0.005 220)"
    w14: ColorField = "oklch(0.14 0.005 220)"
    w16: ColorField = "oklch(0.16 0.005 220)"
    w20: ColorField = "oklch(0.20 0.005 220)"
    w25: ColorField = "oklch(0.25 0.005 220)"
    w30: ColorField = "oklch(0.30 0.005 220)"
    w35: ColorField = "oklch(0.35 0.005 220)"
    w80: ColorField = "oklch(0.800 .005 100)"
    w85: ColorField = "oklch(0.850 .005 100)"
    w90: ColorField = "oklch(0.900 .005 100)"
    w91: ColorField = "oklch(0.910 .005 100)"
    w92: ColorField = "oklch(0.925 .005 100)"
    w95: ColorField = "oklch(0.950 .005 100)"
    w97: ColorField = "oklch(0.975 .005 100)"
    w99: ColorField = "oklch(0.990 .005 100)"
    w100: ColorField = "oklch(0.995 .005 100)"


class ColorSpace(StrEnum):
    """Colorspace constants."""

    srgb = auto()
    display_p3 = "display-p3"
    oklch = auto()


class ColorFieldType(StrEnum):
    """Constants representing nodes in a ColorInfo object.

    Use in build directives to declaratively apply transformations to
    Palette ColorMap fields.
    """

    info = auto()
    """Indicates a ColorField is a ``ColorInfo`` instance."""
    hex = auto()
    """Indicates a ColorField should be a RGB hex code in a specified gamut."""
    oklch = auto()
    """Indicates a ColorField should be a oklch css code in a specified gamut."""
    css = auto()
    """Indicates a ColorField should be a css code in a specified gamut."""


class ColorInfo(BaseNode):
    """Detailed information about a specific color.

    Use the `parse` function to instantiate an instance rather than doing so
    directly to ensure the raw value is parseable.
    """

    raw: str = Field(examples=["oklch(0.6 0.2 25)", "#010203"])
    # parsed: ColorBase = Field(exclude=True)
    """Parseable color definition, e.g., a css value."""
    gamut: str = Field(
        default=ColorSpace.srgb,
        examples=["srgb", "display-p3"],
    )
    """Target gamut to fit the raw color definition to."""
    raw_oklch: ColorFieldStr
    """Raw input in the oklch colorspace."""
    oklch: ColorFieldStr
    """OKLCH value fit to the specified `gamut`."""
    css: ColorFieldStr
    """CSS value in the gamut."""
    hex: ColorFieldStr
    """24 or 32-bit hex representation for RGB gamuts."""
    is_in_gamut: bool
    """Indicates whether the raw value is within the color gamut."""
    max_oklch_chroma: float
    """The maximum oklch chroma value determined from the fit method."""
    _color: ColorBase | None = PrivateAttr(None)
    """Parsed instance."""

    def color(self) -> ColorBase:
        """Coloraide.Color object parsed from the definition.

        Returns:
            A coloraide.Color instance.

        """
        if self._color is None:
            self._color = ColorBase(self.raw)
        return self._color


class Parser:
    """Parse raw color strings."""

    def __init__(self, gamut: str = ColorSpace.srgb, fit_method: str = "raytrace"):
        """Set gamut and fit method."""
        self.gamut = gamut
        self.fit_method = fit_method

    @staticmethod
    def _to_hex(val: ColorBase) -> str:
        """Convert RGB to their corresponding 24-bit or 34-bit hex color code.

        Used primarily to extract a hex code for use
        in programs--such as neovim--that only allow specifying colors
        via RGB channels.

        Returns:
            A hex color code.

        """
        if val.space() != ColorSpace.srgb:
            val = ColorBase(ColorSpace.srgb, val.coords(), alpha=val.alpha())
        return val.to_string(hex=True)

    def _fit(self, val: ColorBase) -> ColorBase:
        return val.clone().fit(self.gamut, method=self.fit_method)

    def _max_oklch_chroma(self, val: ColorBase) -> float:
        """Determine maximum OKLCH chroma in the gamut for fixed lightness and hue.

        Returns:
            OKLCH chroma value.

        """
        if val.space() != ColorSpace.oklch:
            val = val.convert("oklch")
        lightness, _, hue = val.coords()
        cmax = ColorBase("oklch", (lightness, 0.4, hue))
        return self._fit(cmax).get("chroma")

    def __call__(self, val: ColorField) -> ColorInfo:
        """Parse a string representation of a color.

        Returns:
            A ColorInfo instance parsed from the input string. Raises a
            ValueError if the input is not parseable.

        """
        if isinstance(val, ColorInfo):
            return val
        raw_color = ColorBase(val)
        if raw_color.space() != ColorSpace.oklch:
            raw_oklch = raw_color.convert(ColorSpace.oklch)
        else:
            raw_oklch = raw_color

        oklch_fit = self._fit(raw_oklch)
        color = oklch_fit.convert(self.gamut)

        inst = ColorInfo(
            raw=val,
            raw_oklch=raw_oklch.to_string(),
            gamut=self.gamut,
            oklch=oklch_fit.to_string(),
            css=color.to_string(),
            hex=self._to_hex(color),
            is_in_gamut=raw_oklch.convert(self.gamut).in_gamut(),
            max_oklch_chroma=self._max_oklch_chroma(raw_oklch),
        )
        inst._color = raw_color
        return inst


class Extractor:
    """A ColorFieldHandler that extracts ``ColorInfo`` field values.

    Attrs:
        field (ColorFieldType): Which field will be extracted.
        is_identity: Indicates whether the extractor is the identity function.

    """

    def __init__(self, field: str | ColorFieldType):
        """Validate input as a ColorFieldType."""
        self.field = ColorFieldType(field)
        self.is_identity = self.field == ColorFieldType.info

    def __call__(self, val: ColorField) -> ColorField:
        """Extract field value from the input.

        Calling twice results in a TypeError, to avoid uncaught errors
        when chaining extractors. An expection is when the extractor
        represents the identity function.

        Raises:
            TypeError: When the input is not a ``ColorInfo`` instance.

        Returns:
            A ``ColorInfo`` field value defined by the ``field`` attr
            or the ColorInfo instance itself in case when the extractor is
            the identity function.

        """
        if not isinstance(val, ColorInfo):
            clsname = ColorInfo.__name__
            raise TypeError(f"Input type {type(val)} is not a {clsname} instance.")
        return val if self.is_identity else val[self.field]


class Hue(StrEnum):
    """Named hues. These represent the fields of a ``Hues`` instance."""

    red = auto()
    orange = auto()
    yellow = auto()
    lime = auto()
    green = auto()
    mint = auto()
    cyan = auto()
    azure = auto()
    blue = auto()
    violet = auto()
    magenta = auto()
    rose = auto()

    @staticmethod
    def get(index: int) -> Hue:
        """Get a Hue color by integer index.

        Returns:
            Hue value corresponding to the index.

        """
        return _hue_lu[index]


_hue_lu = (
    Hue.red,  # 0
    Hue.orange,  # 1
    Hue.yellow,  # 2
    Hue.lime,  # 3
    Hue.green,  # 4
    Hue.mint,  # 5
    Hue.cyan,  # 6
    Hue.azure,  # 7
    Hue.blue,  # 8
    Hue.violet,  # 9
    Hue.magenta,  # 10, A
    Hue.rose,  # 11, B
)


class HueAlias(BaseNode):
    """A mapping from indexed color names to ``Hues`` fields."""

    c0: Hue = Hue.get(0)
    c1: Hue = Hue.get(1)
    c2: Hue = Hue.get(2)
    c3: Hue = Hue.get(3)
    c4: Hue = Hue.get(4)
    c5: Hue = Hue.get(5)
    c6: Hue = Hue.get(6)
    c7: Hue = Hue.get(7)
    c8: Hue = Hue.get(8)
    c9: Hue = Hue.get(9)
    ca: Hue = Hue.get(0xA)
    cb: Hue = Hue.get(0xB)

    def model_post_init(self, context, /) -> None:
        """Validate each Hue appears exactly once.

        Raises:
            ValueError: If there are not the same number of values as field names.

        """
        required_len = len(self)
        vals = (v for _, v in self)
        if len(set(vals)) != required_len:
            raise ValueError(f"Instance must contain {required_len} unique values.")
        return super().model_post_init(context)


class ColorMap(BaseNode):
    """Base dataclass for mappings of the form color name -> ColorInfo.

    The fields can either be a complete object containing data for all
    gamuts, gamut specific color info, or a string. While the model itself
    does not enforce uniformity of type among the strings, the data structure
    should typically be equivalent to one of
        Mapping[str, ColorInfo]
        Mapping[str, GamutColor]
        Mapping[str, str]
    Instances containing values other than ColorInfo are obtained via transform
    methods.
    """

    _field_type: ColorFieldType | None = PrivateAttr(default=None)

    @property
    def field_type(self) -> ColorFieldType | None:
        """What the field values represent."""
        return self._field_type

    def map(self, handler: ColorFieldHandler) -> Self:
        """Apply a generic color field handler to each field.

        Example handlers enclude
        - field extractors, e.g., mapping a parsed instance to specific field
        - parsers, to convert from string color definitions to ColorInfo fields

        Returns:
            A new ColorMap instance with the handler applied to each field.

        """
        data: dict[str, ColorField] = {k: handler(v) for k, v in self}
        inst = self.model_validate(data)
        if isinstance(handler, Extractor):
            inst._field_type = handler.field
        elif isinstance(handler, Parser):
            inst._field_type = ColorFieldType.info
        return inst


class Hues(ColorMap):
    """Named accents.

    A ``Hues`` instance serves primarily to color text and highlights.

    """

    red: ColorField = "oklch(0.575 0.185 25)"
    orange: ColorField = "oklch(0.650 0.150 60)"
    yellow: ColorField = "oklch(0.675 0.120 100)"
    lime: ColorField = "oklch(0.650 0.130 115)"
    green: ColorField = "oklch(0.575 0.165 130)"
    mint: ColorField = "oklch(0.675 0.130 155)"
    cyan: ColorField = "oklch(0.625 0.100 180)"
    azure: ColorField = "oklch(0.675 0.110 225)"
    blue: ColorField = "oklch(0.575 0.140 250)"
    violet: ColorField = "oklch(0.575 0.185 290)"
    magenta: ColorField = "oklch(0.575 0.185 330)"
    rose: ColorField = "oklch(0.675 0.100 360)"

    # @staticmethod
    # def neutral() -> Hues:
    #     """Neutral hues.
    #
    #     Returns:
    #         A neutral mode selection of hues.
    #
    #     """
    #     return Hues()

    @staticmethod
    def dark() -> Hues:
        """Dark mode hues.

        Returns:
            A dark mode selection of hues.

        """
        return Hues(
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
        )

    @staticmethod
    def light() -> Hues:
        """Light mode hues.

        Returns:
            A light mode selection of hues.

        """
        return Hues(
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
        )

    @staticmethod
    def highlights() -> Hues:
        """Highlight hues.

        Returns:
            A selection of hues to use in highlights.

        """
        return Hues(
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
        )

    @staticmethod
    def bright() -> Hues:
        """Highlight hues.

        Returns:
            A selection of brighter hues.

        """
        return Hues(
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
        )


class Bases(ColorMap):
    """Configuration node for foregrounds and backgrounds.

    Colors are grouped primarily into

    - backgrounds (main and overlays),
    - foreground colors
    - opposite overlays
    """

    bg: ColorField = Ref.b13
    """Primary background color."""
    bg1: ColorField = Ref.b14
    """Secondary background color."""
    bg2: ColorField = Ref.b16
    """Tertiary background color."""
    bg3: ColorField = Ref.b20
    """Overlay background 1."""
    bg4: ColorField = Ref.b25
    """Overlay background 2."""
    bg5: ColorField = Ref.b30
    """Overlay background 3."""
    bg6: ColorField = Ref.b35
    """Overlay."""
    hidden: ColorField = Ref.g45
    """Strongly de-mphasized foreground text."""
    subfg: ColorField = Ref.g70
    """De-emphasized foreground text."""
    fg: ColorField = Ref.w80
    """Primary foreground text."""
    emph: ColorField = Ref.w85
    """Emphasized foreground text."""
    op2: ColorField = Ref.s80
    """Tertiary opposite background color."""
    op1: ColorField = Ref.s85
    """Secondary opposite background color."""
    op: ColorField = Ref.s90
    """Primary opposite background color."""

    @staticmethod
    def dark() -> Bases:
        """Dark mode bases.

        Returns:
            A dark mode selection of bases.

        """
        return Bases()

    @staticmethod
    def light() -> Bases:
        """Light mode bases.

        Returns:
            A dark mode selection of bases.

        """
        dark = Bases.dark()
        return Bases(
            bg=Ref.s100,
            bg1=Ref.s99,
            bg2=Ref.s95,
            bg3=Ref.s92,
            bg4=Ref.s99,
            bg5=Ref.s85,
            bg6=Ref.s80,
            hidden=Ref.g75,
            subfg=Ref.g60,
            fg=Ref.g30,
            emph=Ref.g20,
            op2=dark.bg3,
            op1=dark.bg2,
            op=dark.bg,
        )


class Grayscale(ColorMap):
    """Grayscale monochromatic named colors that are palette independent."""

    black: ColorField = "oklch(0.10 0.01 220)"
    darkgray: ColorField = "oklch(0.30 0.01 220)"
    neutralgray: ColorField = "oklch(0.50 0.01 220)"
    lightgray: ColorField = "oklch(0.70 0.01 220)"
    white: ColorField = "oklch(0.995 0.003 220)"


def parse(
    val: str,
    gamut: str = ColorSpace.srgb,
    fit_method: str = "raytrace",
) -> ColorInfo:
    """Parse a string representation of a color.

    Generate a ``Parser`` instance and call it on the input.

    Returns:
        A ColorInfo instance parsed from the input string. Raises a
        ValueError if the input is not parseable.

    """
    return Parser(gamut=gamut, fit_method=fit_method)(val)
