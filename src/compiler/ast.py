from dataclasses import dataclass
from typing import Optional
from compiler.tokenizer import Source, L
@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    location: Source

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