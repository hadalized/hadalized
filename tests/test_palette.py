import pytest

from hadalized.color import ColorFieldType
from hadalized.palette import Palette


def test_palette_parse_is_idempotent(palette: Palette):
    assert palette.parse().parse() is palette.parse()


def test_palette_to_chained_error(palette: Palette):
    with pytest.raises(TypeError):
        palette.to("hex").to("hex")


def test_palette_to_info(raw_palette: Palette):
    parsed = raw_palette.to(ColorFieldType.info)
    assert parsed._is_parsed
    assert parsed.to(ColorFieldType.info) is parsed


def test_palette_to_hex(palette: Palette):
    val = palette.to(ColorFieldType.hex)
    leaf = val.hue.red
    assert val.hue.field_type == ColorFieldType.hex
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)
    assert leaf.startswith("#")


def test_palette_to_css(palette: Palette):
    val = palette.to("css")
    leaf = val.hue.red
    assert val.hue.field_type == ColorFieldType.css
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)


def test_palette_to_oklch(palette: Palette):
    val = palette.to("oklch")
    leaf = val.hue.red
    assert val.hue.field_type == ColorFieldType.oklch
    assert isinstance(val, Palette)
    assert isinstance(leaf, str)
    assert leaf.startswith("oklch")


def test_node_properties(palette: Palette):
    assert palette.meta
    assert palette.colors
