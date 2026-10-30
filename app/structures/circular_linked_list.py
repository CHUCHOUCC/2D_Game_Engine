from .node import Node


class CircularLinkedList:
    """Circular list: the last node points back to the first one.

    Only the tail is kept; the head is always _tail.next. A cursor remembers the
    element that comes next, so advance() can go round and round forever.
    Invariant: empty means _tail is None; otherwise _tail.next is the head and
    following _size links from the head comes back to it.
    Costs: add and advance are O(1); remove is O(n).
    Empty-list rule: advance() and current() raise IndexError.
    """

    def __init__(self):
        self._tail = None
        self._cursor = None
        self._size = 0

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def add(self, data) -> None:
        """Add an element at the end of the lap (just before the head)."""
        node = Node(data)
        if self._tail is None:
            node.next = node
            self._cursor = node
        else:
            node.next = self._tail.next
            self._tail.next = node
        self._tail = node
        self._size += 1

    def current(self):
        """The element the cursor is on, without moving it."""
        if self._cursor is None:
            raise IndexError("the list is empty")
        return self._cursor.data

    def advance(self):
        """Move the cursor to the next element (going back to the first after the last) and return it."""
        if self._cursor is None:
            raise IndexError("the list is empty")
        self._cursor = self._cursor.next
        return self._cursor.data

    def remove(self, predicate) -> bool:
        """Remove the first element (from the head) that satisfies the condition."""
        if self._tail is None:
            return False
        previous = self._tail
        current = self._tail.next
        for _ in range(self._size):
            if predicate(current.data):
                if self._size == 1:
                    self._tail = None
                    self._cursor = None
                else:
                    previous.next = current.next
                    if current is self._tail:
                        self._tail = previous
                    if current is self._cursor:
                        self._cursor = current.next
                self._size -= 1
                return True
            previous = current
            current = current.next
        return False

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        """One lap, from the head to the tail."""
        if self._tail is None:
            return
        current = self._tail.next
        for _ in range(self._size):
            yield current.data
            current = current.next
