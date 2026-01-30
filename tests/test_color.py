import pytest

from hadalized.color import ColorInfo, ColorFieldType, parse, Extractor

from coloraide import Color


def test_color_info_color_method():
    raw = "rgb(0.5 0.5 0.5)"
    color = Color(raw)
    val = ColorInfo(
        raw=raw,
        gamut="srgb",
        oklch="",
        raw_oklch="",
        hex="",
        css="",
        is_in_gamut=True,
        max_oklch_chroma=0.5,
    )
    assert color == val.color()


def test_color_info_color_method_raises_error():
    val = ColorInfo(
        raw="bad color",
        gamut="",
        oklch="",
        raw_oklch="",
        hex="",
        css="",
        is_in_gamut=True,
        max_oklch_chroma=0.5,
    )
    with pytest.raises(ValueError):
        val.color()


def test_extractor():
    color = parse("oklch(0.5 0.2 25)")
    ident = Extractor(ColorFieldType.info)
    f_hex = Extractor("hex")
    assert ident(color) is color
    assert f_hex(color) == color.hex
    assert Extractor("css")(color) == color.css
    assert Extractor("oklch")(color) == color.oklch


def test_extractor_type_error():
    color = parse("oklch(0.5 0.2 25)")
    func = Extractor("hex")
    with pytest.raises(TypeError):
        func(func(color))
