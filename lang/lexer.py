"""Lexer for the Alg-like language syntax."""

from typing import List, Optional

from .tokens import Token, TokenType, KEYWORDS, TWO_CHAR_OPERATORS, SINGLE_CHAR_OPERATORS


class LexerError(Exception):
    """Ошибка лексического анализа."""
    
    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class Lexer:
    """Лексический анализатор."""
    
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> str | None:
        """Получить текущий символ."""
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def peek_char(self, offset: int = 1) -> str | None:
        """Посмотреть на символ с заданным смещением."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def advance(self) -> None:
        """Продвинуться к следующему символу."""
        if self.pos < len(self.text):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self) -> None:
        """Пропустить пробельные символы кроме переводов строки."""
        current = self.current_char()
        while current and current in ' \t\r':
            self.advance()
            current = self.current_char()
    
    def skip_comment(self) -> None:
        """Пропустить комментарий до конца строки."""
        while self.current_char() and self.current_char() != '\n':
            self.advance()
    
    def read_number(self) -> Token:
        """Прочитать число."""
        start_line, start_column = self.line, self.column
        result = ''
        
        # Читаем цифры
        current = self.current_char()
        while current and current.isdigit():
            result += current
            self.advance()
            current = self.current_char()
        
        # Проверяем на десятичную точку
        next_char = self.peek_char()
        if current == '.' and next_char and next_char.isdigit():
            result += current
            self.advance()
            
            current = self.current_char()
            while current and current.isdigit():
                result += current
                self.advance()
                current = self.current_char()
            
            return Token(TokenType.NUMBER, float(result), start_line, start_column)
        
        return Token(TokenType.NUMBER, int(result), start_line, start_column)
    
    def read_string(self) -> Token:
        """Прочитать строку в кавычках."""
        start_line, start_column = self.line, self.column
        quote_char = self.current_char()  # " или '
        self.advance()  # Пропускаем открывающую кавычку
        
        result = ''
        current = self.current_char()
        while current and current != quote_char:
            if current == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    result += '\n'
                elif escape_char == 't':
                    result += '\t'
                elif escape_char == 'r':
                    result += '\r'
                elif escape_char == '\\':
                    result += '\\'
                elif escape_char == quote_char:
                    result += quote_char
                elif escape_char == '0':
                    result += '\0'
                elif escape_char is not None:
                    result += escape_char
                self.advance()
            else:
                result += current
                self.advance()
            current = self.current_char()
        
        if not current:
            raise LexerError("Unterminated string", start_line, start_column)
        
        self.advance()  # Пропускаем закрывающую кавычку
        return Token(TokenType.STRING, result, start_line, start_column)
    
    def read_identifier(self) -> Token:
        """Прочитать идентификатор или ключевое слово."""
        start_line, start_column = self.line, self.column
        result = ''
        
        # Первый символ - буква или _
        current = self.current_char()
        if current and (current.isalpha() or current == '_'):
            result += current
            self.advance()
        
        # Остальные символы - буквы, цифры или _
        current = self.current_char()
        while current and (current.isalnum() or current == '_'):
            result += current
            self.advance()
            current = self.current_char()
        
        # Проверяем, является ли идентификатор ключевым словом
        token_type = KEYWORDS.get(result, TokenType.IDENTIFIER)
        
        if token_type in (TokenType.TRUE, TokenType.FALSE):
            value = result == 'true'
            return Token(token_type, value, start_line, start_column)
        elif token_type == TokenType.NULL:
            return Token(token_type, None, start_line, start_column)
        else:
            return Token(token_type, result, start_line, start_column)
    
    def read_operator(self) -> Token:
        """Прочитать оператор."""
        start_line, start_column = self.line, self.column
        
        # Проверяем двухсимвольные операторы
        current = self.current_char()
        next_char = self.peek_char()
        if current and next_char:
            two_char = current + next_char
            if two_char in TWO_CHAR_OPERATORS:
                self.advance()
                self.advance()
                return Token(TWO_CHAR_OPERATORS[two_char], two_char, start_line, start_column)
        
        # Проверяем односимвольные операторы
        if current and current in SINGLE_CHAR_OPERATORS:
            self.advance()
            return Token(SINGLE_CHAR_OPERATORS[current], current, start_line, start_column)
        
        raise LexerError(f"Unknown symbol: {current!r}", start_line, start_column)
    
    def tokenize(self) -> List[Token]:
        """Выполнить лексический анализ и вернуть список токенов."""
        self.tokens = []
        
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            current = self.current_char()
            if not current:
                break
            
            # Перевод строки
            if current == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, current, self.line, self.column))
                self.advance()
            
            # Комментарии
            elif current == '/' and self.peek_char() == '/':
                self.skip_comment()
            
            # Числа
            elif current.isdigit():
                self.tokens.append(self.read_number())
            
            # Строки
            elif current in ('"', "'"):
                self.tokens.append(self.read_string())
            
            # Идентификаторы и ключевые слова
            elif current.isalpha() or current == '_':
                self.tokens.append(self.read_identifier())
            
            # Операторы и разделители
            else:
                self.tokens.append(self.read_operator())
        
        # Добавляем токен конца файла
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(text: str) -> List[Token]:
    """Helper function to tokenize text."""
    lexer = Lexer(text)
    return lexer.tokenize()