from abc import ABC, abstractmethod


class ExpressionError(Exception):
    """The expression is invalid: unknown operator, missing child or math error."""


class ExpressionNode(ABC):
    """Node of an expression tree. Each node type knows how to evaluate itself (polymorphism)."""

    @abstractmethod
    def evaluate(self):
        """Return the numeric value of the subtree rooted at this node."""


class NumberNode(ExpressionNode):
    """Leaf: base case of the recursion, evaluates to its own value."""

    def __init__(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ExpressionError(f"A leaf value must be numeric, not {value!r}")
        self.value = value

    def evaluate(self):
        return self.value


class OperationNode(ExpressionNode):
    """Internal node: combines the results of its two children with an operator.

    Evaluated in postorder: left child first, then right child, and finally
    the parent's operation. Traversing the whole tree visits each node once,
    so it costs O(n).
    Error rule: an unknown operator or a missing child raises ExpressionError
    with an identifiable message, before computing anything.
    """

    VALID_OPERATORS = ("+", "-", "*", "/")

    def __init__(self, operator, left=None, right=None):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self):
        if self.operator not in self.VALID_OPERATORS:
            raise ExpressionError(f"Unknown operator: '{self.operator}'")
        if self.left is None or self.right is None:
            raise ExpressionError(f"Operation '{self.operator}' needs two children")

        a = self.left.evaluate()
        b = self.right.evaluate()

        if self.operator == "+":
            return a + b
        if self.operator == "-":
            return a - b
        if self.operator == "*":
            return a * b
        if b == 0:
            raise ExpressionError("Division by zero")
        return a / b
