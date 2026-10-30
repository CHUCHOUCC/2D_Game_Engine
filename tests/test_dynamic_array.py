import pytest

from app.structures.dynamic_array import DynamicArray


def build(*values):
    array = DynamicArray(2)
    for value in values:
        array.append(value)
    return array


def test_it_keeps_the_values_when_it_grows():
    array = build(*range(10))
    assert list(array) == list(range(10))
    assert array.size() == 10 and array.capacity() >= 10


def test_the_capacity_doubles_when_full():
    array = DynamicArray(2)
    array.append(1)
    array.append(2)
    assert array.capacity() == 2
    array.append(3)
    assert array.capacity() == 4


def test_get_and_set_by_index_and_negative_index():
    array = build("a", "b", "c")
    array[1] = "B"
    assert (array[0], array[1], array[-1]) == ("a", "B", "c")


def test_reading_outside_the_bounds_raises():
    array = build(1)
    for index in (1, -2, 99):
        with pytest.raises(IndexError):
            array.get(index)
    with pytest.raises(IndexError):
        array.set(5, 0)


def test_insert_shifts_the_elements_to_the_right():
    array = build(1, 3)
    array.insert(1, 2)
    array.insert(0, 0)
    array.insert(4, 4)
    assert list(array) == [0, 1, 2, 3, 4]


def test_insert_outside_the_bounds_raises():
    with pytest.raises(IndexError):
        build(1).insert(3, 0)


def test_remove_at_closes_the_gap():
    array = build(1, 2, 3, 4)
    assert array.remove_at(1) == 2
    assert list(array) == [1, 3, 4]


def test_pop_takes_the_last_one_and_an_empty_array_raises():
    array = build(1, 2)
    assert array.pop() == 2 and array.size() == 1
    array.pop()
    with pytest.raises(IndexError):
        array.pop()


def test_filled_makes_independent_slots():
    array = DynamicArray.filled(5, False)
    array[2] = True
    assert list(array) == [False, False, True, False, False]


def test_clear_empties_it_and_it_can_be_reused():
    array = build(1, 2, 3)
    array.clear()
    assert array.is_empty()
    array.append(9)
    assert list(array) == [9]


def test_the_capacity_must_be_positive():
    with pytest.raises(ValueError):
        DynamicArray(0)
