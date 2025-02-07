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
    sym_tab.define("a")
    assert(interpret(ast.BinaryOp(L,
        ast.Identifier(L, "a"),
        "=",
        ast.Literal(L, 5)
    ), sym_tab)) == None
    assert(sym_tab.read("a")) == 5

def test_interpreter_variable_updates_visible_to_interpreter() -> None:
    sym_tab = SymTab()
    sym_tab.define("a")
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
