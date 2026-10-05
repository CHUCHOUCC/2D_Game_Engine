import pytest

from app.domain import Event, ScoreCounter
from app.structures import EmptyQueueError, Queue


def test_new_queue_is_empty():
    assert Queue().is_empty()


def test_fifo_first_in_is_first_out():
    queue = Queue()
    for item in (1, 2, 3):
        queue.enqueue(item)
    assert queue.front() == 1
    assert queue.rear() == 3
    assert [queue.dequeue() for _ in range(3)] == [1, 2, 3]


def test_events_come_out_in_order_and_score_ends_at_15():
    queue = Queue()
    incoming = [Event("coin", "A"), Event("coin", "B"), Event("damage")]
    for event in incoming:
        queue.enqueue(event)

    counter = ScoreCounter()
    outgoing = []
    while not queue.is_empty():
        event = queue.dequeue()
        outgoing.append(event)
        counter.apply(event)

    assert outgoing == incoming
    assert counter.score == 15


def test_after_removing_the_last_element_front_and_rear_are_empty():
    queue = Queue()
    queue.enqueue("only")
    assert queue.dequeue() == "only"
    assert queue.is_empty()
    with pytest.raises(EmptyQueueError):
        queue.front()
    with pytest.raises(EmptyQueueError):
        queue.rear()


def test_enqueue_again_after_emptying_works():
    queue = Queue()
    queue.enqueue("a")
    queue.dequeue()
    queue.enqueue("b")
    assert queue.front() == "b"
    assert queue.rear() == "b"
    assert queue.dequeue() == "b"


def test_dequeue_on_empty_queue_follows_an_explicit_rule():
    with pytest.raises(EmptyQueueError):
        Queue().dequeue()
