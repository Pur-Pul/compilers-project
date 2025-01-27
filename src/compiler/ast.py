from dataclasses import dataclass
from typing import Optional
@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""

@dataclass
class Literal(Expression):
    value: int | bool

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
class IfClause(Expression):
    """AST node for an if statement"""
    condition: Expression
    then: Expression
    otherwise: Optional[Expression] = None

@dataclass
class FunctionCall(Expression):
    """AST node for a function call"""
    function: Identifier
    parameters: list[Expression]