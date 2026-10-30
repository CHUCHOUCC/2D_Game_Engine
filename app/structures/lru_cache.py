import threading
import time


class _Entry:
    """Doubly linked node of the cache: key, value, expiry time and both neighbours."""

    __slots__ = ("key", "value", "expires_at", "prev", "next")

    def __init__(self, key, value, expires_at):
        self.key = key
        self.value = value
        self.expires_at = expires_at
        self.prev = None
        self.next = None


class LRUCache:
    """Cache with a size limit and a time limit, built on a hash index plus a doubly linked list.

    The list keeps the entries from the most recently used (right after the head sentinel) to the
    least recently used (right before the tail sentinel). The dictionary maps each key to its node,
    so finding an entry never walks the list.
    Invariant: every key in _index has exactly one node between _head and _tail and the other way
    round; len(_index) <= capacity; the sentinels are never removed.
    Costs: get, put and delete are O(1): they only touch the dictionary and relink a few nodes.
    clear() is O(1) and purge_expired() is O(n).
    Expiry rule: an entry older than its ttl counts as absent; get() removes it and returns the
    default, so stale data is never served. Full cache rule: put() evicts the least recently used
    entry. Empty cache rule: get() returns the default; there is nothing to raise.
    Thread safety: a lock protects every operation, because FastAPI runs synchronous routes in a
    thread pool.
    """

    def __init__(self, capacity: int = 128, ttl_seconds: float | None = None, clock=time.monotonic):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._ttl = ttl_seconds
        self._clock = clock
        self._index = {}
        # Sentinels: the list is never empty, so linking needs no special cases.
        self._head = _Entry(None, None, None)
        self._tail = _Entry(None, None, None)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    # ------------------------------------------------------------------ list helpers

    def _unlink(self, entry):
        entry.prev.next = entry.next
        entry.next.prev = entry.prev
        entry.prev = entry.next = None

    def _push_front(self, entry):
        entry.prev = self._head
        entry.next = self._head.next
        self._head.next.prev = entry
        self._head.next = entry

    def _expired(self, entry) -> bool:
        return entry.expires_at is not None and self._clock() >= entry.expires_at

    # ------------------------------------------------------------------ public operations

    def get(self, key, default=None):
        with self._lock:
            entry = self._index.get(key)
            if entry is None or self._expired(entry):
                if entry is not None:
                    self._unlink(entry)
                    del self._index[key]
                self.misses += 1
                return default
            # Used now: move it to the front.
            self._unlink(entry)
            self._push_front(entry)
            self.hits += 1
            return entry.value

    def put(self, key, value, ttl_seconds: float | None = None) -> None:
        ttl = self._ttl if ttl_seconds is None else ttl_seconds
        expires_at = None if ttl is None else self._clock() + ttl
        with self._lock:
            entry = self._index.get(key)
            if entry is not None:
                entry.value = value
                entry.expires_at = expires_at
                self._unlink(entry)
                self._push_front(entry)
                return
            if len(self._index) >= self._capacity:
                # Full: the least recently used entry sits right before the tail.
                oldest = self._tail.prev
                self._unlink(oldest)
                del self._index[oldest.key]
                self.evictions += 1
            entry = _Entry(key, value, expires_at)
            self._index[key] = entry
            self._push_front(entry)

    def get_or_load(self, key, loader, ttl_seconds: float | None = None):
        """The cached value, or the result of loader() stored for next time."""
        missing = _MISSING
        value = self.get(key, missing)
        if value is missing:
            value = loader()
            self.put(key, value, ttl_seconds)
        return value

    def delete(self, key) -> bool:
        with self._lock:
            entry = self._index.pop(key, None)
            if entry is None:
                return False
            self._unlink(entry)
            return True

    def clear(self) -> None:
        with self._lock:
            self._index = {}
            self._head.next = self._tail
            self._tail.prev = self._head

    def purge_expired(self) -> int:
        """Removes every expired entry; returns how many. O(n)."""
        removed = 0
        with self._lock:
            entry = self._head.next
            while entry is not self._tail:
                following = entry.next
                if self._expired(entry):
                    self._unlink(entry)
                    del self._index[entry.key]
                    removed += 1
                entry = following
        return removed

    def keys(self):
        """Keys from the most to the least recently used (expired ones included until purged)."""
        with self._lock:
            out = []
            entry = self._head.next
            while entry is not self._tail:
                out = out + [entry.key]
                entry = entry.next
            return out

    def __len__(self) -> int:
        return len(self._index)

    def __contains__(self, key) -> bool:
        with self._lock:
            entry = self._index.get(key)
            return entry is not None and not self._expired(entry)

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "size": len(self._index),
            "capacity": self._capacity,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
        }


_MISSING = object()
