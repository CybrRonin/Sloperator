"""Precedence tests.

Precedence is decided by the nesting of the parser's expression methods:
``term`` handles ``+`` and ``-`` and calls ``factor`` for its operands, while
``factor`` handles ``*`` and ``/``. Multiplicative operators therefore bind
tighter than additive ones. ``*`` and ``/`` sit on the *same* level and are
left-associative, so they are applied left to right rather than
multiplication first.
"""

import pytest

from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import Binary, ExprStmt, Grouping, Literal, Unary
from sloperator.runner import run_source


def only_expression(source: str):
    (statement,) = parse(tokenize(source))
    assert isinstance(statement, ExprStmt)
    return statement.expression


def evaluate(expression: str) -> str:
    result = run_source(f"hallucinate({expression})✨")
    assert result.stderr == "", result.stderr
    assert result.exit_code == 0
    return result.stdout.rstrip("\n")


@pytest.mark.parametrize(
    ("expression", "value"),
    [
        ("1 + 2 * 3", "7"),
        ("2 * 3 + 1", "7"),
        ("1 + 2 * 3 - 4", "3"),
        ("10 - 2 * 3", "4"),
    ],
)
def test_multiplication_binds_tighter_than_addition(expression: str, value: str):
    assert evaluate(expression) == value


def test_multiplication_is_the_operand_of_addition():
    expr = only_expression("1 + 2 * 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.PLUS
    assert isinstance(expr.right, Binary) and expr.right.operator.type is TokenType.STAR
    assert isinstance(expr.left, Literal) and expr.left.value == 1


def test_addition_is_the_operand_of_multiplication():
    expr = only_expression("2 * (1 + 3)✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.STAR
    assert isinstance(expr.right, Grouping)


def test_unary_minus_binds_tighter_than_multiplication():
    expr = only_expression("-2 * 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.STAR
    assert isinstance(expr.left, Unary)
    assert evaluate("-2 * 3") == "-6"


@pytest.mark.parametrize(
    ("expression", "value"),
    [
        # Left to right: (8 / 2) * 4. Multiplication-first would give 8 / (2 * 4) == 1.
        ("8 / 2 * 4", "16"),
        # Left to right: (2 * 8) / 4. Right grouping would give 2 * (8 / 4) == 4.
        ("2 * 8 / 4", "4"),
        ("12 / 2 / 3", "2"),
        ("2 * 3 * 4", "24"),
    ],
)
def test_multiplication_and_division_share_a_level_left_to_right(expression: str, value: str):
    assert evaluate(expression) == value


def test_division_then_multiplication_builds_a_left_leaning_tree():
    expr = only_expression("8 / 2 * 4✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.STAR
    assert isinstance(expr.left, Binary) and expr.left.operator.type is TokenType.SLASH
    assert isinstance(expr.right, Literal) and expr.right.value == 4


def test_arithmetic_binds_tighter_than_comparison():
    expr = only_expression("1 + 2 * 3 < 8✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.LESS
    assert evaluate("1 + 2 * 3 < 8") == "✅"
