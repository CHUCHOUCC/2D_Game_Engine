import pytest

from app.structures import EmptyStackError, Stack


def test_new_stack_is_empty():
    assert Stack().is_empty()


def test_lifo_last_in_is_first_out():
    stack = Stack()
    for item in (1, 2, 3):
        stack.push(item)
    assert [stack.pop() for _ in range(3)] == [3, 2, 1]
    assert stack.is_empty()


def test_peek_does_not_remove_the_element():
    stack = Stack()
    stack.push("a")
    assert stack.peek() == "a"
    assert not stack.is_empty()


def test_undo_two_moves_with_positions():
    # A tuple (immutable copy) of the previous position is saved before moving.
    position = (0, 0)
    history = Stack()

    history.push(position)
    position = (5, 0)
    history.push(position)
    position = (5, 4)

    position = history.pop()
    assert position == (5, 0)
    position = history.pop()
    assert position == (0, 0)


def test_pop_on_empty_stack_follows_an_explicit_rule_and_stack_stays_usable():
    stack = Stack()
    with pytest.raises(EmptyStackError):
        stack.pop()
    with pytest.raises(EmptyStackError):
        stack.peek()
    stack.push(1)
    assert stack.pop() == 1
