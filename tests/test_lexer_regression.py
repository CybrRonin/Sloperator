"""Regression tests for lexical error paths that were not otherwise covered."""

import pytest

from sloperator.errors import LexicalError
from sloperator.lexer import tokenize


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("a ? b", "unexpected character '?'"),
        ("a ' b", "unexpected character '''"),
        ("a @ b", "unexpected character '@'"),
    ],
    ids=["question-mark", "single-quote", "at-sign"],
)
def test_unexpected_character_reports_the_offending_character(source: str, message: str):
    with pytest.raises(LexicalError) as info:
        tokenize(source)
    assert info.value.line == 1
    assert info.value.message == message


def test_backslash_before_newline_is_an_unknown_escape():
    with pytest.raises(LexicalError) as info:
        tokenize("hallucinate(“abc\\\ndef”)✨")
    assert info.value.line == 1
    assert info.value.message == "unknown escape sequence '\\\n'"
