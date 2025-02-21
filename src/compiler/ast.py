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
class Break(Expression):
    def __str__ (self) -> str:
        return "break"

@dataclass
class Continue(Expression):
    def __str__ (self) -> str:
        return "continue"

@dataclass
class Literal(Expression):
    value: int | bool | None
    def __str__ (self) -> str:
        return str(self.value)

@dataclass
class Identifier(Expression):
    name: str
    def __str__ (self) -> str:
        return self.name

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression
    def __str__ (self) -> str:
        return f"{str(self.left)} {self.op} {self.right}"

@dataclass
class UnaryOp(Expression):
    """AST node for a unary operation like `not A`"""
    op: str
    right: Expression
    def __str__ (self) -> str:
        return f"{self.op} {self.right}"

@dataclass
class VariableDeclaration(Expression):
    """AST node for defining a variable"""
    variable: Identifier
    var_type: Optional[Type] = None
    def __str__ (self) -> str:
        return f"var {self.variable} : {self.var_type if self.var_type is not None else "Any"}"

@dataclass
class Conditional(Expression):
    """AST node for a conditional statement like `if A then B"""
    op: str
    condition: Expression
    first: Expression
    second: Optional[Expression] = None
    def __str__ (self) -> str:
        return f"{self.op} {self.condition} {self.first} {self.second if self.second is not None else ""}"

@dataclass
class Block(Expression):
    """AST node for a block like { f(a); x = y; f(x) }"""
    expressions: list[Expression]
    result: Expression
    def __str__ (self) -> str:
        block = ""
        for expression in self.expressions:
            block += str(expression) + "; "
        return f"{"{"} {block}{self.result} {"}"}"

@dataclass
class FunctionCall(Expression):
    """AST node for a function call"""
    function: Identifier
    parameters: list[Expression]
    
    def __str__ (self) -> str:
        params = []
        for param in self.parameters:
            params.append(str(param))
        return f"{self.function} ({params})"