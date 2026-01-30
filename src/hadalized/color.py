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


def _parse(val: str) -> ColorBase | None:
    """Parse an input string into a coloraide.Color instance.

    Returns:
        The color instance if parseable else None.

    """
    match = ColorBase.match(val, fullmatch=True)
    return ColorBase(match.color) if match else None


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

    identity = auto()
    """Indicates a ColorField should be a full ColorInfo instance."""
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

        Raises:
            ValueError: If `raw` is not parseable.

        Returns:
            A coloraide.Color instance.

        """
        if self._color is None:
            if (parsed := _parse(self.raw)) is None:
                raise ValueError(f"Unable to parse {self.raw=}")
            self._color = parsed
        return self._color


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

    # TODO: Add a field type?

    def map(self, handler: ColorFieldHandler) -> Self:
        """Apply a generic color field handler to each field.

        Example handlers enclude
        - field extractors, e.g., mapping a parsed instance to specific field
        - parsers, to convert from string color definitions to ColorInfo fields

        Returns:
            A new ColorMap instance with the handler applied to each field.

        """
        data: dict[str, ColorField] = {k: handler(v) for k, v in self}
        return self.model_validate(data)


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

        Raises:
            ValueError: if the input is not parseable.

        """
        if isinstance(val, ColorInfo):
            return val

        if (parsed := _parse(val)) is None:
            raise ValueError(f"Unable to parse color from {val=}")

        if parsed.space() != ColorSpace.oklch:
            raw_oklch = parsed.convert(ColorSpace.oklch)
        else:
            raw_oklch = parsed

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
        inst._color = parsed
        return inst


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


def extractor(color_type: str | ColorFieldType) -> ColorFieldHandler:
    """ColorFieldHandler factory.

    Creates a function that extracts the specified field from a ColorInfo
    instance. The handler passes strings through so that it is idempotent.

    Example:
        func = extractor("hex")
        color = parse("oklch(0.5 0.1 25)")
        assert color.hex == func(color)
        assert color.hex == func(func(color))
        identity_func = extractor("identity")
        assert identity_func(color) is color

    Returns:
        A function mapable over ColorMap instances that gets the specified
        field from a ColorInfo object.

    """
    color_type = ColorFieldType(color_type)
    is_identity = color_type == ColorFieldType.identity

    def handler(val: ColorField) -> ColorField:
        return val if is_identity or isinstance(val, str) else val[color_type]

    return handler
