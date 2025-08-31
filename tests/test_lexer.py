"""Тесты для лексического анализатора."""

import pytest
from lang.lexer import tokenize, LexerError
from lang.tokens import TokenType

# Constants to avoid magic numbers in assertions
EXPECTED_INT = 123
EXPECTED_FLOAT = 45.67
EXPECTED_TOKENS_AFTER_COMMENTS = 11


def test_numbers() -> None:
    """Тест разбора чисел."""
    tokens = tokenize("123 45.67 0")
    
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == EXPECTED_INT
    
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].value == EXPECTED_FLOAT
    
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 0


def test_strings() -> None:
    """Тест разбора строк."""
    tokens = tokenize('"hello" "world with spaces"')
    
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "hello"
    
    assert tokens[1].type == TokenType.STRING
    assert tokens[1].value == "world with spaces"


def test_identifiers() -> None:
    """Тест разбора идентификаторов."""
    tokens = tokenize("variable_name myVar test123")
    
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "variable_name"
    
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "myVar"
    
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].value == "test123"


def test_keywords() -> None:
    """Тест разбора ключевых слов."""
    tokens = tokenize("if else while for function var const")
    
    assert tokens[0].type == TokenType.IF
    assert tokens[1].type == TokenType.ELSE
    assert tokens[2].type == TokenType.WHILE
    assert tokens[3].type == TokenType.FOR
    assert tokens[4].type == TokenType.FUNCTION
    assert tokens[5].type == TokenType.VAR
    assert tokens[6].type == TokenType.CONST


def test_operators() -> None:
    """Тест разбора операторов."""
    tokens = tokenize("+ - * / % == != < <= > >=")
    
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
        TokenType.MODULO, TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS,
        TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
    ]
    
    for i, expected_type in enumerate(expected_types):
        assert tokens[i].type == expected_type


def test_vector_literals() -> None:
    """Тест разбора векторных литералов."""
    tokens = tokenize("<| 1, 2, 3 |>")
    
    assert tokens[0].type == TokenType.VECTOR_OPEN
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[2].type == TokenType.COMMA
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[4].type == TokenType.COMMA
    assert tokens[5].type == TokenType.NUMBER
    assert tokens[6].type == TokenType.VECTOR_CLOSE


def test_comments() -> None:
    """Тест обработки комментариев."""
    tokens = tokenize("var x = 5; // это комментарий\nvar y = 10;")
    
    # Комментарии должны игнорироваться
    assert len(tokens) == EXPECTED_TOKENS_AFTER_COMMENTS  # var x = 5 ; var y = 10 ;  EOF
    assert tokens[0].type == TokenType.VAR
    assert tokens[5].type == TokenType.VAR


def test_error_handling() -> None:
    """Тест обработки ошибок."""
    with pytest.raises(LexerError):
        tokenize('"незакрытая строка')
    
    with pytest.raises(LexerError):
        tokenize("@#$%")  # invalid symbols