import pytest
from compiler.interpreter import interpret, SymTab
from compiler.tokenizer import L
import compiler.ast as ast

def test_interpreter_int_addition() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, 2),
        "+",
        ast.Literal(L, 3)
    ))) == 5

def test_interpreter_int_subtraction() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, 2),
        "-",
        ast.Literal(L, 3)
    ))) == -1

def test_interpreter_int_multiplication() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, 2),
        "*",
        ast.Literal(L, 3)
    ))) == 6

def test_interpreter_int_division() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, 3),
        "/",
        ast.Literal(L, 3)
    ))) == 1

def test_interpreter_int_modulo() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, 2),
        "%",
        ast.Literal(L, 3)
    ))) == 2

def test_interpreter_and() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, True),
        "and",
        ast.Literal(L, False)
    ))) == False
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, True),
        "and",
        ast.Literal(L, True)
    ))) == True

def test_interpreter_or() -> None:
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, True),
        "or",
        ast.Literal(L, False)
    ))) == True
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, False),
        "or",
        ast.Literal(L, True)
    ))) == True
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, False),
        "or",
        ast.Literal(L, False)
    ))) == False

def test_interpreter_equal() -> None:
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "==",
        ast.Literal(L, 2)
    ))) == True
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "==",
        ast.Literal(L, 3)
    ))) == False

def test_interpreter_not_equal() -> None:
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "!=",
        ast.Literal(L, 2)
    ))) == False
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "!=",
        ast.Literal(L, 3)
    ))) == True

def test_interpreter_smaller() -> None:
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "<",
        ast.Literal(L, 2)
    ))) == False
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 3),
        "<",
        ast.Literal(L, 2)
    ))) == False
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "<",
        ast.Literal(L, 3)
    ))) == True

def test_interpreter_smaller_equal() -> None:
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "<=",
        ast.Literal(L, 2)
    ))) == True
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 3),
        "<=",
        ast.Literal(L, 2)
    ))) == False
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        "<=",
        ast.Literal(L, 3)
    ))) == True

def test_interpreter_larger() -> None:
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        ">",
        ast.Literal(L, 2)
    ))) == False
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 3),
        ">",
        ast.Literal(L, 2)
    ))) == True
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        ">",
        ast.Literal(L, 3)
    ))) == False

def test_interpreter_larger_equal() -> None:
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        ">=",
        ast.Literal(L, 2)
    ))) == True
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 3),
        ">=",
        ast.Literal(L, 2)
    ))) == True
    assert(interpret(ast.BinaryOp(L, 
        ast.Literal(L, 2),
        ">=",
        ast.Literal(L, 3)
    ))) == False

def test_interpreter_negate() -> None:
    assert(interpret(ast.UnaryOp(L,
        '-',
        ast.Literal(L, 1)
    ))) == -1
    assert(interpret(ast.UnaryOp(L,
        '-',
        ast.Literal(L, -1)
    ))) == 1

def test_interpreter_not() -> None:
    assert(interpret(ast.UnaryOp(L,
        'not',
        ast.Literal(L, True)
    ))) == False
    assert(interpret(ast.UnaryOp(L,
        'not',
        ast.Literal(L, True)
    ))) == False

def test_interpreter_variable_declaration() -> None:
    sym_tab = SymTab()
    assert(interpret(ast.VariableDeclaration(L, ast.Identifier(L, "a")), sym_tab)) == None
    assert(sym_tab.read("a")) == None

def test_interpreter_non_declared_variable_fails_gracefully() -> None:
    with pytest.raises(Exception) as e:
        interpret(ast.Identifier(L, "a"))
    assert(e.value.args[0]) == f"{L} Variable a not declared."

def test_intepreter_assignment_updates_variable() -> None:
    sym_tab = SymTab()
    sym_tab.declare("a")
    assert(interpret(ast.BinaryOp(L,
        ast.Identifier(L, "a"),
        "=",
        ast.Literal(L, 5)
    ), sym_tab)) == None
    assert(sym_tab.read("a")) == 5

def test_interpreter_variable_updates_visible_to_interpreter() -> None:
    sym_tab = SymTab()
    sym_tab.declare("a")
    assert(interpret(ast.BinaryOp(L,
        ast.Identifier(L, "a"),
        "=",
        ast.Literal(L, 5)
    ), sym_tab)) == None
    assert(interpret(ast.Identifier(L, "a"), sym_tab)) == 5

def test_intepreter_block_executes_all_expressions() -> None:
    assert(interpret(
        ast.Block(L,
            [
                ast.BinaryOp(L,
                    ast.VariableDeclaration(L, ast.Identifier(L, "a")),
                    "=",
                    ast.BinaryOp(L,
                        ast.Literal(L, 2),
                        "+",
                        ast.Literal(L, 3)
                    )
                ),
                ast.BinaryOp(L,
                    ast.Identifier(L, "a"),
                    "=",
                    ast.BinaryOp(L,
                        ast.Identifier(L, "a"),
                        "+",
                        ast.Literal(L, 4)
                    )
                )
            ],
            ast.Identifier(L, "a")
        )
    )) == 9

def test_interprete_or_short_circuting() -> None:
    sym_tab = SymTab()
    sym_tab.declare("evaluated_right_hand_side")
    sym_tab.assign("evaluated_right_hand_side", False)
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, True),
        'or',
        ast.Block(L,
            [ast.BinaryOp(L,
                ast.Identifier(L, "evaluated_right_hand_side"),
                '=',
                ast.Literal(L, True)
            )],
            ast.Literal(L, True)
        )
    ))) == True
    assert(sym_tab.read("evaluated_right_hand_side")) == False

def test_interprete_and_short_circuting() -> None:
    sym_tab = SymTab()
    sym_tab.declare("evaluated_right_hand_side")
    sym_tab.assign("evaluated_right_hand_side", False)
    assert(interpret(ast.BinaryOp(L,
        ast.Literal(L, False),
        'and',
        ast.Block(L,
            [ast.BinaryOp(L,
                ast.Identifier(L, "evaluated_right_hand_side"),
                '=',
                ast.Literal(L, True)
            )],
            ast.Literal(L, False)
        )
    ))) == False
    assert(sym_tab.read("evaluated_right_hand_side")) == False