import pytest

from hadalized.cache import Cache, Options


@pytest.fixture
def cache(tmp_path) -> Cache:
    opt = Options(cache_dir=tmp_path)
    return Cache(opt)


def test_add_and_delete(cache: Cache):
    with cache:
        path = "test.txt"
        cache.add(path, "123")
        assert cache.get(path) == "123"
        cache.delete(path)
        assert cache.get(path) is None


def test_add_and_delete_in_memory():
    with Cache(Options(cache_in_memory=True)) as cache:
        path = "test.txt"
        cache.add(path, "123")
        assert cache.get(path) == "123"
        cache.delete(path)
        assert cache.get(path) is None


def test_exit_with_error():
    with pytest.raises(ValueError), Cache(Options(cache_in_memory=True)):
        raise ValueError("bomb")
