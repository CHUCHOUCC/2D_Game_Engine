class Node:
    """Linked node: holds a piece of data and a reference to the next node."""

    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node
