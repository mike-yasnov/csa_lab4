"""AST nodes for the Alg-like language."""

from abc import ABC, abstractmethod
from typing import Any, List
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
    """Numeric literal."""
    value: int | float
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_number_literal(self)


@dataclass
class StringLiteral(Expression):
    """String literal."""
    value: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_string_literal(self)


@dataclass
class BooleanLiteral(Expression):
    """Boolean literal."""
    value: bool
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_boolean_literal(self)


@dataclass
class NullLiteral(Expression):
    """Null literal."""
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_null_literal(self)


@dataclass
class Identifier(Expression):
    """Variable identifier."""
    name: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_identifier(self)


@dataclass
class BinaryOperation(Expression):
    """Binary operation."""
    left: Expression
    operator: str
    right: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_binary_operation(self)


@dataclass
class UnaryOperation(Expression):
    """Unary operation."""
    operator: str
    operand: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_unary_operation(self)


@dataclass
class FunctionCall(Expression):
    """Function call."""
    name: str
    arguments: List[Expression]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_call(self)


@dataclass
class VectorLiteral(Expression):
    """Vector literal like <| 1, 2, 3, 4 |>."""
    elements: List[Expression]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_vector_literal(self)


@dataclass
class ArrayAccess(Expression):
    """Array element access."""
    array: Expression
    index: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_array_access(self)


# Операторы
@dataclass
class ExpressionStatement(Statement):
    """Expression used as a statement."""
    expression: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_expression_statement(self)


@dataclass
class VarDeclaration(Statement):
    """Variable declaration."""
    name: str
    initializer: Expression | None = None
    is_const: bool = False
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_var_declaration(self)


@dataclass
class Assignment(Statement):
    """Assignment."""
    target: Identifier
    value: Expression
    operator: str = "="  # =, +=, -=
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_assignment(self)


@dataclass
class Block(Statement):
    """Block of statements."""
    statements: List[Statement]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_block(self)


@dataclass
class IfStatement(Statement):
    """If statement."""
    condition: Expression
    then_stmt: Statement
    else_stmt: Statement | None = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    """While loop."""
    condition: Expression
    body: Statement
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_while_statement(self)


@dataclass
class ForStatement(Statement):
    """For loop."""
    init: Statement | None
    condition: Expression | None
    update: Expression | None
    body: Statement
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_for_statement(self)


@dataclass
class FunctionDeclaration(Statement):
    """Function declaration."""
    name: str
    parameters: List[str]
    body: Block
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_declaration(self)


@dataclass
class ReturnStatement(Statement):
    """Return statement."""
    value: Expression | None = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_return_statement(self)


@dataclass
class Program(ASTNode):
    """Program root node."""
    statements: List[Statement]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_program(self)


# Абстрактный класс посетителя
class ASTVisitor(ABC):
    """Visitor interface to traverse AST."""
    
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