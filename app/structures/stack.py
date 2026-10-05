from .node import Node


class EmptyStackError(Exception):
    """Raised when reading or removing an element from an empty stack."""


class Stack:
    """LIFO stack built on linked nodes: the last element in is the first out.

    Invariant: _top is None if and only if the stack is empty.
    Costs: push, pop, peek and is_empty are O(1), because only the top node
    is touched and the chain is never traversed.
    Empty-stack rule: pop() and peek() raise EmptyStackError; callers can
    check first with is_empty().
    """

    def __init__(self):
        self._top = None

    def is_empty(self):
        return self._top is None

    def push(self, data):
        # The new node points to the previous top and becomes the new top.
        self._top = Node(data, self._top)

    def pop(self):
        if self._top is None:
            raise EmptyStackError("Cannot pop: the stack is empty")
        data = self._top.data
        self._top = self._top.next
        return data

    def peek(self):
        if self._top is None:
            raise EmptyStackError("No top element: the stack is empty")
        return self._top.data
