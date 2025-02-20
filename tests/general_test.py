from compiler.ir_generator import generate_ir
from compiler.tokenizer import tokenize
from compiler.parser import parse
from compiler.type_checker import typecheck
from compiler.ir import IRVar
from compiler.types import Int, Type, Unit, Bool
from compiler.assembly_generator import generate_assembly

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

def test_2() -> None:
    tokens = tokenize("if 1 == 1 then 2 else 3")
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('==') : Bool,
        IRVar('print_int') : Unit
    }
    ir = generate_ir(root_types, expr)
    for instruction in ir:
        print(instruction)

def test_3() -> None:
    tokens = tokenize("if true and false then 2 else 3")
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('and') : Bool,
        IRVar('or') : Bool,
        IRVar('==') : Bool,
        IRVar('print_int') : Unit
    }
    ir = generate_ir(root_types, expr)
    for instruction in ir:
        print(instruction)

def test_4() -> None:
    tokens = tokenize("""
        var a = 5;
        var b = 4;
        var c = -a * b;
        print_int(c)
    """)
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('unary_-') : Int,
        IRVar('and') : Bool,
        IRVar('or') : Bool,
        IRVar('==') : Bool,
        IRVar('print_int') : Unit
    }
    ir = generate_ir(root_types, expr)
    for instruction in ir:
        print(instruction)

def test_5() -> None:
    tokens = tokenize("""{ var x = true; if x then 1 else 2; }""")
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('unary_-') : Int,
        IRVar('and') : Bool,
        IRVar('or') : Bool,
        IRVar('==') : Bool,
        IRVar('print_int') : Unit
    }
    ir = generate_ir(root_types, expr)
    print(generate_assembly(ir))
    #for instruction in ir:
    #    print(instruction)

def test_6() -> None:
    tokens = tokenize("""
        var x = 5 + 6;
        if x == 11 then x = x * 1 else x = x / 2;
    """)
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('unary_-') : Int,
        IRVar('and') : Bool,
        IRVar('or') : Bool,
        IRVar('==') : Bool,
        IRVar('/') : Bool,
        IRVar('print_int') : Unit
    }
    ir = generate_ir(root_types, expr)
    print(generate_assembly(ir))

def test_7() -> None:
    tokens = tokenize("""
        f(1,2,3,4,5,6,7,8)
    """)
    expr = parse(tokens)
    typecheck(expr)
    root_types: dict[IRVar, Type] = {
        IRVar('+') : Int,
        IRVar('*') : Int,
        IRVar('unary_-') : Int,
        IRVar('and') : Bool,
        IRVar('or') : Bool,
        IRVar('==') : Bool,
        IRVar('/') : Bool,
        IRVar('print_int') : Unit,
        IRVar('f') : Unit
    }
    ir = generate_ir(root_types, expr)
    print(generate_assembly(ir))
test_7()