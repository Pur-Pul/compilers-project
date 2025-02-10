from typing import Any
from compiler import ast
from typing import Optional, Self, Union, Callable
import copy
"""
type Function = Union[
    Callable[[int | bool], int | bool],
    Callable[[int | bool, int | bool], int | bool],
    Callable[[ast.Expression, ast.Expression, ast.Expression | None], Value],
    Callable[[ast.Expression, ast.Expression], Value],
    Callable[[], None]
]
"""
type Function = Union[
    Callable[[ast.Expression, ast.Expression, ast.Expression | None, SymTab], Value],
    Callable[[ast.Expression, ast.Expression, SymTab], Value],
    Callable[[ast.Expression, SymTab], Value],
    Callable[[], None]
]
type Value = int | bool | None | Function

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

    def call_function(self, func: str, params: list[ast.Expression | None], scope: Optional[Self] = None) -> Callable:
        if func in self.locals:
            return self.locals[func](*params, self if scope is None else scope)
        elif self.parent is not None:
            return self.parent.call_function(func, params, self if scope is None else scope)
        else:
            raise Exception(f"Function {func} not declared.")

    def initialize_top(self) -> None:
        def binary_op(op: str, sym_tab: SymTab, a: ast.Expression, b: ast.Expression) -> Value:
            operations: dict[str, Callable[[int | bool, int | bool], Value]] = {
                'or': lambda a, b: a or b,
                'and': lambda a, b: a and b,
                '==': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '<': lambda a, b: a < b,
                '<=': lambda a, b: a <= b,
                '>': lambda a, b: a > b,
                '>=': lambda a, b: a >= b,
                '+': lambda a, b: a + b,
                '-': lambda a, b: a - b,
                '*': lambda a, b: a * b,
                '/': lambda a, b: int(a / b),
                '%': lambda a, b: a % b
            }
            left = interpret(a, sym_tab)
            right = interpret(b, sym_tab)
            
            if isinstance(left, (int, bool)) and isinstance(right, (int, bool)):
                return operations[op](left, right)
            else:
                raise Exception(f"Binary operation {op} recieved incompatible type.")

        def unary_op(op: str, sym_tab: SymTab, a: ast.Expression) -> Value:
            value = interpret(a, sym_tab)
            match op:
                case 'unary_-':
                    if isinstance(value, (int, bool)):
                        return -value
                    else:
                        raise Exception(f"Unary operation {op} recieved incompatible type.")
                case 'unary_not':
                    if isinstance(value, (int, bool, type(None))):
                        return not value
                    else:
                        raise Exception(f"Unary operation {op} recieved incompatible type.")
                case _:
                    raise Exception(f"Unkown operator {op}")
            
        def while_clause(sym_tab: SymTab, condition: ast.Expression, expression: ast.Expression) -> Value:
            value: Value
            while interpret(condition, sym_tab):
                value = interpret(expression, sym_tab)
            return value

        def conditional_op(op: str, sym_tab: SymTab, condition: ast.Expression, first: ast.Expression, second: Optional[ast.Expression] = None, ) -> Value:
            match op:
                case 'if':
                    return interpret(first, sym_tab) if interpret(condition, sym_tab) else (interpret(second, sym_tab) if second is not None else None)
                case 'while':
                    return while_clause(sym_tab, condition, first)
                case _:
                    raise Exception(f"Unkown operator ${op}")

        for variable in ['or', 'and', '==', '!=', '<', '<=', '>', '>=', '+', '-', '*', '/', '%']:
            self.declare(variable)
            self.assign(variable, lambda a, b, sym_tab, var=variable: binary_op(var,sym_tab,a,b))
        for variable in ['unary_-', 'unary_not']:
            self.declare(variable)
            self.assign(variable, lambda a, sym_tab, var=variable: unary_op(var,sym_tab,a))
        for variable in ['if', 'while']:
            self.declare(variable)
            self.assign(variable, lambda condition, first, second, sym_tab, var=variable: conditional_op(var,sym_tab,condition,first,second))
        self.declare('unit')
        self.assign('unit', None)

def interpret(node: ast.Expression, sym_tab: SymTab | None = None, ) -> Value:
    if sym_tab is None:
        sym_tab = SymTab()
        sym_tab.initialize_top()
        
    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            try:
                return sym_tab.read(node.name)
            except Exception as e:
                raise Exception(f"{node.location} {e.args[0]}")

        case ast.BinaryOp():
            if node.op == '=':
                variable_value: Any = interpret(node.left, sym_tab)
                match node.left:
                    case ast.Identifier():
                        sym_tab.assign(node.left.name, interpret(node.right, sym_tab))
                    case ast.VariableDeclaration():
                        sym_tab.assign(node.left.variable.name, interpret(node.right, sym_tab))
                    case _:
                        raise Exception(f"{node.location} Can't assign to literal.")
                return None
            elif node.op == 'and':
                try:
                    if not interpret(node.left, sym_tab):
                        return False
                    return interpret(node.right, sym_tab)
                except Exception as e:
                    raise Exception(f"{node.location} {e.args[0]}")
            elif node.op == 'or':
                try:
                    if interpret(node.left, sym_tab):
                        return True
                    return interpret(node.right, sym_tab)
                except Exception as e:
                    raise Exception(f"{node.location} {e.args[0]}")
            else:
                try:
                    return sym_tab.call_function(node.op, [node.left, node.right])
                except Exception as e:
                    raise Exception(f"{node.location} {e.args[0]}")

        case ast.UnaryOp():
            try:
                return sym_tab.call_function("unary_"+node.op, [node.right])
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
            return sym_tab.call_function(node.op, [node.condition, node.first, node.second]) 

        case _:
            raise Exception(f"{node.location} Unkown expression: {node}")
