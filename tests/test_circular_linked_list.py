import pytest

from app.structures.circular_linked_list import CircularLinkedList


def build(*values):
    ring = CircularLinkedList()
    for value in values:
        ring.add(value)
    return ring


def test_one_lap_keeps_the_order_of_insertion():
    assert list(build(1, 2, 3)) == [1, 2, 3]


def test_advance_goes_round_and_round():
    ring = build("a", "b", "c")
    assert ring.current() == "a"
    assert [ring.advance() for _ in range(7)] == ["b", "c", "a", "b", "c", "a", "b"]


def test_a_single_element_points_to_itself():
    ring = build("only")
    assert ring.advance() == "only" and ring.advance() == "only"


def test_an_empty_ring_raises():
    ring = CircularLinkedList()
    with pytest.raises(IndexError):
        ring.advance()
    with pytest.raises(IndexError):
        ring.current()
    assert list(ring) == [] and not ring.remove(lambda _: True)


def test_adding_after_going_round_goes_to_the_end_of_the_lap():
    ring = build(1, 2)
    ring.advance()
    ring.add(3)
    assert list(ring) == [1, 2, 3]


def test_remove_the_head_the_middle_and_the_tail():
    ring = build(1, 2, 3, 4)
    assert ring.remove(lambda n: n == 1)
    assert ring.remove(lambda n: n == 3)
    assert ring.remove(lambda n: n == 4)
    assert list(ring) == [2] and ring.size() == 1


def test_removing_the_element_under_the_cursor_moves_the_cursor_on():
    ring = build(1, 2, 3)
    ring.advance()  # cursor on 2
    ring.remove(lambda n: n == 2)
    assert ring.current() == 3


def test_removing_the_last_element_leaves_an_empty_ring_that_can_be_reused():
    ring = build(1)
    assert ring.remove(lambda n: n == 1) and ring.is_empty()
    ring.add(2)
    assert ring.current() == 2 and list(ring) == [2]
