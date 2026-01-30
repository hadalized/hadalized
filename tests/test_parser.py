from typing import TYPE_CHECKING

import pytest

from hadalized.color import Parser, parse

if TYPE_CHECKING:
    pass


def test_parse_oklch():
    parser = Parser("srgb")
    val = "oklch(0.5 0.1 25)"
    info = parser(val)
    assert info.oklch == val
    assert parser(info) is info


def test_parse_rgb():
    assert parse("rgb(0.5 0.5 0.5)")


def test_parse_fail():
    with pytest.raises(ValueError):
        parse("bad color")


@pytest.mark.parametrize(
    "val,gamut,in_gamut",
    [
        ("oklch(0.60 0.4 25)", "srgb", False),
        ("oklch(0.60 0.1 25)", "srgb", True),
    ],
)
def test_in_gamut(val: str, gamut: str, in_gamut: bool):
    color = parse(val, gamut=gamut)
    assert color.is_in_gamut is in_gamut
    if not in_gamut:
        assert color.oklch != color.raw_oklch


def test_max_oklch():
    parser = Parser("srgb")
    val = "oklch(0.5 0.5 25)"
    color = parser(val).color().convert("srgb")
    assert parser._max_oklch_chroma(color) < 0.5
