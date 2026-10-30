from app.structures.node import DoublyNode, Node


def test_node_points_to_the_next_one():
    second = Node("b")
    first = Node("a", second)
    assert first.next is second and second.next is None


def test_doubly_node_knows_both_neighbours():
    first = DoublyNode("a")
    second = DoublyNode("b", previous=first)
    first.next = second
    assert second.previous is first and first.previous is None and first.next is second
