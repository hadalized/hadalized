import pytest

from hadalized.color import ColorInfo, ColorFieldType, parse, extractor

from coloraide import Color


def test_parse_oklch():
    val = "oklch(0.5 0.1 25)"
    assert parse(val, "srgb").oklch == val


def test_parse_rgb():
    assert parse("rgb(0.5 0.5 0.5)", "srgb")


def test_parse_fail():
    with pytest.raises(ValueError):
        parse("bad color", "srgb")


def test_parse_is_in_gamut():
    assert parse("oklch(0.5 0.1 25)", "srgb").is_in_gamut
    assert parse("oklch(0.6 0.2 25)", "display-p3").is_in_gamut
    assert not parse("oklch(0.6 0.5 25)", "srgb").is_in_gamut


def test_color_info_color_property():
    val = parse("oklch(0.5 0.2 25)", "srgb")
    assert isinstance(val.color(), Color)


def test_color_info_color_prop_from_unparsed():
    val = ColorInfo(
        raw="rgb(0.5 0.5 0.5)",
        gamut="srgb",
        oklch="",
        raw_oklch="",
        hex="",
        css="",
        is_in_gamut=True,
        max_oklch_chroma=0.5,
    )
    assert isinstance(val.color(), Color)


def test_color_info_bad_def():
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


def test_extract_on_str_input():
    func = extractor(ColorFieldType.hex)
    assert func("extracted") == "extracted"


def test_extractor_on_color():
    color = parse("oklch(0.5 0.2 25)", "srgb")
    assert extractor("hex")(color) == color.hex
    assert extractor("css")(color) == color.css
    assert extractor("oklch")(color) == color.oklch
    assert extractor(ColorFieldType.identity)(color) == color
