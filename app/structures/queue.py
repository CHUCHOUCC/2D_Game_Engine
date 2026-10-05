from .node import Node


class EmptyQueueError(Exception):
    """Raised when reading or removing an element from an empty queue."""


class Queue:
    """FIFO queue built on linked nodes: the first element in is the first out.

    Keeps references to the front (where elements are removed) and the rear
    (where elements are inserted).
    Invariant: _front and _rear are both None (empty queue) or both point to
    nodes of the same chain, and _rear.next is None.
    Costs: enqueue and dequeue are O(1); the chain is never traversed
    because the rear reference is kept.
    Empty-queue rule: dequeue(), front() and rear() raise EmptyQueueError;
    callers can check first with is_empty().
    """

    def __init__(self):
        self._front = None
        self._rear = None

    def is_empty(self):
        return self._front is None

    def enqueue(self, data):
        new_node = Node(data)
        if self._rear is None:
            # Empty queue: the new node is both front and rear.
            self._front = new_node
        else:
            self._rear.next = new_node
        self._rear = new_node

    def dequeue(self):
        if self._front is None:
            raise EmptyQueueError("Cannot dequeue: the queue is empty")
        data = self._front.data
        self._front = self._front.next
        if self._front is None:
            # The last element was removed: the rear must be cleared as well.
            self._rear = None
        return data

    def front(self):
        if self._front is None:
            raise EmptyQueueError("No front element: the queue is empty")
        return self._front.data

    def rear(self):
        if self._rear is None:
            raise EmptyQueueError("No rear element: the queue is empty")
        return self._rear.data
