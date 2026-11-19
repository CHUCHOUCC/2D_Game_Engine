from .linked_list import LinkedList
from .queue import Queue
from .stack import Stack


class TreeNode:
    """A node of a general tree: a value and any number of children (kept in our own linked list)."""

    def __init__(self, value):
        self.value = value
        self.children = LinkedList()

    def add_child(self, value) -> "TreeNode":
        """Create a child holding value, add it after the existing ones and return it."""
        child = TreeNode(value)
        self.children.add(child)
        return child


class Tree:
    """General tree with a single root.

    Both traversals are iterative on purpose: preorder uses our Stack (depth first)
    and level_order uses our Queue (breadth first), so a deep tree can never hit
    Python's recursion limit.
    Invariant: every node except the root has exactly one parent.
    Costs: preorder, level_order, size, height and find visit each node once: O(n).
    """

    def __init__(self, root_value):
        self.root = TreeNode(root_value)

    def preorder(self):
        """Values parent first, then each child's subtree from the first child to the last."""
        pending = Stack()
        pending.push(self.root)
        while not pending.is_empty():
            node = pending.pop()
            yield node.value
            # The Stack returns the last pushed first, so push the children in reverse
            # (through a second stack) to visit them from the first to the last.
            reverse = Stack()
            for child in node.children:
                reverse.push(child)
            while not reverse.is_empty():
                pending.push(reverse.pop())

    def level_order(self):
        """Values level by level, from the root downwards."""
        pending = Queue()
        pending.enqueue(self.root)
        while not pending.is_empty():
            node = pending.dequeue()
            yield node.value
            for child in node.children:
                pending.enqueue(child)

    def size(self) -> int:
        return sum(1 for _ in self.level_order())

    def height(self) -> int:
        """Number of edges of the longest path from the root to a leaf (a lone root is 0)."""
        deepest = 0
        pending = Queue()
        pending.enqueue((self.root, 0))
        while not pending.is_empty():
            node, depth = pending.dequeue()
            deepest = max(deepest, depth)
            for child in node.children:
                pending.enqueue((child, depth + 1))
        return deepest

    def find(self, predicate):
        """The first value (in preorder) that satisfies the condition, or None."""
        for value in self.preorder():
            if predicate(value):
                return value
        return None
