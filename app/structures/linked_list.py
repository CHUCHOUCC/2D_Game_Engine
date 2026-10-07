from app.structures.node import Node

class LinkedList:

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


