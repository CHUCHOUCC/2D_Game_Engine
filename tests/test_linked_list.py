from app.structures.linked_list import LinkedList


def test_new_list_is_empty():
    items = LinkedList()
    assert items.is_empty() is True
    assert items.size() == 0


def test_add_increases_size():
    items = LinkedList()
    items.add("a")
    items.add("b")
    assert items.size() == 2
    assert items.is_empty() is False


def test_add_keeps_insertion_order():
    items = LinkedList()
    for value in ("a", "b", "c"):
        items.add(value)
    assert items._head.data == "a"
    assert items._head.next.data == "b"
    assert items._tail.data == "c"


def test_single_element_is_head_and_tail():
    items = LinkedList()
    items.add("a")
    assert items._head is items._tail

def build(*items):
    numbers = LinkedList()
    for item in items:
        numbers.add(item)
    return numbers


def test_find_returns_the_first_matching_item():
    numbers = build(1, 2, 3, 4)
    assert numbers.find(lambda x: x > 2) == 3


def test_find_returns_none_when_nothing_matches_or_list_is_empty():
    assert build(1, 2).find(lambda x: x == 9) is None
    assert LinkedList().find(lambda x: True) is None


def test_remove_head():
    numbers = build(1, 2, 3)
    assert numbers.remove(lambda x: x == 1) is True
    assert list(numbers) == [2, 3]
    assert numbers.size() == 2


def test_remove_middle():
    numbers = build(1, 2, 3)
    assert numbers.remove(lambda x: x == 2) is True
    assert list(numbers) == [1, 3]


def test_remove_tail_and_keep_adding():
    numbers = build(1, 2, 3)
    assert numbers.remove(lambda x: x == 3) is True
    numbers.add(4)
    assert list(numbers) == [1, 2, 4]


def test_remove_the_only_item_leaves_a_usable_empty_list():
    numbers = build(1)
    assert numbers.remove(lambda x: x == 1) is True
    assert numbers.is_empty()
    numbers.add(7)
    assert list(numbers) == [7]


def test_remove_returns_false_when_nothing_matches():
    numbers = build(1, 2)
    assert numbers.remove(lambda x: x == 9) is False
    assert numbers.size() == 2


def test_iteration_follows_insertion_order():
    assert list(build("a", "b", "c")) == ["a", "b", "c"]