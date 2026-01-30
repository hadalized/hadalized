from hadalized import homedirs


def test_homedirs():
    assert homedirs.build()
    assert homedirs.cache()
    assert homedirs.config()
    assert homedirs.template()
    assert homedirs.state()
    assert homedirs.data()
