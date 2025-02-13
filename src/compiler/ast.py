from dataclasses import dataclass, field
from typing import Optional
from compiler.tokenizer import Source, L
from compiler.types import Type, Unit
@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    location: Source
    type: Type = field(kw_only=True, default=Unit)

@dataclass
class Literal(Expression):
    value: int | bool | None

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    """AST node for a unary operation like `not A`"""
    op: str
    right: Expression

@dataclass
class VariableDeclaration(Expression):
    """AST node for defining a variable"""
    variable: Identifier
    var_type: Optional[Type] = None

@dataclass
class Conditional(Expression):
    """AST node for a conditional statement like `if A then B"""
    op: str
    condition: Expression
    first: Expression
    second: Optional[Expression] = None

@dataclass
class Block(Expression):
    """AST node for a block like { f(a); x = y; f(x) }"""
    expressions: list[Expression]
    result: Expression

@dataclass
class FunctionCall(Expression):
    """AST node for a function call"""
    function: Identifier
    parameters: list[Expression]