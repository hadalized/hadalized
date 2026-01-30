from typing import TYPE_CHECKING

import pytest

from hadalized.color import parse

if TYPE_CHECKING:
    pass


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
