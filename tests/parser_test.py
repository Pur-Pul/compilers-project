import pytest
from compiler.parser import parse
from compiler.tokenizer import Token, Source, L
import compiler.ast as ast

def test_parse_one_identifier() -> None:
    tokens = [Token("first", "identifier", L)]
    assert(parse(tokens)) == ast.Identifier("first")

def test_parse_multiple_identifiers_fails() -> None:
    tokens = [Token("first", "identifier", Source("filename",5,5)),Token("second", "identifier", Source("filename",5,11))]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == 'filename:5:11: garbage at end of expression.'

def test_parse_one_int_literal() -> None:
    tokens = [Token("1", "int_literal", L)]
    assert(parse(tokens)) == ast.Literal(1)

def test_parse_multiple_literals_fails() -> None:
    tokens = [Token("1", "int_literal", Source("filename",5,5)),Token("2", "int_literal", Source("filename",5,7))]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == 'filename:5:7: garbage at end of expression.'

def test_parse_addition_operation() -> None:
    tokens = [Token("1", "int_literal", L),Token("+", "operation", L),Token("2", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"+",ast.Literal(2))

def test_parse_subtraction_operation() -> None:
    tokens = [Token("1", "int_literal", L),Token("-", "operation", L),Token("2", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"-",ast.Literal(2))

def test_parse_multiplication_operation() -> None:
    tokens = [Token("1", "int_literal", L),Token("*", "operation", L),Token("2", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"*",ast.Literal(2))

def test_parse_division_operation() -> None:
    tokens = [Token("1", "int_literal", L),Token("/", "operation", L),Token("2", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"/",ast.Literal(2))

def test_nested_operation_is_left_associative() -> None:
    tokens = [Token("1", "int_literal", L),Token("+", "operation", L),Token("2", "int_literal", L),Token("-", "operation", L),Token("3", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.BinaryOp(ast.Literal(1),"+",ast.Literal(2)),"-",ast.Literal(3))

def test_in_nested_operation_multiplication_and_division_has_presedence_over_addition_and_subtraction() -> None:
    tokens = [Token("1", "int_literal", L),Token("+", "operation", L),Token("2", "int_literal", L),Token("*", "operation", L),Token("3", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"+",ast.BinaryOp(ast.Literal(2),"*",ast.Literal(3)),)
    tokens = [Token("1", "int_literal", L),Token("+", "operation", L),Token("2", "int_literal", L),Token("/", "operation", L),Token("3", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"+",ast.BinaryOp(ast.Literal(2),"/",ast.Literal(3)),)
    tokens = [Token("1", "int_literal", L),Token("-", "operation", L),Token("2", "int_literal", L),Token("*", "operation", L),Token("3", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"-",ast.BinaryOp(ast.Literal(2),"*",ast.Literal(3)),)
    tokens = [Token("1", "int_literal", L),Token("-", "operation", L),Token("2", "int_literal", L),Token("/", "operation", L),Token("3", "int_literal", L)]
    assert(parse(tokens)) == ast.BinaryOp(ast.Literal(1),"-",ast.BinaryOp(ast.Literal(2),"/",ast.Literal(3)),)

def test_empty_tokens_fails_gracefully() -> None:
    with pytest.raises(Exception) as e:
        parse([])
    assert(e.value.args[0]) == ':0:0: expected "(", an integer literal or an identifier'

def test_if_identifier_then_identifier() -> None:
    tokens = [Token("if", "identifier", L), Token("something", "identifier", L), Token("then", "identifier", L), Token("somethingElse", "identifier", L)]
    assert(parse(tokens)) == ast.IfClause(ast.Identifier("something"),ast.Identifier("somethingElse"))

def test_if_identifier_then_identifier_else_identifier() -> None:
    tokens = [Token("if", "identifier", L), Token("something", "identifier", L), Token("then", "identifier", L), Token("somethingElse", "identifier", L), Token("else", "identifier", L), Token("somethingThird", "identifier", L)]
    assert(parse(tokens)) == ast.IfClause(ast.Identifier("something"),ast.Identifier("somethingElse"),ast.Identifier("somethingThird"))

def test_if_else_nested() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("something", "identifier", L),
        Token("then", "identifier", L),
            Token("if", "identifier", L),
            Token("somethingElse", "identifier", L),
            Token("then", "identifier", L),
            Token("do", "identifier", L),
            Token("else", "identifier", L),
            Token("doNot", "identifier", L),
        Token("else", "identifier", L),
        Token("dosomething", "identifier", L)
    ]
    assert(parse(tokens)) == ast.IfClause(
        ast.Identifier("something"),
        ast.IfClause(
            ast.Identifier("somethingElse"),
            ast.Identifier("do"),
            ast.Identifier("doNot"),
        ),
        ast.Identifier("dosomething")
    )

def test_if_else_nested_with_operations() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("5", "int_literal", L),
        Token("-", "operator", L),
        Token("4", "int_literal", L),

        Token("then", "identifier", L),
            Token("if", "identifier", L),
            Token("a", "identifier", L),
            Token("+", "operator", L),
            Token("b", "identifier", L),

            Token("then", "identifier", L),
            Token("1", "int_literal", L),
            Token("+", "operator", L),
            Token("2", "int_literal", L),

            Token("else", "identifier", L),
            Token("5", "int_literal", L),
            Token("*", "operator", L),
            Token("3", "int_literal", L),

        Token("else", "identifier", L),
            Token("if", "identifier", L),
            Token("d", "identifier", L),
            Token("*", "operator", L),
            Token("c", "identifier", L),

            Token("then", "identifier", L),
            Token("6", "int_literal", L),
            Token("-", "operator", L),
            Token("10", "int_literal", L),

            Token("else", "identifier", L),
            Token("8", "int_literal", L),
            Token("/", "operator", L),
            Token("4", "int_literal", L),
    ]
    assert(parse(tokens)) == ast.IfClause(
        ast.BinaryOp(
            ast.Literal(5),
            '-',
            ast.Literal(4)
        ),
        ast.IfClause(
            ast.BinaryOp(
                ast.Identifier('a'),
                '+',
                ast.Identifier('b')
            ),
            ast.BinaryOp(
                ast.Literal(1),
                '+',
                ast.Literal(2)
            ),
            ast.BinaryOp(
                ast.Literal(5),
                '*',
                ast.Literal(3)
            ),
        ),
        ast.IfClause(
            ast.BinaryOp(
                ast.Identifier('d'),
                '*',
                ast.Identifier('c')
            ),
            ast.BinaryOp(
                ast.Literal(6),
                '-',
                ast.Literal(10)
            ),
            ast.BinaryOp(
                ast.Literal(8),
                '/',
                ast.Literal(4)
            ),
        ),
    )
def test_if_else_in_operation() -> None:
    tokens = [
        Token("1", "int_literal", L),
        Token("+", "operator", L),
        Token("if", "identifier", L),
        Token("5", "int_literal", L),
        Token("-", "operator", L),
        Token("4", "int_literal", L),
        Token("then", "identifier", L),
            Token("1", "int_literal", L),
        Token("else", "identfier", L),
            Token("2", "int_literal", L)
    ]
    assert(parse(tokens)) == ast.BinaryOp(
        ast.Literal(1),
        '+',
        ast.IfClause(
            ast.BinaryOp(
                ast.Literal(5),
                '-',
                ast.Literal(4),
            ),
            ast.Literal(1),
            ast.Literal(2)
        )
        
    )

def test_if_with_missing_else_fails_gracefully() -> None:
    tokens = [
        Token("if", "identifier", L),
        Token("something", "identifier", L),
        Token("then", "identifier", L),
        Token("1", "int_literal", L),
        Token("else", "identifier", L),
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: expected "(", an integer literal or an identifier'

    tokens = [
        Token("if", "identifier", L),
        Token("something", "identifier", L),
        Token("then", "identifier", L),
        Token("1", "int_literal", L),
        Token("2", "int_literal", L),
    ]
    with pytest.raises(Exception) as e:
        parse(tokens)
    assert(e.value.args[0]) == ':0:0: garbage at end of expression.'

def test_function_with_identifier() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [ast.Identifier('a')]
    )

def test_function_with_two_identifiers() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("b", "identifier", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.Identifier('a'),
            ast.Identifier('b')
        ]
    )

def test_function_with_ten_identifiers() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("b", "identifier", L),
        Token(",", "punctuation", L),
        Token("c", "identifier", L),
        Token(",", "punctuation", L),
        Token("d", "identifier", L),
        Token(",", "punctuation", L),
        Token("e", "identifier", L),
        Token(",", "punctuation", L),
        Token("f", "identifier", L),
        Token(",", "punctuation", L),
        Token("g", "identifier", L),
        Token(",", "punctuation", L),
        Token("h", "identifier", L),
        Token(",", "punctuation", L),
        Token("i", "identifier", L),
        Token(",", "punctuation", L),
        Token("j", "identifier", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.Identifier('a'),
            ast.Identifier('b'),
            ast.Identifier('c'),
            ast.Identifier('d'),
            ast.Identifier('e'),
            ast.Identifier('f'),
            ast.Identifier('g'),
            ast.Identifier('h'),
            ast.Identifier('i'),
            ast.Identifier('j'),
        ]
    )

def test_function_with_identifier_and_operation() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("1", "int_literal", L),
        Token("+", "operator", L),
        Token("2", "int_literal", L),
        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.Identifier('a'),
            ast.BinaryOp(
                ast.Literal(1),
                "+",
                ast.Literal(2)
            )
        ]
    )

def test_function_with_nested_functions() -> None:
    tokens = [
        Token("f", "identifier", L),
        Token("(", "punctuation", L),

        Token("g", "identifier", L),
        Token("(", "punctuation", L),
        Token("1", "int_literal", L),
        Token(",", "punctuation", L),
        Token("2", "int_literal", L),
        Token(")", "punctuation", L),

        Token(",", "punctuation", L),

        Token("h", "identifier", L),
        Token("(", "punctuation", L),
        Token("a", "identifier", L),
        Token(",", "punctuation", L),
        Token("b", "identifier", L),
        Token(")", "punctuation", L),

        Token(")", "punctuation", L)
    ]
    assert(parse(tokens)) == ast.FunctionCall(
        ast.Identifier('f'),
        [
            ast.FunctionCall(
                ast.Identifier('g'),
                [
                    ast.Literal(1),
                    ast.Literal(2)
                ]
            ),
            ast.FunctionCall(
                ast.Identifier('h'),
                [
                    ast.Identifier('a'),
                    ast.Identifier('b')
                ]
            )
        ]
    )