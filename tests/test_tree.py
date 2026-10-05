import pytest

from app.structures import ExpressionError, NumberNode, OperationNode


def test_2_plus_3_times_4_is_20():
    total = OperationNode("+", NumberNode(2), NumberNode(3))
    tree = OperationNode("*", total, NumberNode(4))
    assert tree.evaluate() == 20


def test_leaf_with_7_evaluates_to_7():
    assert NumberNode(7).evaluate() == 7


def test_unknown_operator_is_rejected_with_an_identifiable_message():
    tree = OperationNode("^", NumberNode(2), NumberNode(3))
    with pytest.raises(ExpressionError, match="Unknown operator"):
        tree.evaluate()


def test_operation_without_required_children_is_rejected():
    tree = OperationNode("+", NumberNode(2), None)
    with pytest.raises(ExpressionError, match="needs two children"):
        tree.evaluate()


def test_error_in_a_subtree_propagates_upwards():
    inner = OperationNode("?", NumberNode(1), NumberNode(1))
    tree = OperationNode("+", inner, NumberNode(5))
    with pytest.raises(ExpressionError, match="Unknown operator"):
        tree.evaluate()


def test_division_by_zero_is_rejected():
    tree = OperationNode("/", NumberNode(4), NumberNode(0))
    with pytest.raises(ExpressionError, match="Division by zero"):
        tree.evaluate()


def test_leaf_with_text_is_rejected():
    with pytest.raises(ExpressionError):
        NumberNode("7")
