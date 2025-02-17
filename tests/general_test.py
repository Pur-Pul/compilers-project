from compiler.ir_generator import generate_ir
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.ir import IRVar
from compiler.types import Int, Type, Unit

def test_1() -> None:
    tokens = tokenize("1 + 2 * 3")
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('print_int') : Unit
    }
    ir = generate_ir(root_types, expr)
    for instruction in ir:
        print(instruction)

test_1()