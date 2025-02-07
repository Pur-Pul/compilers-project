from typing import Any
from compiler import ast
from typing import Optional
type Value = int | bool | None

class SymTab:
    parent : Optional['SymTab'] = None
    locals: dict
    def __init__(self, parent: Optional['SymTab'] = None):
        self.parent = parent
        self.locals = {}
    def define(self, variable: str) -> None:
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

def interpret(node: ast.Expression, sym_tab: SymTab = SymTab()) -> Value:
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
            if node.op == '+':
                return a + b
            elif node.op == '<':
                return a < b
            elif node.op == '=':
                match node.left:
                    case ast.Identifier():
                        sym_tab.assign(node.left.name, b)
                    case ast.VariableDeclaration():
                        sym_tab.assign(node.left.variable.name, b)
                    case _:
                        raise Exception(f"{node.location} Can't assign to literal.")
                return None
            else:
                raise Exception(f"{node.location} Unkown operator: {node.op}")

        case ast.VariableDeclaration():
            sym_tab.define(node.variable.name)
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

