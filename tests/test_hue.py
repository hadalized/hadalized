import pytest

from hadalized.color import Hue, HueAlias


def test_hue_alias():
    assert HueAlias()
    with pytest.raises(ValueError):
        HueAlias(c1=Hue.red)
