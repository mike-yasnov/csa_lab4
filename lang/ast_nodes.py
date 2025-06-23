"""Узлы абстрактного синтаксического дерева (AST) для алголичного языка."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union
from dataclasses import dataclass


class ASTNode(ABC):
    """Базовый класс для всех узлов AST."""
    
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Паттерн посетитель для обхода AST."""
        pass


class Expression(ASTNode):
    """Базовый класс для выражений."""
    pass


class Statement(ASTNode):
    """Базовый класс для операторов."""
    pass


# Выражения
@dataclass
class NumberLiteral(Expression):
    """Числовой литерал."""
    value: Union[int, float]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_number_literal(self)


@dataclass
class StringLiteral(Expression):
    """Строковый литерал."""
    value: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_string_literal(self)


@dataclass
class BooleanLiteral(Expression):
    """Булев литерал."""
    value: bool
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_boolean_literal(self)


@dataclass
class NullLiteral(Expression):
    """Null литерал."""
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_null_literal(self)


@dataclass
class Identifier(Expression):
    """Идентификатор переменной."""
    name: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_identifier(self)


@dataclass
class BinaryOperation(Expression):
    """Бинарная операция."""
    left: Expression
    operator: str
    right: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_binary_operation(self)


@dataclass
class UnaryOperation(Expression):
    """Унарная операция."""
    operator: str
    operand: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_unary_operation(self)


@dataclass
class FunctionCall(Expression):
    """Вызов функции."""
    name: str
    arguments: List[Expression]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_call(self)


@dataclass
class VectorLiteral(Expression):
    """Векторный литерал <| 1, 2, 3, 4 |>."""
    elements: List[Expression]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_vector_literal(self)


@dataclass
class ArrayAccess(Expression):
    """Доступ к элементу массива."""
    array: Expression
    index: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_array_access(self)


# Операторы
@dataclass
class ExpressionStatement(Statement):
    """Выражение как оператор."""
    expression: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_expression_statement(self)


@dataclass
class VarDeclaration(Statement):
    """Объявление переменной."""
    name: str
    initializer: Optional[Expression] = None
    is_const: bool = False
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_var_declaration(self)


@dataclass
class Assignment(Statement):
    """Присваивание."""
    target: Identifier
    value: Expression
    operator: str = "="  # =, +=, -=
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_assignment(self)


@dataclass
class Block(Statement):
    """Блок операторов."""
    statements: List[Statement]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_block(self)


@dataclass
class IfStatement(Statement):
    """Условный оператор."""
    condition: Expression
    then_stmt: Statement
    else_stmt: Optional[Statement] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    """Цикл while."""
    condition: Expression
    body: Statement
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_while_statement(self)


@dataclass
class ForStatement(Statement):
    """Цикл for."""
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Expression]
    body: Statement
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_for_statement(self)


@dataclass
class FunctionDeclaration(Statement):
    """Объявление функции."""
    name: str
    parameters: List[str]
    body: Block
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_declaration(self)


@dataclass
class ReturnStatement(Statement):
    """Оператор возврата."""
    value: Optional[Expression] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_return_statement(self)


@dataclass
class Program(ASTNode):
    """Корневой узел программы."""
    statements: List[Statement]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_program(self)


# Абстрактный класс посетителя
class ASTVisitor(ABC):
    """Интерфейс посетителя для обхода AST."""
    
    @abstractmethod
    def visit_number_literal(self, node: NumberLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_string_literal(self, node: StringLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_boolean_literal(self, node: BooleanLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_null_literal(self, node: NullLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass
    
    @abstractmethod
    def visit_vector_literal(self, node: VectorLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_array_access(self, node: ArrayAccess) -> Any:
        pass
    
    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_var_declaration(self, node: VarDeclaration) -> Any:
        pass
    
    @abstractmethod
    def visit_assignment(self, node: Assignment) -> Any:
        pass
    
    @abstractmethod
    def visit_block(self, node: Block) -> Any:
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        pass
    
    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        pass
    
    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass 