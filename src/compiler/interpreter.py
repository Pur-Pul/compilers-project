from typing import Any
from compiler import ast
from typing import Optional, Self
from collections.abc import Callable
type Value = int | bool | None | Callable

class SymTab:
    parent : Optional[Self] = None
    locals: dict
    def __init__(self, parent: Optional[Self] = None):
        self.parent = parent
        self.locals = {}

    def declare(self, variable: str) -> None:
        self.locals[variable] = None

    def assign(self, variable: str, value: Value) -> None:
        if variable in self.locals:
            self.locals[variable] = value
        elif self.parent is not None:
            self.parent.assign(variable, value)
        else:
            raise Exception(f"Variable {variable} not declared.")

    def read(self, variable: str) -> Value:
        if variable in self.locals:
            return self.locals[variable]
        elif self.parent is not None:
            return self.parent.read(variable)
        else:
            raise Exception(f"Variable {variable} not declared.")
    
    def function(self, func: str) -> Callable:
        if func in self.locals:
            return self.locals[func]
        elif self.parent is not None:
            return self.parent.function(func)
        else:
            raise Exception(f"Function {func} not declared.")
    

def add(a: int, b:int) -> int:
    return a + b 
def sub(a: int, b:int) -> int:
    return a - b
def mult(a:int, b:int) -> int:
    return a * b
def div(a:int, b:int) -> int:
    return int(a / b)
def mod(a:int, b:int) -> int:
    return a % b
def unary_negate(a:int) -> int:
    return -a
def unary_not(a:bool) -> bool:
    return not a
def bool_and(a:bool, b:bool) -> bool:
    return a and b
def bool_or(a:bool, b:bool) -> bool:
    return a or b
def bool_equal(a:Value, b:Value) -> bool:
    return a == b
def bool_not_equal(a:Value, b:Value) -> bool:
    return a != b
def bool_smaller(a:int, b:int) -> bool:
    return a < b
def bool_smaller_equal(a:int, b:int) -> bool:
    return a <= b
def bool_larger(a:int, b:int) -> bool:
    return a > b
def bool_larger_equal(a:int, b:int) -> bool:
    return a >= b
"""
def if_clause(condition: Value, first: Value, second: Optional[Value] = None) -> Value:
    return first if condition else second
"""

def interpret(node: ast.Expression, sym_tab: SymTab | None = None) -> Value:
    binary_operators = {
        'or': bool_or,
        'and': bool_and,
        '==': bool_equal,
        '!=': bool_not_equal,
        '<': bool_smaller,
        '<=': bool_smaller_equal,
        '>': bool_larger,
        '>=': bool_larger_equal,
        '+': add,
        '-': sub,
        '*': mult,
        '/': div,
        '%': mod
    }
    unary_operators = {
        '-': unary_negate,
        'not': unary_not
    }
    """
    conditionals = {
        'if': if_clause,
        'while': while_clause
    }
    """
    if sym_tab is None:
        sym_tab = SymTab()
        function: Callable
        for operator, function in binary_operators.items():
            sym_tab.declare(operator)
            sym_tab.assign(operator, function)

        for operator, function in unary_operators.items():
            sym_tab.declare("unary_"+operator)
            sym_tab.assign("unary_"+operator, function)

    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            try:
                return sym_tab.read(node.name)
            except Exception as e:
                raise Exception(f"{node.location} "+e.args[0])

        case ast.BinaryOp():
            a: Any = interpret(node.left, sym_tab)
            b: Any = interpret(node.right, sym_tab)
            if node.op == '=':
                match node.left:
                    case ast.Identifier():
                        sym_tab.assign(node.left.name, b)
                    case ast.VariableDeclaration():
                        sym_tab.assign(node.left.variable.name, b)
                    case _:
                        raise Exception(f"{node.location} Can't assign to literal.")
                return None
            else:
                try:
                    return sym_tab.function(node.op)(a, b)
                except Exception as e:
                    raise Exception(f"{node.location} {e.args[0]}")

        case ast.UnaryOp():
            value: Any = interpret(node.right, sym_tab)
            try:
                return sym_tab.function("unary_"+node.op)(value)
            except Exception as e:
                raise Exception(f"{node.location} {e.args[0]}")

        case ast.VariableDeclaration():
            sym_tab.declare(node.variable.name)
            return None

        case ast.Block():
            for expression in node.expressions:
                interpret(expression, sym_tab)
            return interpret(node.result, sym_tab)

        case ast.Conditional():
            if interpret(node.condition, sym_tab):
                return interpret(node.first, sym_tab)
            elif node.second is not None:
                return interpret(node.second, sym_tab)
            return None

        case _:
            raise Exception(f"{node.location} Unkown expression: {node}")

