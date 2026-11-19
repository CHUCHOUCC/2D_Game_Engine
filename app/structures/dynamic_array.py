import ctypes


class DynamicArray:
    """Array that grows: a fixed block of memory that is replaced by a bigger one when it fills up.

    The block is a ctypes array of Python objects, so it has a fixed length and
    knows nothing about append or pop: growing, shifting and bounds are all done here.
    Invariant: 0 <= _size <= _capacity; slots from _size on are unused (None).
    Costs: get and set by index are O(1); append is O(1) amortised because the
    capacity doubles; insert and remove_at are O(n) because elements are shifted.
    Bounds rule: an index outside 0.._size-1 raises IndexError (negative indexes count from the end).
    """

    def __init__(self, capacity: int = 4):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._size = 0
        self._block = self._new_block(capacity)

    @classmethod
    def filled(cls, count: int, value) -> "DynamicArray":
        """An array with `count` copies of value."""
        array = cls(max(1, count))
        for _ in range(count):
            array.append(value)
        return array

    @staticmethod
    def _new_block(capacity: int):
        block = (ctypes.py_object * capacity)()
        for slot in range(capacity):
            block[slot] = None
        return block

    def capacity(self) -> int:
        return self._capacity

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def _checked(self, index: int) -> int:
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        return index

    def _grow(self) -> None:
        bigger = self._new_block(self._capacity * 2)
        for slot in range(self._size):
            bigger[slot] = self._block[slot]
        self._block = bigger
        self._capacity *= 2

    def get(self, index: int):
        return self._block[self._checked(index)]

    def set(self, index: int, value) -> None:
        self._block[self._checked(index)] = value

    def append(self, value) -> None:
        if self._size == self._capacity:
            self._grow()
        self._block[self._size] = value
        self._size += 1

    def insert(self, index: int, value) -> None:
        """Put value at index, shifting the elements after it one place to the right."""
        if not 0 <= index <= self._size:
            raise IndexError("index out of range")
        if self._size == self._capacity:
            self._grow()
        for slot in range(self._size, index, -1):
            self._block[slot] = self._block[slot - 1]
        self._block[index] = value
        self._size += 1

    def remove_at(self, index: int):
        """Remove and return the element at index, closing the gap."""
        index = self._checked(index)
        value = self._block[index]
        for slot in range(index, self._size - 1):
            self._block[slot] = self._block[slot + 1]
        self._size -= 1
        self._block[self._size] = None
        return value

    def pop(self):
        """Remove and return the last element."""
        return self.remove_at(self._size - 1)

    def clear(self) -> None:
        for slot in range(self._size):
            self._block[slot] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int):
        return self.get(index)

    def __setitem__(self, index: int, value) -> None:
        self.set(index, value)

    def __iter__(self):
        for slot in range(self._size):
            yield self._block[slot]
