from app.structures.node import Node

class LinkedList:
    """Singly linked list with head and tail references: add and add_first are O(1), find and remove O(n)."""

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def add(self, data):
        new_node = Node(data)

        if self._head is None:
            self._head = new_node
            self._tail = new_node

        else:
            self._tail.next = new_node
            self._tail = new_node

        self._size += 1

    def size(self):
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def add_first(self, data):
        """Add an element at the start."""
        self._head = Node(data, self._head)
        if self._tail is None:
            self._tail = self._head
        self._size += 1

    def clear(self):
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def find(self, predicate):
        current = self._head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next

        return None
      


    def remove(self, predicate):
        previous = None
        current = self._head
        while current is not None:
            if predicate(current.data) == True:
                if previous is None:
                    self._head = current.next
                else:
                    previous.next = current.next

                if current is self._tail:
                    self._tail = previous
                self._size -= 1
                return True
            previous = current
            current = current.next

        return False


    def __iter__(self):
        current = self._head
        while current is not None:
            yield current.data
            current = current.next


