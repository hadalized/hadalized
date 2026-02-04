"""Schema for a color palette.

A palette is the primary context used to render a color theme.
"""

from typing import Literal, Self

from pydantic import Field, PrivateAttr

from hadalized.base import BaseNode
from hadalized.color import (
    Bases,
    ColorFieldHandler,
    ColorFieldType,
    ColorMap,
    Extractor,
    Grayscale,
    Hues,
    Parser,
)


class PaletteMeta(BaseNode):
    """Palette metadata."""

    name: str
    desc: str
    version: str = "2.1"
    """Version of the palette color definitions."""
    mode: Literal["dark", "light"]
    """Whether the theme is dark or light mode."""
    gamut: str = "srgb"
    """Gamut to fit to when parsing."""
    aliases: list[str] = Field(default=[])
    """Palette aliases."""


class PaletteColors(BaseNode):
    """Palette color maps."""

    hue: Hues
    """Named main color hues."""
    base: Bases
    """Named bases relative to the palette."""
    bright: Hues = Hues.bright()
    """Named bright color variants."""
    hl: Hues = Hues.highlights()
    """Name highlight color variants."""
    gs: Grayscale = Grayscale()
    """Grayscale colors."""


class Palette(PaletteColors, PaletteMeta):
    """A collection of hues and bases.

    The primary data structure used to render an application theme template.
    """

    _cache: dict = PrivateAttr(default={})
    _meta: PaletteMeta | None = PrivateAttr(default=None)
    _colors: PaletteColors | None = PrivateAttr(default=None)
    _is_parsed: bool = PrivateAttr(default=False)
    """Indicates the underlying colortype is ColorInfo."""
    # TODO: We might want to make the typing here explicit.

    @property
    def meta(self) -> PaletteMeta:
        """Palette metadata."""
        if self._meta is None:
            self._meta = PaletteMeta.model_validate({
                k: v for k, v in self if not isinstance(v, ColorMap)
            })
        return self._meta

    @property
    def colors(self) -> PaletteColors:
        """Palette color maps."""
        if self._colors is None:
            self._colors = PaletteColors.model_validate({
                k: v for k, v in self if isinstance(v, ColorMap)
            })
        return self._colors

    def map(self, handler: ColorFieldHandler) -> Self:
        """Map a handler accross color fields.

        Returns:
            A new Palette instance with the handler applied to each
            field that contains a ColorMap instance.

        """
        return self.model_validate({
            k: v.map(handler) if isinstance(v, ColorMap) else v for k, v in self
        })

    def to(self, color_type: ColorFieldType | str) -> Self:
        """Entry point for the `map` method that accepts a directive.

        When called on an unparsed instance, a new parsed instance is created
        and acted on.

        Usage:
            palette = palette.to("hex")

        Returns:
            A new Palette instance with the handler applied to each
            field that contains a ColorMap instance.

        """
        inst = self if self._is_parsed else self.parse()
        if color_type == ColorFieldType.info:
            return inst
        if (pal := inst._cache.get(color_type)) is None:
            pal = self.map(Extractor(color_type))
            inst._cache[color_type] = pal
        return pal

    def parse(self, gamut: str | None = None) -> Self:
        """Parse each colormap.

        Returns:
            A new instance where each ColorMap field is parsed to contain
            full ColorInfo values.

        """
        gamut = gamut or self.gamut
        if self._is_parsed and gamut == self.gamut:
            out = self
        else:
            parser = Parser(gamut=gamut)
            out = self.map(parser)
            out._is_parsed = True
        return out
