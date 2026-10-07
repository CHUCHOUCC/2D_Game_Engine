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