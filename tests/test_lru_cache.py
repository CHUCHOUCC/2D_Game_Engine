import threading

import pytest

from app.structures import LRUCache


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_empty_cache_returns_the_default():
    cache = LRUCache(capacity=2)
    assert cache.get("missing") is None
    assert cache.get("missing", "default") == "default"
    assert len(cache) == 0


def test_put_and_get_and_overwrite():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("a", 2)
    assert cache.get("a") == 2
    assert len(cache) == 1


def test_full_cache_evicts_the_least_recently_used():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")          # a is now the most recently used
    cache.put("c", 3)       # b is evicted
    assert "b" not in cache
    assert cache.keys() == ["c", "a"]
    assert cache.evictions == 1


def test_entries_expire_after_their_ttl():
    clock = FakeClock()
    cache = LRUCache(capacity=4, ttl_seconds=10, clock=clock)
    cache.put("a", 1)
    cache.put("b", 2, ttl_seconds=60)
    clock.now = 9.9
    assert cache.get("a") == 1
    clock.now = 10
    assert cache.get("a") is None          # expired entries are never served
    assert "a" not in cache
    assert cache.get("b") == 2


def test_purge_removes_only_expired_entries():
    clock = FakeClock()
    cache = LRUCache(capacity=4, ttl_seconds=5, clock=clock)
    cache.put("old", 1)
    clock.now = 4
    cache.put("new", 2)
    clock.now = 6
    assert cache.purge_expired() == 1
    assert cache.keys() == ["new"]


def test_get_or_load_calls_the_loader_once():
    cache = LRUCache(capacity=4)
    count = {"n": 0}

    def loader():
        count["n"] += 1
        return "value"

    assert cache.get_or_load("k", loader) == "value"
    assert cache.get_or_load("k", loader) == "value"
    assert count["n"] == 1
    assert cache.stats()["hits"] == 1


def test_get_or_load_caches_falsy_values():
    cache = LRUCache(capacity=4)
    count = {"n": 0}

    def loader():
        count["n"] += 1
        return []

    cache.get_or_load("empty", loader)
    cache.get_or_load("empty", loader)
    assert count["n"] == 1


def test_delete_and_clear():
    cache = LRUCache(capacity=4)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.delete("a") is True
    assert cache.delete("a") is False
    cache.clear()
    assert len(cache) == 0 and cache.keys() == []
    cache.put("c", 3)
    assert cache.keys() == ["c"]


def test_stats_report_hit_rate():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.get("a")
    cache.get("b")
    assert cache.stats() == {"size": 1, "capacity": 2, "hits": 1, "misses": 1, "evictions": 0, "hit_rate": 0.5}


def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        LRUCache(capacity=0)


def test_concurrent_access_keeps_the_size_limit():
    cache = LRUCache(capacity=50)

    def worker(offset):
        for i in range(500):
            cache.put((offset, i % 80), i)
            cache.get((offset, (i * 7) % 80))

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(cache) <= 50
    assert len(cache.keys()) == len(cache)


def test_lazy_connection_opens_only_when_used():
    from app.database import LazyConnection

    opened = {"n": 0}

    class FakeConnection:
        def execute(self, sql, params=None):
            return sql

        def commit(self):
            opened["committed"] = True

        def rollback(self):
            opened["rolled_back"] = True

        def close(self):
            opened["closed"] = True

    def factory():
        opened["n"] += 1
        return FakeConnection()

    idle = LazyConnection(factory)
    idle.finish(failed=False)
    assert opened["n"] == 0 and not idle.opened

    used = LazyConnection(factory)
    assert used.execute("select 1") == "select 1"
    used.execute("select 2")
    used.finish(failed=False)
    assert opened == {"n": 1, "committed": True, "closed": True}
