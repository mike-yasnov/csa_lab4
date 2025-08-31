"""Синтаксический анализатор для алголичного языка."""

from typing import List

from .tokens import Token, TokenType
from .ast_nodes import (
    Program,
    Statement,
    FunctionDeclaration,
    VarDeclaration,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    Block,
    Identifier,
    Assignment,
    ExpressionStatement,
    Expression,
    BinaryOperation,
    UnaryOperation,
    ArrayAccess,
    FunctionCall,
    BooleanLiteral,
    NullLiteral,
    NumberLiteral,
    StringLiteral,
    VectorLiteral,
)


class ParseError(Exception):
    """Ошибка синтаксического анализа."""
    
    def __init__(self, message: str, token: Token) -> None:
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")


class Parser:
    """Рекурсивно-нисходящий парсер."""
    
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        # Убираем переводы строк, так как они нам не нужны для парсинга
        self.tokens = [t for t in self.tokens if t.type != TokenType.NEWLINE]
    
    def current_token(self) -> Token:
        """Получить текущий токен."""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF токен
        return self.tokens[self.current]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Посмотреть на токен с заданным смещением."""
        pos = self.current + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF токен
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Продвинуться к следующему токену и вернуть текущий."""
        token = self.current_token()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def match(self, *types: TokenType) -> bool:
        """Проверить, соответствует ли текущий токен одному из типов."""
        return self.current_token().type in types
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        """Потребить токен заданного типа или выбросить ошибку."""
        if self.current_token().type == token_type:
            return self.advance()
        
        raise ParseError(message, self.current_token())
    
    def parse(self) -> Program:
        """Главная функция парсинга."""
        statements = []
        
        while not self.match(TokenType.EOF):
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def declaration(self) -> Statement | None:
        """Объявление (функция или переменная)."""
        try:
            if self.match(TokenType.FUNCTION):
                return self.function_declaration()
            if self.match(TokenType.VAR, TokenType.CONST):
                return self.var_declaration()
            
            return self.statement()
        except ParseError:
            # Синхронизация при ошибке
            self.synchronize()
            raise
    
    def function_declaration(self) -> FunctionDeclaration:
        """Объявление функции."""
        self.consume(TokenType.FUNCTION, "Ожидался 'function'")
        name_token = self.consume(TokenType.IDENTIFIER, "Ожидалось имя функции")
        
        self.consume(TokenType.LPAREN, "Ожидалась '('")
        
        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Ожидалось имя параметра").value)
            while self.match(TokenType.COMMA):
                self.advance()  # consume comma
                parameters.append(self.consume(TokenType.IDENTIFIER, "Ожидалось имя параметра").value)
        
        self.consume(TokenType.RPAREN, "Ожидалась ')'")
        
        body = self.block_statement()
        
        return FunctionDeclaration(name_token.value, parameters, body)
    
    def var_declaration(self) -> VarDeclaration:
        """Объявление переменной."""
        is_const = self.match(TokenType.CONST)
        self.advance()  # consume var/const
        
        name_token = self.consume(TokenType.IDENTIFIER, "Ожидалось имя переменной")
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()  # consume =
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Ожидалась ';'")
        
        return VarDeclaration(name_token.value, initializer, is_const)
    
    def statement(self) -> Statement:
        """Оператор."""
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.LBRACE):
            return self.block_statement()
        
        return self.expression_statement()
    
    def if_statement(self) -> IfStatement:
        """Условный оператор."""
        self.consume(TokenType.IF, "Ожидался 'if'")
        self.consume(TokenType.LPAREN, "Ожидалась '('")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Ожидалась ')'")
        
        then_stmt = self.statement()
        
        else_stmt = None
        if self.match(TokenType.ELSE):
            self.advance()  # consume else
            else_stmt = self.statement()
        
        return IfStatement(condition, then_stmt, else_stmt)
    
    def while_statement(self) -> WhileStatement:
        """Цикл while."""
        self.consume(TokenType.WHILE, "Ожидался 'while'")
        self.consume(TokenType.LPAREN, "Ожидалась '('")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Ожидалась ')'")
        
        body = self.statement()
        
        return WhileStatement(condition, body)
    
    def for_statement(self) -> ForStatement:
        """Цикл for."""
        self.consume(TokenType.FOR, "Ожидался 'for'")
        self.consume(TokenType.LPAREN, "Ожидалась '('")
        
        # Инициализация
        init = None
        if self.match(TokenType.SEMICOLON):
            self.advance()
        elif self.match(TokenType.VAR):
            init = self.var_declaration()
        else:
            init = self.expression_statement()
        
        # Условие
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Ожидалась ';'")
        
        # Обновление
        update = None
        if not self.match(TokenType.RPAREN):
            update = self.expression()
        self.consume(TokenType.RPAREN, "Ожидалась ')'")
        
        body = self.statement()
        
        return ForStatement(init, condition, update, body)
    
    def return_statement(self) -> ReturnStatement:
        """Оператор возврата."""
        self.consume(TokenType.RETURN, "Ожидался 'return'")
        
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Ожидалась ';'")
        
        return ReturnStatement(value)
    
    def block_statement(self) -> Block:
        """Блок операторов."""
        self.consume(TokenType.LBRACE, "Ожидалась '{'")
        
        statements = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        
        self.consume(TokenType.RBRACE, "Ожидалась '}'")
        
        return Block(statements)
    
    def expression_statement(self) -> Statement:
        """Выражение как оператор."""
        # Проверяем на присваивание
        if (self.match(TokenType.IDENTIFIER) and
            self.peek_token().type in (TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN)):
            
            target = Identifier(self.advance().value)
            operator = self.advance().value
            value = self.expression()
            self.consume(TokenType.SEMICOLON, "Ожидалась ';'")
            
            return Assignment(target, value, operator)
        
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Ожидалась ';'")
        
        return ExpressionStatement(expr)
    
    def expression(self) -> Expression:
        """Выражение."""
        return self.logical_or()
    
    def logical_or(self) -> Expression:
        """Логическое ИЛИ."""
        expr = self.logical_and()
        
        while self.match(TokenType.OR):
            operator = self.advance().value
            right = self.logical_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def logical_and(self) -> Expression:
        """Логическое И."""
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.advance().value
            right = self.equality()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def equality(self) -> Expression:
        """Равенство."""
        expr = self.comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.advance().value
            right = self.comparison()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expression:
        """Сравнение."""
        expr = self.term()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                          TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.advance().value
            right = self.term()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def term(self) -> Expression:
        """Сложение и вычитание."""
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().value
            right = self.factor()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def factor(self) -> Expression:
        """Умножение, деление, возведение в степень."""
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.POWER):
            operator = self.advance().value
            right = self.unary()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expression:
        """Унарные операции."""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.advance().value
            expr = self.unary()
            return UnaryOperation(operator, expr)
        
        return self.call()
    
    def call(self) -> Expression:
        """Вызов функции и доступ к элементам."""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.LBRACKET):
                self.advance()  # consume [
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Ожидалась ']'")
                expr = ArrayAccess(expr, index)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: Expression) -> FunctionCall:
        """Завершить разбор вызова функции."""
        self.advance()  # consume (
        
        arguments = []
        if not self.match(TokenType.RPAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                self.advance()  # consume comma
                arguments.append(self.expression())
        
        self.consume(TokenType.RPAREN, "Ожидалась ')'")
        
        if isinstance(callee, Identifier):
            return FunctionCall(callee.name, arguments)
        else:
            raise ParseError("Можно вызывать только функции", self.current_token())
    
    def primary(self) -> Expression:
        """Первичные выражения."""
        if self.match(TokenType.TRUE):
            self.advance()
            return BooleanLiteral(value=True)
        
        if self.match(TokenType.FALSE):
            self.advance()
            return BooleanLiteral(value=False)
        
        if self.match(TokenType.NULL):
            self.advance()
            return NullLiteral()
        
        if self.match(TokenType.NUMBER):
            return NumberLiteral(self.advance().value)
        
        if self.match(TokenType.STRING):
            return StringLiteral(self.advance().value)
        
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.advance().value)
        
        if self.match(TokenType.LPAREN):
            self.advance()  # consume (
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Ожидалась ')'")
            return expr
        
        # Векторный литерал
        if self.match(TokenType.VECTOR_OPEN):
            self.advance()  # consume <|
            
            elements = []
            if not self.match(TokenType.VECTOR_CLOSE):
                elements.append(self.expression())
                while self.match(TokenType.COMMA):
                    self.advance()  # consume comma
                    elements.append(self.expression())
            
            self.consume(TokenType.VECTOR_CLOSE, "Ожидалась '|>'")
            return VectorLiteral(elements)
        
        # Встроенные функции
        if self.match(TokenType.PRINT, TokenType.READ, TokenType.READ_INT, TokenType.LEN):
            name = self.advance().value
            self.consume(TokenType.LPAREN, "Ожидалась '('")
            
            arguments = []
            if not self.match(TokenType.RPAREN):
                arguments.append(self.expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.expression())
            
            self.consume(TokenType.RPAREN, "Ожидалась ')'")
            return FunctionCall(name, arguments)
        
        raise ParseError(f"Неожиданный токен: {self.current_token().type}", self.current_token())
    
    def synchronize(self) -> None:
        """Синхронизация после ошибки."""
        self.advance()
        
        while not self.match(TokenType.EOF):
            if self.tokens[self.current - 1].type == TokenType.SEMICOLON:
                return
            
            if self.current_token().type in (
                TokenType.FUNCTION, TokenType.VAR, TokenType.FOR,
                TokenType.IF, TokenType.WHILE, TokenType.RETURN,
            ):
                return
            
            self.advance()


def parse(tokens: List[Token]) -> Program:
    """Удобная функция для парсинга."""
    parser = Parser(tokens)
    return parser.parse()