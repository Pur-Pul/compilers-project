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
            Token
        Token("else", "identifier", L),
        Token("somethingThird", "identifier", L)]