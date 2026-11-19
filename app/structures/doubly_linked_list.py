from .node import DoublyNode


class DoublyLinkedList:
    """Doubly linked list: every node knows the one before and the one after.

    Invariant: _head.previous and _tail.next are None; for every node,
    node.next.previous is node; _size counts the nodes.
    Costs: add_first, add_last, pop_first and pop_last are O(1); find and remove
    are O(n). Walking backwards (reversed) costs as little as walking forwards.
    Empty-list rule: pop_first() and pop_last() raise IndexError.
    """

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def add_last(self, data) -> None:
        node = DoublyNode(data, previous=self._tail)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def add_first(self, data) -> None:
        node = DoublyNode(data, next_node=self._head)
        if self._head is None:
            self._tail = node
        else:
            self._head.previous = node
        self._head = node
        self._size += 1

    def pop_first(self):
        if self._head is None:
            raise IndexError("pop from an empty list")
        node = self._head
        self._unlink(node)
        return node.data

    def pop_last(self):
        if self._tail is None:
            raise IndexError("pop from an empty list")
        node = self._tail
        self._unlink(node)
        return node.data

    def find(self, predicate):
        """The first element that satisfies the condition, or None."""
        current = self._head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def remove(self, predicate) -> bool:
        """Remove the first element that satisfies the condition; True if one was removed."""
        current = self._head
        while current is not None:
            if predicate(current.data):
                self._unlink(current)
                return True
            current = current.next
        return False

    def _unlink(self, node) -> None:
        """Take a node out and join its two neighbours."""
        if node.previous is None:
            self._head = node.next
        else:
            node.previous.next = node.next
        if node.next is None:
            self._tail = node.previous
        else:
            node.next.previous = node.previous
        node.previous = node.next = None
        self._size -= 1

    def clear(self) -> None:
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        current = self._head
        while current is not None:
            yield current.data
            current = current.next

    def reversed(self):
        """Elements from the tail to the head."""
        current = self._tail
        while current is not None:
            yield current.data
            current = current.previous
