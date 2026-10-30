class Node:
    """Singly linked node: a piece of data and a reference to the next node."""

    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node


class DoublyNode:
    """Doubly linked node: a piece of data and references to both neighbours."""

    def __init__(self, data, previous=None, next_node=None):
        self.data = data
        self.previous = previous
        self.next = next_node
