import pytest

from app.structures.doubly_linked_list import DoublyLinkedList


def build(*values):
    items = DoublyLinkedList()
    for value in values:
        items.add_last(value)
    return items


def test_it_walks_forwards_and_backwards():
    items = build(1, 2, 3)
    assert list(items) == [1, 2, 3]
    assert list(items.reversed()) == [3, 2, 1]


def test_add_first_and_add_last():
    items = build(2)
    items.add_first(1)
    items.add_last(3)
    assert list(items) == [1, 2, 3] and list(items.reversed()) == [3, 2, 1]


def test_pop_first_and_pop_last():
    items = build(1, 2, 3)
    assert (items.pop_first(), items.pop_last()) == (1, 3)
    assert list(items) == [2] and items.size() == 1


def test_popping_the_only_element_empties_both_ends():
    items = build(1)
    items.pop_last()
    assert items.is_empty()
    items.add_last(2)
    assert list(items) == [2] and list(items.reversed()) == [2]


def test_popping_an_empty_list_raises():
    items = DoublyLinkedList()
    with pytest.raises(IndexError):
        items.pop_first()
    with pytest.raises(IndexError):
        items.pop_last()


def test_remove_keeps_both_directions_consistent():
    items = build(1, 2, 3, 4)
    assert items.remove(lambda n: n == 2)
    assert items.remove(lambda n: n == 4)
    assert list(items) == [1, 3] and list(items.reversed()) == [3, 1]


def test_find_and_a_failed_remove():
    items = build(1, 2, 3)
    assert items.find(lambda n: n == 3) == 3
    assert items.find(lambda n: n == 9) is None
    assert not items.remove(lambda n: n == 9)
