import pytest
from compiler.type_checker import typecheck, SymTab
from compiler.tokenizer import L
import compiler.ast as ast
from compiler.types import Any, Unit, Int, Bool, FunType

def test_type_checker_literal() -> None:
    assert(typecheck(ast.Literal(L, None))) == Unit
    assert(typecheck(ast.Literal(L, 0))) == Int
    assert(typecheck(ast.Literal(L, 1))) == Int
    assert(typecheck(ast.Literal(L, True))) == Bool
    assert(typecheck(ast.Literal(L, False))) == Bool

def test_type_checker_variable() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    assert(typecheck(ast.Identifier(L, 'a'), sym_tab)) == Any
    sym_tab.assign('a', Unit)
    assert(typecheck(ast.Identifier(L, 'a'), sym_tab)) == Unit
    sym_tab.assign('a', Int)
    assert(typecheck(ast.Identifier(L, 'a'), sym_tab)) == Int
    sym_tab.assign('a', Bool)
    assert(typecheck(ast.Identifier(L, 'a'), sym_tab)) == Bool
    sym_tab.assign('a', FunType([Int], Int))
    assert(typecheck(ast.Identifier(L, 'a'), sym_tab)) == FunType([Int], Int)

def test_type_checker_untyped_variable_declaration_defaults_to_any() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    assert(typecheck(ast.VariableDeclaration(L, ast.Identifier(L, 'a')), sym_tab)) == Any

def test_type_checker_assignment() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    assert(typecheck(ast.BinaryOp(L,
        ast.Identifier(L, 'a'),
        '=',
        ast.Literal(L, 2)
    ), sym_tab)) == FunType([Any, Int], Int)
    assert(sym_tab.read('a')) == Int

    sym_tab.declare('b')
    assert(typecheck(ast.BinaryOp(L,
        ast.Identifier(L, 'b'),
        '=',
        ast.Literal(L, True)
    ), sym_tab)) == FunType([Any, Bool], Bool)
    assert(sym_tab.read('b')) == Bool

    with pytest.raises(Exception) as e:
        typecheck(ast.BinaryOp(L,
            ast.Identifier(L, 'a'),
            '=',
            ast.Identifier(L, 'b'),
        ), sym_tab)
    assert(e.value.args[0]) == "Left and right of '=' are of different types. Int != Bool"
    assert(sym_tab.read('a')) == Int

def test_type_checker_assignment_of_variable_declaration() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    assert(typecheck(ast.BinaryOp(L,
        ast.VariableDeclaration(L, ast.Identifier(L, 'a')),
        '=',
        ast.Literal(L, 2)
    ), sym_tab)) == FunType([Any, Int], Int)
    assert(sym_tab.read('a')) == Int

    assert(typecheck(ast.BinaryOp(L,
        ast.VariableDeclaration(L, ast.Identifier(L, 'b')),
        '=',
        ast.Literal(L, True)
    ), sym_tab)) == FunType([Any, Bool], Bool)
    assert(sym_tab.read('b')) == Bool

    assert(typecheck(ast.BinaryOp(L,
        ast.VariableDeclaration(L, ast.Identifier(L, 'c')),
        '=',
        ast.Identifier(L, 'b'),
    ), sym_tab)) == FunType([Any, Bool], Bool)
    assert(sym_tab.read('c')) == Bool

def test_assignment_to_literal_fails_gracefully() -> None:
    with pytest.raises(Exception) as e:
        typecheck(ast.BinaryOp(L, 
            ast.Literal(L, 1),
            '=',
            ast.Literal(L, 1)
        ))
    assert(e.value.args[0]) == "Unsupported type 'Int' to the left of '='."
    
def test_type_checker_binary_operation() -> None:
    for operation in ['+','-','*','/']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Literal(L, 1),
            operation,
            ast.Literal(L, 1),
        ))) == Int
    for operation in ['<','<=','>','>=']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Literal(L, 1),
            operation,
            ast.Literal(L, 1),
        ))) == Bool
    for operation in ['and', 'or']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Literal(L, 1),
            operation,
            ast.Literal(L, 1),
        ))) == Bool
    for operation in ['==', '!=']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Literal(L, 1),
            operation,
            ast.Literal(L, 1),
        ))) == Bool
        assert(typecheck(ast.BinaryOp(L, 
            ast.Literal(L, True),
            operation,
            ast.Literal(L, True),
        ))) == Bool
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'unit'),
            operation,
            ast.Identifier(L, 'unit'),
        ))) == Bool

def test_type_checker_binary_operation_wtih_variables() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    sym_tab.assign('a', Int)
    for operation in ['+','-','*','/']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'a'),
            operation,
            ast.Identifier(L, 'a'),
        ), sym_tab)) == Int
    
    for operation in ['<','<=','>','>=']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'a'),
            operation,
            ast.Identifier(L, 'a'),
        ), sym_tab)) == Bool
    
    sym_tab.assign('a', Bool)
    for operation in ['and', 'or']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'a'),
            operation,
            ast.Identifier(L, 'a'),
        ), sym_tab)) == Bool
    
    for operation in ['==', '!=']:
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'a'),
            operation,
            ast.Identifier(L, 'a'),
        ), sym_tab)) == Bool
        sym_tab.assign('a', Int)
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'a'),
            operation,
            ast.Identifier(L, 'a'),
        ), sym_tab)) == Bool
        sym_tab.assign('a', Unit)
        assert(typecheck(ast.BinaryOp(L, 
            ast.Identifier(L, 'a'),
            operation,
            ast.Identifier(L, 'a'),
        ), sym_tab)) == Bool

def test_type_checker_unary_operation() -> None:
    assert(typecheck(ast.UnaryOp(L, 'not', ast.Literal(L, True)))) == Bool
    assert(typecheck(ast.UnaryOp(L, 'not', ast.Literal(L, False)))) == Bool
    assert(typecheck(ast.UnaryOp(L, '-', ast.Literal(L, 1)))) == Int
    assert(typecheck(ast.UnaryOp(L, '-', ast.Literal(L, -1)))) == Int

def test_type_checker_unary_operation_with_variable() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    sym_tab.assign('a', Bool)
    assert(typecheck(ast.UnaryOp(L, 'not', ast.Identifier(L, 'a')), sym_tab)) == Bool
    sym_tab.assign('a', Int)
    assert(typecheck(ast.UnaryOp(L, '-', ast.Identifier(L, 'a')), sym_tab)) == Int

def test_type_checker_function_call() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('f')
    sym_tab.assign('f', FunType([Int], Int))
    sym_tab.declare('g')
    sym_tab.assign('g', FunType([Int, Int], Int))
    assert(typecheck(ast.FunctionCall(L,
        ast.Identifier(L, 'f'),
        [ast.Literal(L, 1)]
    ), sym_tab)) == Int
    assert(typecheck(ast.FunctionCall(L,
        ast.Identifier(L, 'g'),
        [ast.Literal(L, 1), ast.Literal(L, 1)]
    ), sym_tab)) == Int

def test_type_checker_function_call_to_invalid_function_fails_gracefully() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('g')
    sym_tab.assign('g', Int)
    with pytest.raises(Exception) as e:
        typecheck(ast.FunctionCall(L,
            ast.Identifier(L, 'g'),
            [ast.Literal(L, 1)]
        ), sym_tab)
    assert(e.value.args[0]) == "Variable 'g' is not a function."

def test_type_checker_function_call_with_incorrect_number_of_arguments_fails_gracefully() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('g')
    sym_tab.assign('g', FunType([Int, Int], Int))
    with pytest.raises(Exception) as e:
        typecheck(ast.FunctionCall(L,
            ast.Identifier(L, 'g'),
            [ast.Literal(L, 1)]
        ), sym_tab)
    assert(e.value.args[0]) == "Function 'g' received incorrect number of arguments. Expected 2, but received 1."

def test_type_checker_function_call_with_incorrect_argument_type_fails_gracefully() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('f')
    sym_tab.assign('f', FunType([Int], Int))
    with pytest.raises(Exception) as e:
        typecheck(ast.FunctionCall(L,
            ast.Identifier(L, 'f'),
            [ast.Literal(L, True)]
        ), sym_tab)
    assert(e.value.args[0]) == "Function 'f' argument number 1 is incorrect type. Expected 'Int', but received 'Bool'."

def test_type_checker_block_typechecks_all_expressions() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    sym_tab.declare('b')
    assert(typecheck(ast.Block(L,
        [
            ast.BinaryOp(L,
                ast.Identifier(L, 'a'),
                '=',
                ast.Literal(L, 2)
            ),
            ast.BinaryOp(L,
                ast.Identifier(L, 'b'),
                '=',
                ast.Literal(L, True)
            ),
            ast.BinaryOp(L,
                ast.VariableDeclaration(L,ast.Identifier(L, 'c')),
                '=',
                ast.BinaryOp(L, 
                    ast.Identifier(L, 'a'),
                    '==',
                    ast.Identifier(L, 'b')
                )
            ),
        ],
        ast.Identifier(L, 'c')
    ), sym_tab)) == Bool
    assert(sym_tab.read('a')) == Int
    assert(sym_tab.read('b')) == Bool
    with pytest.raises(Exception) as e:
        sym_tab.read('c')
    assert(e.value.args[0]) == "Variable 'c' is not declared."

def test_type_checker_if_conditional() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Literal(L, 2)))) == Int
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Literal(L, True)))) == Bool
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Identifier(L, 'a')), sym_tab)) == Any
    sym_tab.assign('a', Int)
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Identifier(L, 'a')), sym_tab)) == Int

def test_type_checker_if_else_conditional() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    sym_tab.declare('b')
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Literal(L, 2), ast.Literal(L, 3)))) == Int
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, False), ast.Literal(L, 2), ast.Literal(L, 3)))) == Int

    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Literal(L, True), ast.Literal(L, False)))) == Bool
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, False), ast.Literal(L, True), ast.Literal(L, False)))) == Bool

    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Identifier(L, 'a'), ast.Identifier(L, 'b')), sym_tab)) == Any
    assert(typecheck(ast.Conditional(L, 'if', ast.Literal(L, False), ast.Identifier(L, 'a'), ast.Identifier(L, 'b')), sym_tab)) == Any
    
    sym_tab.assign('a', Int)
    with pytest.raises(Exception) as e:
        typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Identifier(L, 'a'), ast.Identifier(L, 'b')), sym_tab)
    assert(e.value.args[0]) == "Expected 'if-else' expressions to be same type, but received 'Int != Any'."

    sym_tab.assign('b', Bool)
    with pytest.raises(Exception) as e:
        typecheck(ast.Conditional(L, 'if', ast.Literal(L, True), ast.Identifier(L, 'a'), ast.Identifier(L, 'b')), sym_tab)
    assert(e.value.args[0]) == "Expected 'if-else' expressions to be same type, but received 'Int != Bool'."
    with pytest.raises(Exception) as e:
        typecheck(ast.Conditional(L, 'if', ast.Literal(L, False), ast.Identifier(L, 'a'), ast.Identifier(L, 'b')), sym_tab)
    assert(e.value.args[0]) == "Expected 'if-else' expressions to be same type, but received 'Int != Bool'."

def test_type_checker_while_conditional() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    sym_tab.declare('a')
    assert(typecheck(ast.Conditional(L, 'while', ast.Literal(L, True), ast.Literal(L, 2)))) == Unit
    assert(typecheck(ast.Conditional(L, 'while', ast.Literal(L, True), ast.Literal(L, True)))) == Unit
    assert(typecheck(ast.Conditional(L, 'while', ast.Literal(L, True), ast.Identifier(L, 'a')), sym_tab)) == Unit
    with pytest.raises(Exception) as e:
        typecheck(ast.Conditional(L, 'while', ast.Literal(L, False), ast.Literal(L, 1), ast.Literal(L, 2)))
    assert(e.value.args[0]) == "Conditional 'while' received incorrect number of arguments. Expected 2, but received 3."

def test_type_checker_typed_var_declaration() -> None:
    sym_tab = SymTab()
    sym_tab.initialize_top()
    assert(typecheck(ast.VariableDeclaration(L, ast.Identifier(L, 'a'), Int))) == Int
    assert(typecheck(ast.VariableDeclaration(L, ast.Identifier(L, 'a'), Bool))) == Bool
    assert(typecheck(ast.VariableDeclaration(L, ast.Identifier(L, 'a'), Unit))) == Unit
    assert(typecheck(ast.VariableDeclaration(L, ast.Identifier(L, 'a'), Any))) == Any
    