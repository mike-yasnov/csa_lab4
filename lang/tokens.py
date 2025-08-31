"""Token definitions for the Alg-like language syntax."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    """Типы токенов."""
    
    # Литералы
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Ключевые слова
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    VAR = auto()
    CONST = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    # Операторы
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    POWER = auto()          # **
    
    # Операторы сравнения
    EQUAL = auto()          # ==
    NOT_EQUAL = auto()      # !=
    LESS = auto()           # <
    LESS_EQUAL = auto()     # <=
    GREATER = auto()        # >
    GREATER_EQUAL = auto()  # >=
    
    # Логические операторы
    AND = auto()            # &&
    OR = auto()             # ||
    NOT = auto()            # !
    
    # Операторы присваивания
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    
    # Скобки и разделители
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    DOT = auto()            # .
    
    # Векторные операторы
    VECTOR_OPEN = auto()    # <|
    VECTOR_CLOSE = auto()   # |>
    
    # Встроенные функции
    PRINT = auto()
    READ = auto()
    READ_INT = auto()
    LEN = auto()
    
    # Системные токены
    EOF = auto()
    NEWLINE = auto()
    
    # Специальные токены для портов
    PORT = auto()


@dataclass
class Token:
    """Класс для представления токена."""
    
    type: TokenType
    value: Any = None
    line: int = 1
    column: int = 1
    
    def __repr__(self) -> str:
        if self.value is not None:
            return f"Token({self.type.name}, {self.value!r})"
        return f"Token({self.type.name})"


# Ключевые слова
KEYWORDS = {
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'function': TokenType.FUNCTION,
    'fun': TokenType.FUNCTION,  # Короткий синоним
    'return': TokenType.RETURN,
    'var': TokenType.VAR,
    'let': TokenType.VAR,       # Синоним
    'const': TokenType.CONST,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'print': TokenType.PRINT,
    'read': TokenType.READ,
    'readInt': TokenType.READ_INT,
    'len': TokenType.LEN,
    'port': TokenType.PORT,
}


# Двухсимвольные операторы
TWO_CHAR_OPERATORS = {
    '==': TokenType.EQUAL,
    '!=': TokenType.NOT_EQUAL,
    '<=': TokenType.LESS_EQUAL,
    '>=': TokenType.GREATER_EQUAL,
    '&&': TokenType.AND,
    '||': TokenType.OR,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '**': TokenType.POWER,
    '<|': TokenType.VECTOR_OPEN,
    '|>': TokenType.VECTOR_CLOSE,
}


# Односимвольные операторы
SINGLE_CHAR_OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '<': TokenType.LESS,
    '>': TokenType.GREATER,
    '!': TokenType.NOT,
    '=': TokenType.ASSIGN,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ';': TokenType.SEMICOLON,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
}