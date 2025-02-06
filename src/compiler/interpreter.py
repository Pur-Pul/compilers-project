from typing import Any
from compiler import ast

type Value = int | bool | None

def interpret(node: ast.Expression) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
            if node.op == '+':
                return a + b
            elif node.op == '<':
                return a < b
            else:
                raise Exception()

        case ast.Conditional():
            if interpret(node.condition):
                return interpret(node.first)
            elif node.second is not None:
                return interpret(node.second)

    return None
