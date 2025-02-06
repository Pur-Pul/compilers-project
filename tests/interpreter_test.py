from compiler.interpreter import interpret
from compiler.tokenizer import L
import compiler.ast as ast

def test_interpreter_int_addition() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, 2),
        "+",
        ast.Literal(L, 3)
    ))) == 5